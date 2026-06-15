from fastapi.responses import HTMLResponse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
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
    task_type: str = Form("bg-remove")  # Default "bg-remove" rahega, mobile se "enhance" bhi bhej sakte ho
):
    try:
        # 1. Image read karna
        input_data = await file.read()
        working_img = Image.open(io.BytesIO(input_data))
        
        # 2. Check karna ki user ko kya karna hai
        if task_type == "bg-remove":
            # BACKGROUND REMOVAL
            if working_img.mode != "RGBA":
                working_img = working_img.convert("RGBA")
<<<<<<< HEAD
            output_image = remove(working_img, session=session)
=======
            output_image = rembg.remove(working_img)
>>>>>>> 8438d4aa2d58611e40c852d0c17b6d1a2f5fcec4
            fmt = "PNG"
            media_type = "image/png"
            
        elif task_type == "enhance":
            # QUALITY ENHANCEMENT (Color, Contrast, Sharpness badhana)
            # 20% Saturation badhao
            color_enhancer = ImageEnhance.Color(working_img)
            working_img = color_enhancer.enhance(1.2)

            # 25% Contrast badhao
            contrast_enhancer = ImageEnhance.Contrast(working_img)
            working_img = contrast_enhancer.enhance(1.25)

            # 30% Sharpness badhao (Photo ekdum saaf dikhegi)
            sharpness_enhancer = ImageEnhance.Sharpness(working_img)
            working_img = sharpness_enhancer.enhance(1.3)
            
            output_image = working_img
            fmt = "JPEG"
            media_type = "image/jpeg"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid task_type. Use 'bg-remove' or 'enhance'")
        
        # 3. Photo ko wapas data stream mein badalna
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format=fmt)
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type=media_type)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/home", response_class=HTMLResponse)
def get_frontend():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()