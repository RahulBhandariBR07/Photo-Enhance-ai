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
    # 1. Shuru mein hi variable initialize karo
    output_image = None
    fmt = "JPEG"
    media_type = "image/jpeg"

    try:
        input_data = await file.read()
        working_img = Image.open(io.BytesIO(input_data))
        
        if task_type == "bg-remove":
            if working_img.mode != "RGBA":
                working_img = working_img.convert("RGBA")
            output_image = working_img
            fmt = "PNG"
            media_type = "image/png"
            
        elif task_type == "enhance":
            img = ImageEnhance.Color(working_img).enhance(1.2)
            img = ImageEnhance.Contrast(img).enhance(1.25)
            img = ImageEnhance.Sharpness(img).enhance(1.3)
            output_image = img
            fmt = "JPEG"
            media_type = "image/jpeg"
        else:
            raise HTTPException(status_code=400, detail="Invalid task_type")
        
        # 2. Check karo ki kya image process hui
        if output_image is None:
            raise HTTPException(status_code=500, detail="Processing failed")

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format=fmt)
        img_byte_arr.seek(0)
        return StreamingResponse(img_byte_arr, media_type=media_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))