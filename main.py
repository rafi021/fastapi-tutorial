from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import shutil   # For file operations


app = FastAPI()

# Step 1: Create 'uploads' directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Step 2: Mount 'uploads' directory to serve static files
# URL: http://localhost:8000/files/your_uploaded_file.ext
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")



# Step 3: Save the uploaded file to the 'uploads' directory
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    file_Path = os.path.join(UPLOAD_DIR, filename)
    
    if not filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    try:
        with open(file_Path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return {
        "message": "File uploaded successfully.",
        "filename": filename, "url": f"/files/{filename}"
        }

# Step 4: Get the uploaded file using the URL provided in the response of the upload endpoint.
# Example: http://localhost:8000/files/your_uploaded_file.ext
@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return {"message": "File exists.", "url": f"http://localhost:8000/files/{filename}"}