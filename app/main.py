from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def server_frontend():
    return FileResponse("app/index.html")

@app.post("/api/tasks/")
async def process_image(file: UploadFile = File(...), task_type: str = Form(...)):
    # Yahan tumhari image processing logic aayegi
    # Filhal ke liye testing ke liye original file wapas bhej rahe hain
    content = await file.read()
    return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")
    