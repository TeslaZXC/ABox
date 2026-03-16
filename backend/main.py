from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from api import auth, files, s3

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ABox API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(s3.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
