from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import schemas
import models
from database import get_db
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_verification_code,
    generate_s3_keys
)
from core.email import send_verification_email
from api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(email=user_in.email, password_hash=hashed_password, is_active=False)
    db.add(new_user)
    
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    verification = models.EmailVerification(email=user_in.email, code=code, expires_at=expires_at)
    db.add(verification)
    
    db.commit()
    db.refresh(new_user)

    send_verification_email(user_in.email, code)

    return {"message": "Код подтверждения отправлен на email"}

@router.post("/verify-email")
def verify_email(data: schemas.VerifyEmail, db: Session = Depends(get_db)):
    verification = db.query(models.EmailVerification).filter(
        models.EmailVerification.email == data.email,
        models.EmailVerification.code == data.code
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    if datetime.utcnow() > verification.expires_at:
        db.delete(verification)
        db.commit()
        raise HTTPException(status_code=400, detail="Code expired")

    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    access_key, secret_key = generate_s3_keys()
    user.access_key = access_key
    user.secret_key = secret_key

    db.delete(verification)
    db.commit()

    return {"message": "Email подтвержден"}

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/resend-code")
def resend_code(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="User already active")

    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    verification = db.query(models.EmailVerification).filter(models.EmailVerification.email == data.email).first()
    if verification:
        verification.code = code
        verification.expires_at = expires_at
    else:
        verification = models.EmailVerification(email=data.email, code=code, expires_at=expires_at)
        db.add(verification)
        
    db.commit()
    send_verification_email(data.email, code)

    return {"message": "Код подтверждения отправлен на email"}

@router.get("/me", response_model=schemas.UserResponse)
def get_user_me(current_user: models.User = Depends(get_current_user)):
    return current_user
