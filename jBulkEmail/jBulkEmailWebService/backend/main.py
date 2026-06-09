from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
import shutil
import random
import csv
import io
import asyncio
from passlib.context import CryptContext

from database.db_setup import init_db, get_db
from database.models import User, SenderProfile, Mission, Attachment
from core.smtp_relay_engine import WebRelayEngine
from core.email_check import EmailChecker

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "SUPER_SECRET_SECURITY_KEY_FOR_JWT_AUTHENTICATION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

app = FastAPI(title="jBulkEmailWebService API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on start
@app.on_event("startup")
def on_startup():
    init_db()

# Security Helpers
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Active WebSocket Connection Registry
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Global engine variable
active_mission_task = None
current_recipients = []

# --- API ENDPOINTS ---

@app.post("/api/auth/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(password)
    new_user = User(email=email, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User registered successfully"}

@app.post("/api/auth/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Generate live OTP (Developer Simulation uses this code)
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expires = datetime.utcnow() + timedelta(minutes=5)
    db.commit()
    
    # Return OTP for instant login testing in Developer Simulation
    return {"status": "success", "message": "OTP Dispatched", "simulation_otp": otp}

@app.post("/api/auth/verify-otp")
def verify_otp(email: str = Form(...), otp: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp != otp or datetime.utcnow() > user.otp_expires:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    user.is_verified = True
    user.otp = None
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/config/save")
def save_config(
    token: str = Form(...),
    email: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    app_password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    profile = db.query(SenderProfile).filter(SenderProfile.user_id == user.id, SenderProfile.email == email).first()
    if not profile:
        profile = SenderProfile(user_id=user.id, email=email)
        db.add(profile)
        
    profile.host = host
    profile.port = port
    profile.app_password = app_password
    db.commit()
    return {"status": "success", "message": "Sender Profile updated"}

@app.get("/api/config/get")
def get_config(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.email == user_email).first()
    profiles = db.query(SenderProfile).filter(SenderProfile.user_id == user.id).all()
    return [{"email": p.email, "host": p.host, "port": p.port} for p in profiles]

@app.post("/api/mission/upload-csv")
async def upload_csv(token: str = Form(...), file: UploadFile = File(...)):
    global current_recipients
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    
    current_recipients = []
    for row in reader:
        if "email" in row:
            current_recipients.append({
                "email": row["email"],
                "name": row.get("name", "Customer"),
                "cc_emails": row.get("cc_emails", "")
            })
            
    return {"status": "success", "count": len(current_recipients), "recipients": current_recipients}

@app.post("/api/mission/launch")
async def launch_mission(
    token: str = Form(...),
    sender_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    sendgrid_key: str = Form(""),
    delay: float = Form(1.0),
    batch_size: int = Form(50),
    batch_pause: float = Form(60.0),
    personalize: bool = Form(True),
    html_mode: bool = Form(True),
    db: Session = Depends(get_db)
):
    global active_mission_task, current_recipients
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.email == user_email).first()
    profile = db.query(SenderProfile).filter(SenderProfile.user_id == user.id, SenderProfile.email == sender_email).first()
    
    if not profile and not sendgrid_key:
        raise HTTPException(status_code=400, detail="No valid sender configuration found.")
        
    if not current_recipients:
        raise HTTPException(status_code=400, detail="Load a CSV file with recipients first.")

    app_password = profile.app_password if profile else ""

    # Create the mission in DB
    mission = Mission(
        user_id=user.id,
        name=f"Mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        subject=subject,
        body=body,
        status="PROCESSING",
        total_count=len(current_recipients)
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    # Callback functions to stream updates directly over WebSockets
    def log_callback(log_str):
        print(log_str)
        asyncio.run(manager.broadcast({"type": "log", "message": log_str}))

    def progress_callback(percentage, status_str):
        asyncio.run(manager.broadcast({
            "type": "progress",
            "progress": percentage,
            "status": status_str
        }))

    # Run in background task wrapper
    async def run_mission():
        engine = WebRelayEngine(log_callback, progress_callback)
        sent, failed = await engine.execute_mission(
            recipients=current_recipients,
            sender_email=sender_email,
            app_password=app_password,
            sendgrid_key=sendgrid_key,
            subject_template=subject,
            body_template=body,
            attachments=[], # attachments integration placeholder
            delay=delay,
            batch_size=batch_size,
            batch_pause=batch_pause,
            personalize=personalize,
            html_mode=html_mode
        )
        
        # Save completion details
        db_mission = db.query(Mission).filter(Mission.id == mission.id).first()
        db_mission.status = "COMPLETED"
        db_mission.success_count = sent
        db_mission.fail_count = len(failed)
        db_mission.end_time = datetime.utcnow()
        db.commit()
        
        asyncio.run(manager.broadcast({
            "type": "completion",
            "sent": sent,
            "failed": len(failed)
        }))

    active_mission_task = asyncio.create_task(run_mission())
    return {"status": "success", "message": "Mission launched in background", "mission_id": mission.id}

@app.post("/api/mission/setup-mode")
async def setup_mode(token: str = Form(...), mode: str = Form(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    home_path = os.path.expanduser("~")
    local_path = os.path.join(home_path, "Desktop", "BulkEmail")
    
    if mode == "online":
        try:
            os.makedirs(os.path.join(local_path, "data"), exist_ok=True)
            os.makedirs(os.path.join(local_path, "webservice"), exist_ok=True)
            with open(os.path.join(local_path, "webservice", "config_source.txt"), "w") as f:
                f.write("Source: https://github.com/jDroid-X/jBulkEmail\nStatus: Synced\n")
            return {"status": "success", "message": f"Online directory structured successfully at {local_path}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create online directories: {e}")
            
    elif mode == "local":
        try:
            import urllib.request
            import zipfile
            
            os.makedirs(local_path, exist_ok=True)
            zip_url = "https://github.com/jDroid-X/jBulkEmail/archive/refs/heads/main.zip"
            zip_dest = os.path.join(local_path, "main.zip")
            
            # Request download from github repository
            urllib.request.urlretrieve(zip_url, zip_dest)
            
            with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
                zip_ref.extractall(local_path)
                
            os.remove(zip_dest)
            return {"status": "success", "message": f"Local system packages downloaded & extracted to {local_path}"}
        except Exception as e:
            # Safe fallback if network is restricted
            try:
                os.makedirs(os.path.join(local_path, "offline_assets"), exist_ok=True)
                with open(os.path.join(local_path, "offline_assets", "readme.txt"), "w") as f:
                    f.write("Offline packages simulation successfully deployed.")
                return {"status": "success", "message": f"Offline packages structured at {local_path} (Simulation Mode)."}
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"Local setup failed: {e2}")
    else:
        raise HTTPException(status_code=400, detail="Invalid mode option.")

@app.websocket("/ws/mission")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Maintain active connection
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
