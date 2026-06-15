from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageEnhance
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tasks/")
async def process_image(file: UploadFile = File(...), task_type: str = Form("bg-remove")):
    try:
        # 1. Shuru mein hi variable initialize karo
        output_image = None
        fmt = "JPEG"
        media_type = "image/jpeg"
        
        input_data = await file.read()
        working_img = Image.open(io.BytesIO(input_data))
        
        # 2. Logic processing
        if task_type == "bg-remove":
            # Simple RGBA conversion for now
            output_image = working_img.convert("RGBA")
            fmt = "PNG"
            media_type = "image/png"
            
        elif task_type == "enhance":
            img = ImageEnhance.Color(working_img).enhance(1.2)
            img = ImageEnhance.Contrast(img).enhance(1.25)
            output_image = ImageEnhance.Sharpness(img).enhance(1.3)
            fmt = "JPEG"
            media_type = "image/jpeg"
        else:
            raise HTTPException(status_code=400, detail="Invalid task_type")
        
        # 3. Safe Return
        if output_image:
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format=fmt)
            img_byte_arr.seek(0)
            return StreamingResponse(img_byte_arr, media_type=media_type)
        else:
            raise HTTPException(status_code=500, detail="Processing failed")

    except Exception as e:
        # Proper JSON error response
        raise HTTPException(status_code=500, detail=str(e))