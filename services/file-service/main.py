from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import shutil
import os
import jwt
import json
import redis

app = FastAPI(
    title="File Service",
    root_path="/api/v1/files"
)

security = HTTPBearer()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded images statically so the frontend can load thumbnails
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# JWT Configuration
SECRET_KEY = "super-secret-key-change-me"
ALGORITHM = "HS256"

# Database Configuration
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@postgres:5432/mediadb")

# Retry connecting to PostgreSQL up to 10 times on startup
engine = None
for attempt in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            break
    except Exception as e:
        print(f"PostgreSQL not ready yet (Attempt {attempt + 1}/10). Retrying in 2 seconds...")
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# Database Model
class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    uploader = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    current_user: str = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)

    metadata_record = FileMetadata(
        filename=file.filename,
        file_size=file_size,
        uploader=current_user
    )
    db.add(metadata_record)
    db.commit()
    db.refresh(metadata_record)

    # Invalidate Redis cache so the next GET query reads fresh data
    cache_key = f"files:{current_user}"
    redis_client.delete(cache_key)
        
    return {
        "id": metadata_record.id,
        "uploader": metadata_record.uploader,
        "filename": metadata_record.filename,
        "file_size_bytes": metadata_record.file_size,
        "uploaded_at": metadata_record.uploaded_at.isoformat(),
        "message": "File uploaded successfully!"
    }

@app.get("/my-files")
def get_user_files(
    current_user: str = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    cache_key = f"files:{current_user}"
    
    # 1. Try to fetch from Redis cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {"source": "cache (Redis)", "data": json.loads(cached_data)}
    
    # 2. Cache miss -> Fetch from PostgreSQL
    records = db.query(FileMetadata).filter(FileMetadata.uploader == current_user).all()
    files_list = [
        {
            "id": rec.id,
            "filename": rec.filename,
            "file_size_bytes": rec.file_size,
            "uploader": rec.uploader,
            "uploaded_at": rec.uploaded_at.isoformat(),
            "url": f"/api/v1/files/static/{rec.filename}"
        }
        for rec in records
    ]
    
    # 3. Save result to Redis with a 60-second expiration (TTL)
    redis_client.setex(cache_key, 60, json.dumps(files_list))
    
    return {"source": "database (PostgreSQL)", "data": files_list}