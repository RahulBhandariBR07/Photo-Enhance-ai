from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def server_frontend():
    return FileResponse("app/index.html")

@app.post("/api/tasks/")
async def process_image(file: UploadFile = File(...), task_type: str = Form(...)):
    try:
        # Tumhara processing logic yahan continue hoga
        return {"status": "success", "task": task_type}
    except Exception as e:
        return {"error": str(e)}