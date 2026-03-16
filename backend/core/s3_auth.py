from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import urllib.parse

def verify_s3_auth(request: Request, db: Session = Depends(get_db)):
    access_key = request.query_params.get("AWSAccessKeyId")
    if access_key:
        user = db.query(models.User).filter(models.User.access_key == access_key).first()
        if not user:
            raise HTTPException(status_code=403, detail="Invalid Access Key")
        return user

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    if auth_header.startswith("AWS4-HMAC-SHA256"):
        try:
            parts = auth_header.split("Credential=")[1].split(",")[0]
            access_key = parts.split("/")[0]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid Authorization Header Format")
            
    elif auth_header.startswith("AWS "):
        try:
            access_key = auth_header.split("AWS ")[1].split(":")[0]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid Authorization Header Format")
    else:
        raise HTTPException(status_code=401, detail="Unsupported Authorization Method")

    user = db.query(models.User).filter(models.User.access_key == access_key).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Access Key")

    return user
