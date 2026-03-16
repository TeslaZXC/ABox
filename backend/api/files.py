from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import FileResponse as FastAPIFileResponse, StreamingResponse
from io import BytesIO
try:
    from PIL import Image
except ImportError:
    Image = None
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Bucket, Object as S3Object
from api.deps import get_current_user
import schemas
import os
import uuid
from core.config import settings

router = APIRouter(prefix="/api/files", tags=["files"])

def range_requests_response(request: Request, file_path: str, content_type: str):
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")
    
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
    }

    if not range_header:
        headers["Content-Length"] = str(file_size)
        return FastAPIFileResponse(
            path=file_path,
            headers=headers,
            media_type=content_type,
            status_code=200,
        )

    try:
        range_str = range_header.replace("bytes=", "")
        start_str, end_str = range_str.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
    except ValueError:
        return FastAPIFileResponse(path=file_path, status_code=416)

    if start >= file_size or end >= file_size or start > end:
        headers["Content-Range"] = f"bytes */{file_size}"
        return FastAPIFileResponse(path=file_path, headers=headers, status_code=416)

    chunk_size = end - start + 1
    headers["Content-Length"] = str(chunk_size)
    headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    def file_iterator():
        with open(file_path, "rb") as f:
            f.seek(start)
            bytes_left = chunk_size
            while bytes_left > 0:
                chunk = f.read(min(131072, bytes_left))
                if not chunk:
                    break
                bytes_left -= len(chunk)
                yield chunk

    return StreamingResponse(
        file_iterator(),
        headers=headers,
        status_code=206,
        media_type=content_type,
    )

@router.get("", response_model=List[schemas.FileResponse])
def get_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    buckets = db.query(Bucket).filter(Bucket.owner_id == current_user.id).all()
    bucket_ids = [b.id for b in buckets]
    
    objects = db.query(S3Object).filter(
        S3Object.bucket_id.in_(bucket_ids), 
        S3Object.is_deleted == False
    ).all()
    
    response = []
    for obj in objects:
        response.append({
            "id": obj.id,
            "name": obj.key.split('/')[-1],
            "size": obj.size,
            "mime_type": obj.mime_type,
            "uploaded_at": obj.uploaded_at,
            "bucket_name": obj.bucket.name,
            "key": obj.key
        })
    return response

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    bucket_name: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not bucket_name:
        bucket_name = "default"
        
    bucket = db.query(Bucket).filter(Bucket.name == bucket_name, Bucket.owner_id == current_user.id).first()
    if not bucket:
        bucket = Bucket(name=bucket_name, owner_id=current_user.id)
        db.add(bucket)
        db.commit()
        db.refresh(bucket)

    os.makedirs(f"{settings.storage_dir}/{current_user.id}/{bucket_name}", exist_ok=True)
    file_path = f"{settings.storage_dir}/{current_user.id}/{bucket_name}/{file.filename}"
    
    size = 0
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            buffer.write(chunk)
            size += len(chunk)

    if current_user.used_storage + size > current_user.storage_quota:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Storage quota exceeded")

    current_user.used_storage += size

    s3_obj = db.query(S3Object).filter(S3Object.bucket_id == bucket.id, S3Object.key == file.filename).first()
    if s3_obj:
        s3_obj.size = size
        s3_obj.storage_path = file_path
        s3_obj.mime_type = file.content_type
        s3_obj.is_deleted = False
    else:
        s3_obj = S3Object(
            bucket_id=bucket.id,
            key=file.filename,
            size=size,
            mime_type=file.content_type,
            storage_path=file_path
        )
        db.add(s3_obj)

    db.commit()
    return {"message": "success"}

@router.post("/create-archive")
def create_archive(
    req: schemas.FileArchiveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import zipfile
    
    objects = db.query(S3Object).filter(S3Object.id.in_(req.file_ids)).all()
    if not objects:
        raise HTTPException(status_code=404, detail="Files not found")

    for obj in objects:
        if obj.bucket.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")

    bucket_name = objects[0].bucket.name
    bucket_id = objects[0].bucket.id
    zip_filename = f"archive_{uuid.uuid4().hex[:8]}.zip"
    
    storage_dir = f"{settings.storage_dir}/{current_user.id}/{bucket_name}"
    os.makedirs(storage_dir, exist_ok=True)
    zip_path = f"{storage_dir}/{zip_filename}"
    
    size = 0
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for obj in objects:
            zf.write(obj.storage_path, arcname=obj.key.split('/')[-1])
            
    size = os.path.getsize(zip_path)
    
    if current_user.used_storage + size > current_user.storage_quota:
        os.remove(zip_path)
        raise HTTPException(status_code=400, detail="Storage quota exceeded")

    current_user.used_storage += size
    
    new_obj = S3Object(
        bucket_id=bucket_id,
        key=zip_filename,
        size=size,
        mime_type="application/zip",
        storage_path=zip_path
    )
    db.add(new_obj)
    db.commit()
    
    return {"message": "Archive created", "filename": zip_filename}

@router.get("/preview/{file_id}")
def get_file_preview(
    file_id: str, 
    request: Request,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    obj = db.query(S3Object).filter(S3Object.id == file_id, S3Object.is_deleted == False).first()
    if not obj or obj.bucket.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(obj.storage_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    mime = obj.mime_type or ""
    if mime.startswith("image/") and Image and not mime.endswith("gif") and not mime.endswith("svg+xml"):
        try:
            with Image.open(obj.storage_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail((800, 800))
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=75)
                buffer.seek(0)
                return StreamingResponse(buffer, media_type="image/jpeg")
        except Exception:
            pass

    return range_requests_response(request, obj.storage_path, mime or "application/octet-stream")

@router.get("/shared/{file_id}", response_model=schemas.SharedFileResponse)
def get_shared_file_info(file_id: str, db: Session = Depends(get_db)):
    obj = db.query(S3Object).filter(S3Object.id == file_id, S3Object.is_deleted == False).first()
    if not obj:
        raise HTTPException(status_code=404, detail="File not found")
        
    return {
        "id": obj.id,
        "name": obj.key.split('/')[-1],
        "size": obj.size,
        "mime_type": obj.mime_type,
        "uploaded_at": obj.uploaded_at,
        "owner_email": obj.bucket.owner.email
    }

@router.get("/shared/{file_id}/download")
def download_shared_file(file_id: str, request: Request, db: Session = Depends(get_db)):
    obj = db.query(S3Object).filter(S3Object.id == file_id, S3Object.is_deleted == False).first()
    if not obj or not os.path.exists(obj.storage_path):
        raise HTTPException(status_code=404, detail="File not found")

    filename = obj.key.split('/')[-1]
    res = range_requests_response(request, obj.storage_path, obj.mime_type or "application/octet-stream")
    res.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return res

@router.get("/shared/{file_id}/preview")
def get_shared_file_preview(file_id: str, request: Request, db: Session = Depends(get_db)):
    obj = db.query(S3Object).filter(S3Object.id == file_id, S3Object.is_deleted == False).first()
    if not obj or not os.path.exists(obj.storage_path):
        raise HTTPException(status_code=404, detail="File not found")

    mime = obj.mime_type or ""
    if mime.startswith("image/") and Image and not mime.endswith("gif") and not mime.endswith("svg+xml"):
        try:
            with Image.open(obj.storage_path) as img:
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img.thumbnail((800, 800))
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=75)
                buffer.seek(0)
                return StreamingResponse(buffer, media_type="image/jpeg")
        except Exception:
            pass

    return range_requests_response(request, obj.storage_path, mime or "application/octet-stream")
