from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import os

# Database connection string using environment variables or defaults pointing to docker
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secretpassword")
DB_HOST = os.getenv("DB_HOST", "localhost")  # 'postgres' when running inside docker network
DB_NAME = os.getenv("DB_NAME", "mediadb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Model (Database Table)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Microservice", root_path="/api/v1/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {username} created successfully!"}

import jwt
from datetime import datetime, timedelta

# Secret key to sign tokens (in production, use an environment variable)
SECRET_KEY = "super-secret-key-change-me"
ALGORITHM = "HS256"

# Add this new login endpoint below your register endpoint
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # 1. Find user in database
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # 2. Verify password hash
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # 3. Create a JWT token valid for 30 minutes
    expiration = datetime.utcnow() + timedelta(minutes=30)
    token_data = {"sub": user.username, "exp": expiration}
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": f"Welcome back, {username}!"
    }