"""
Image Processing Service for AI Enchanly.

This module provides the image processing algorithms using PIL (Pillow) and
rembg for background removal. It also coordinates running these tasks in the
background and updating the database status accordingly.
"""

import logging
import os
from PIL import Image, ImageEnhance
import rembg
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task

# Configure logging for the service layer
logger = logging.getLogger("enchanly.services.image")


def remove_background(input_path: str, output_path: str) -> None:
    """
    Removes the background of the image using the rembg library.

    Args:
        input_path (str): File path to the original image.
        output_path (str): Target file path for the output PNG image.
    """
    logger.info("Starting background removal for: %s", input_path)
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")

    # Open image
    with Image.open(input_path) as img:
        # Convert to RGBA for alpha channel transparency support if not already
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Remove background using rembg
        output_data = rembg.remove(img)
        
        # Save output image as PNG to retain transparency
        output_data.save(output_path, "PNG")
        
    logger.info("Successfully removed background. Saved to: %s", output_path)


def enhance_image(input_path: str, output_path: str) -> None:
    """
    Enhances the image using PIL ImageEnhance parameters.
    Increases contrast, color saturation, and sharpness to deliver a premium look.

    Args:
        input_path (str): File path to the original image.
        output_path (str): Target file path for the output enhanced image.
    """
    logger.info("Starting image enhancement for: %s", input_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")

    with Image.open(input_path) as img:
        # If image is RGBA, we convert to RGB to save as JPEG, or maintain PNG if output_path is PNG.
        # Let's preserve original format or save as PNG to be safe.
        working_img = img.copy()

        # 1. Enhance Color (Saturation) - factor 1.2 (20% increase)
        color_enhancer = ImageEnhance.Color(working_img)
        working_img = color_enhancer.enhance(1.2)

        # 2. Enhance Contrast - factor 1.25 (25% increase)
        contrast_enhancer = ImageEnhance.Contrast(working_img)
        working_img = contrast_enhancer.enhance(1.25)

        # 3. Enhance Sharpness - factor 1.3 (30% increase)
        sharpness_enhancer = ImageEnhance.Sharpness(working_img)
        working_img = sharpness_enhancer.enhance(1.3)

        # Save to output path. Use PNG or same format as input
        _, ext = os.path.splitext(output_path.lower())
        fmt = "PNG" if ext == ".png" else "JPEG"
        
        # If saving as JPEG, convert RGBA to RGB to avoid alpha errors
        if fmt == "JPEG" and working_img.mode == "RGBA":
            working_img = working_img.convert("RGB")
            
        working_img.save(output_path, fmt)

    logger.info("Successfully enhanced image. Saved to: %s", output_path)


def run_image_processing_task(task_id: str) -> None:
    """
    Core function run as a background job to process the image and update the db.
    This session runs isolated in a background thread provided by FastAPI.

    Args:
        task_id (str): The unique ID of the Task model to be updated.
    """
    logger.info("Task runner started for task ID: %s", task_id)
    
    # Establish a fresh session database connection for the background thread
    db: Session = SessionLocal()
    
    try:
        # Retrieve the task from the database
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            logger.error("Task with ID %s not found in the database. Aborting.", task_id)
            return

        # Update task status to processing
        task.status = "processing"
        db.commit()
        logger.info("Task %s status updated to 'processing'", task_id)

        # Build output path
        # Output paths will be saved in the static output directory
        base_dir = os.path.dirname(task.original_image_path)
        output_dir = os.path.join(os.path.dirname(base_dir), "processed")
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(task.original_image_path)
        name, ext = os.path.splitext(filename)
        
        # Force png for background removal since transparency is required
        if task.task_type == "bg-remove":
            output_filename = f"{name}_processed_{task_id}.png"
        else:
            output_filename = f"{name}_processed_{task_id}{ext}"
            
        processed_path = os.path.join(output_dir, output_filename)

        # Execute the corresponding service method
        if task.task_type == "bg-remove":
            remove_background(task.original_image_path, processed_path)
        elif task.task_type == "enhance":
            enhance_image(task.original_image_path, processed_path)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")

        # Update status to completed and register path
        task.status = "completed"
        # Store relative paths to make static serving cleaner and portable
        task.processed_image_path = os.path.normpath(processed_path).replace("\\", "/")
        db.commit()
        logger.info("Task %s completed successfully. Processed file: %s", task_id, processed_path)

    except Exception as e:
        logger.exception("Exception occurred during task execution: %s", str(e))
        # Ensure session rollbacks are handled and error details are stored
        db.rollback()
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
            
    finally:
        # Always close session local connections
        db.close()
        logger.info("Task runner session closed for task ID: %s", task_id)
