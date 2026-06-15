from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove  # Ye line sabse zaroori hai
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
    # File read karo
    input_data = await file.read()
    
    # Background remove logic
    if task_type == "remove_background":
        output_data = remove(input_data)
    else:
        # Agar enhancement ya aur kuch logic hai toh yahan aayega
        output_data = input_data

    # Result wapas bhejo
    return StreamingResponse(io.BytesIO(output_data), media_type="image/png")