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
async def process_image(
    file: UploadFile = File(...),
    task_type: str = Form("bg-remove")
):
    try:
        # 1. Image read karna
        input_data = await file.read()
        working_img = Image.open(io.BytesIO(input_data))
        
        # Initialize output_image
        output_image = None
        fmt = "JPEG"
        media_type = "image/jpeg"
        
        # 2. Check karna ki user ko kya karna hai
        if task_type == "bg-remove":
            # BACKGROUND REMOVAL (Note: PIL se sirf color change hota hai, 
            # actual removal ke liye 'rembg' library lagti hai. 
            # Abhi ke liye hum image ko waise hi bhej rahe hain)
            if working_img.mode != "RGBA":
                working_img = working_img.convert("RGBA")
            
            output_image = working_img
            fmt = "PNG"
            media_type = "image/png"
            
        elif task_type == "enhance":
            # QUALITY ENHANCEMENT
            working_img = ImageEnhance.Color(working_img).enhance(1.2)
            working_img = ImageEnhance.Contrast(working_img).enhance(1.25)
            working_img = ImageEnhance.Sharpness(working_img).enhance(1.3)
            
            output_image = working_img
            fmt = "JPEG"
            media_type = "image/jpeg"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid task_type.")
        
        # 3. Photo ko wapas data stream mein badalna
        if output_image is not None:
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format=fmt)
            img_byte_arr.seek(0)
            return StreamingResponse(img_byte_arr, media_type=media_type)
        else:
            raise HTTPException(status_code=500, detail="Processing failed.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/home", response_class=HTMLResponse)
def get_frontend():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()