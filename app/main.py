from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tasks/")
async def process_image(file: UploadFile = File(...), task_type: str = Form(...)):
    # 1. Input image read karo
    input_data = await file.read()
    
    # 2. Background remove logic
    if task_type == "remove_background":
        output_data = remove(input_data)
    else:
        output_data = input_data
        
    # 3. Image wapas bhejo
    return StreamingResponse(io.BytesIO(output_data), media_type="image/png")