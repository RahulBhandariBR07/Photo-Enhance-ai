from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
# ASLI FIX: database se get_db ke saath SessionLocal ko bhi import kar liya
from app.database import get_db, SessionLocal 
from app import models
import uuid
import os
import shutil
from app.services.image_service import run_image_processing_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

UPLOAD_DIR = os.path.join("static", "uploads", "original")
OUTPUT_DIR = os.path.join("static", "uploads", "processed")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_image_task(
    user_id: str = Form(...),
    task_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validation
    if task_type not in ["enhance", "bg-remove"]:
        raise HTTPException(status_code=400, detail="Invalid task type. Use 'enhance' or 'bg-remove'.")
    
    # 2. Unique task generation
    task_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    original_filename = f"{task_id}{file_extension}"
    original_path = os.path.join(UPLOAD_DIR, original_filename)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Database entry creation (Initial status)
    db_task = models.Task(
        task_id=task_id,
        user_id=user_id,
        original_image_path=original_path,
        task_type=task_type,
        status="processing"
    )
    db.add(db_task)
    db.commit()
    
    # 4. INSTANT EXECUTION (Bina kisi background thread ke seedhe process)
    try:
        # Pura db session pehle close kar rahe hain taaki service layer naya session bana sake (No DB Lock)
        db.close()
        
        # Sahi function call: Sirf ek task_id string bhej rahe hain jaisa service maang rahi hai
        run_image_processing_task(task_id)
        
        # Processing khatam hone ke baad fresh data fetch kar rahe hain output dikhane ke liye
        from app.database import SessionLocal
        fresh_db = SessionLocal()
        updated_task = fresh_db.query(models.Task).filter(models.Task.task_id == task_id).first()
        
        processed_path = updated_task.processed_image_path if updated_task else ""
        final_status = updated_task.status if updated_task else "completed"
        fresh_db.close()
        
        # Path clean karna URL ke liye
        clean_path = processed_path.replace("\\", "/") if processed_path else ""
        
        return {
            "task_id": task_id,
            "status": final_status,
            "message": "Image processed successfully instantly!",
            "download_url": f"http://10.77.59.178:8000/{clean_path}" if clean_path else None
        }
        
    except Exception as e:
        from app.database import SessionLocal
        error_db = SessionLocal()
        failed_task = error_db.query(models.Task).filter(models.Task.task_id == task_id).first()
        if failed_task:
            failed_task.status = "failed"
            failed_task.error_message = str(e)
            error_db.commit()
        error_db.close()
        
        return {
            "task_id": task_id,
            "status": "failed",
            "message": f"Processing failed: {str(e)}"
        }

@router.get("/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task