from fastapi import APIRouter, Depends, Request, Response, HTTPException, Path, Header
from sqlalchemy.orm import Session
from database import get_db
import models
from core.s3_auth import verify_s3_auth
from core.config import settings
import uuid
from datetime import datetime
import os
import hashlib

router = APIRouter(prefix="/s3", tags=["s3"])

def format_s3_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

@router.get("/")
def list_buckets(current_user: models.User = Depends(verify_s3_auth), db: Session = Depends(get_db)):
    buckets = db.query(models.Bucket).filter(models.Bucket.owner_id == current_user.id).all()
    
    xml_buckets = ""
    for b in buckets:
        xml_buckets += f"""
        <Bucket>
            <Name>{b.name}</Name>
            <CreationDate>{format_s3_date(b.created_at)}</CreationDate>
        </Bucket>"""
        
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Owner>
        <ID>{current_user.id}</ID>
        <DisplayName>{current_user.email}</DisplayName>
    </Owner>
    <Buckets>
        {xml_buckets}
    </Buckets>
</ListAllMyBucketsResult>"""
    return Response(content=xml_response, media_type="application/xml")

@router.put("/{bucket_name}")
def create_bucket(
    bucket_name: str, 
    current_user: models.User = Depends(verify_s3_auth), 
    db: Session = Depends(get_db)
):
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>InvalidBucketName</Code>
    <Message>The specified bucket is not valid.</Message>
</Error>"""
        return Response(content=error_xml, media_type="application/xml", status_code=400)
        
    existing = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    
    if existing:
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>BucketAlreadyExists</Code>
    <Message>The requested bucket name is not available.</Message>
</Error>"""
        return Response(content=error_xml, media_type="application/xml", status_code=409)

    new_bucket = models.Bucket(name=bucket_name, owner_id=current_user.id)
    db.add(new_bucket)
    db.commit()
    
    os.makedirs(f"{settings.storage_dir}/{current_user.id}/{bucket_name}", exist_ok=True)
    return Response(status_code=200)

@router.put("/{bucket_name}/{object_key:path}")
async def put_object(
    request: Request,
    bucket_name: str,
    object_key: str,
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    
    if not bucket:
        return Response(status_code=404, content="<Error><Code>NoSuchBucket</Code></Error>", media_type="application/xml")

    storage_dir = f"{settings.storage_dir}/{current_user.id}/{bucket_name}"
    os.makedirs(os.path.dirname(f"{storage_dir}/{object_key}"), exist_ok=True)
    
    file_path = f"{storage_dir}/{object_key}"
    
    md5_hash = hashlib.md5()
    size = 0
    
    with open(file_path, "wb") as f:
        async for chunk in request.stream():
            f.write(chunk)
            md5_hash.update(chunk)
            size += len(chunk)
            
    if current_user.used_storage + size > current_user.storage_quota:
        os.remove(file_path)
        return Response(status_code=400, content="<Error><Code>QuotaExceeded</Code></Error>", media_type="application/xml")
        
    etag = md5_hash.hexdigest()
    
    s3_obj = db.query(models.Object).filter(models.Object.bucket_id == bucket.id, models.Object.key == object_key).first()
    if s3_obj:
        current_user.used_storage = current_user.used_storage - s3_obj.size + size
        s3_obj.size = size
        s3_obj.etag = etag
        s3_obj.is_deleted = False
        s3_obj.last_modified = datetime.utcnow()
    else:
        current_user.used_storage += size
        content_type = request.headers.get("content-type", "application/octet-stream")
        s3_obj = models.Object(
            bucket_id=bucket.id,
            key=object_key,
            etag=etag,
            size=size,
            mime_type=content_type,
            storage_path=file_path
        )
        db.add(s3_obj)
        
    db.commit()
    
    headers = {"ETag": f'"{etag}"'}
    return Response(status_code=200, headers=headers)

@router.get("/{bucket_name}")
def list_objects(
    bucket_name: str,
    prefix: str = "",
    delimiter: str = "",
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    
    if not bucket:
        return Response(status_code=404, content="<Error><Code>NoSuchBucket</Code></Error>", media_type="application/xml")
        
    query = db.query(models.Object).filter(
        models.Object.bucket_id == bucket.id,
        models.Object.is_deleted == False
    )
    
    if prefix:
        query = query.filter(models.Object.key.startswith(prefix))
        
    objects = query.all()
    
    contents_xml = ""
    for obj in objects:
        contents_xml += f"""
        <Contents>
            <Key>{obj.key}</Key>
            <LastModified>{format_s3_date(obj.last_modified)}</LastModified>
            <ETag>"{obj.etag}"</ETag>
            <Size>{obj.size}</Size>
            <Owner>
                <ID>{current_user.id}</ID>
                <DisplayName>{current_user.email}</DisplayName>
            </Owner>
            <StorageClass>STANDARD</StorageClass>
        </Contents>"""
        
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Name>{bucket.name}</Name>
    <Prefix>{prefix}</Prefix>
    <Marker></Marker>
    <MaxKeys>1000</MaxKeys>
    <IsTruncated>false</IsTruncated>
    {contents_xml}
</ListBucketResult>"""
    return Response(content=xml_response, media_type="application/xml")

@router.delete("/{bucket_name}")
def delete_bucket(
    bucket_name: str,
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    
    if not bucket:
        return Response(status_code=204)
        
    objects = db.query(models.Object).filter(models.Object.bucket_id == bucket.id).all()
    
    total_freed = 0
    for obj in objects:
        if os.path.exists(obj.storage_path):
            os.remove(obj.storage_path)
        total_freed += obj.size
        
    current_user.used_storage = max(0, current_user.used_storage - total_freed)
    
    bucket_dir = f"{settings.storage_dir}/{current_user.id}/{bucket_name}"
    if os.path.exists(bucket_dir):
        import shutil
        shutil.rmtree(bucket_dir)
        
    db.delete(bucket)
    db.commit()
    
    return Response(status_code=204)

@router.get("/{bucket_name}/{object_key:path}")
def get_object(
    bucket_name: str,
    object_key: str,
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
        
    obj = db.query(models.Object).filter(
        models.Object.bucket_id == bucket.id,
        models.Object.key == object_key,
        models.Object.is_deleted == False
    ).first()
    
    if not obj or not os.path.exists(obj.storage_path):
        return Response(status_code=404, content="<Error><Code>NoSuchKey</Code></Error>", media_type="application/xml")
        
    with open(obj.storage_path, "rb") as f:
        file_bytes = f.read()

    headers = {
        "ETag": f'"{obj.etag}"',
        "Content-Length": str(obj.size)
    }
    return Response(content=file_bytes, media_type=obj.mime_type or "application/octet-stream", headers=headers)

@router.delete("/{bucket_name}/{object_key:path}")
def delete_object(
    bucket_name: str,
    object_key: str,
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    if not bucket:
        return Response(status_code=204)
        
    obj = db.query(models.Object).filter(
        models.Object.bucket_id == bucket.id,
        models.Object.key == object_key,
        models.Object.is_deleted == False
    ).first()
    
    if obj:
        if os.path.exists(obj.storage_path):
            os.remove(obj.storage_path)
            
        current_user.used_storage = max(0, current_user.used_storage - obj.size)
        obj.is_deleted = True
        db.commit()
    
    return Response(status_code=204)


@router.head("/{bucket_name}/{object_key:path}")
def head_object(
    bucket_name: str,
    object_key: str,
    current_user: models.User = Depends(verify_s3_auth),
    db: Session = Depends(get_db)
):
    bucket = db.query(models.Bucket).filter(
        models.Bucket.name == bucket_name,
        models.Bucket.owner_id == current_user.id
    ).first()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
        
    obj = db.query(models.Object).filter(
        models.Object.bucket_id == bucket.id,
        models.Object.key == object_key,
        models.Object.is_deleted == False
    ).first()
    
    if not obj:
        return Response(status_code=404)
        
    headers = {
        "ETag": f'"{obj.etag}"',
        "Content-Length": str(obj.size),
        "Last-Modified": obj.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Content-Type": obj.mime_type or "application/octet-stream"
    }
    return Response(status_code=200, headers=headers)
