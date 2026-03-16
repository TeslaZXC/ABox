import uuid
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, Integer, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    access_key = Column(String(20), unique=True)
    secret_key = Column(String(40), unique=True)
    storage_quota = Column(BigInteger, default=10737418240)
    used_storage = Column(BigInteger, default=0)

    buckets = relationship("Bucket", back_populates="owner", cascade="all, delete-orphan")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)


class Bucket(Base):
    __tablename__ = "buckets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(63), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now())
    is_public = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("owner_id", "name", name="uix_owner_name"),)

    owner = relationship("User", back_populates="buckets")
    objects = relationship("Object", back_populates="bucket", cascade="all, delete-orphan")


class Object(Base):
    __tablename__ = "objects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bucket_id = Column(String(36), ForeignKey("buckets.id", ondelete="CASCADE"))
    key = Column(String(1024), nullable=False)
    etag = Column(String(32))
    size = Column(BigInteger, default=0, nullable=False)
    mime_type = Column(String(255))
    uploaded_at = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())
    storage_path = Column(String(1024), nullable=False)
    is_deleted = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("bucket_id", "key", name="uix_bucket_key"),)

    bucket = relationship("Bucket", back_populates="objects")
