from fastapi import FastAPI , File , UploadFile
import io
import numpy as np
from PIL import Image
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import sys
from predictor import recognize_all_cells
import shutil
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sadece test için, üretimde IP veya domain ile sınırla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/analyze-chess')
async def analyze_chess(file: UploadFile = File(...)): # file: UploadFile = File(...)
    if(file == None):
        return
    
    contents = await file.read()
    print("Dosya geldi mi? ->", file.filename)  # Dosya adını yazdır

    temp_dir = "uploaded_images"
    imagename = f"{uuid.uuid4()}.jpg"
    temp_path = os.path.join(temp_dir, imagename)
    
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    result = recognize_all_cells(temp_path)
    if os.path.exists(temp_path):
            os.remove(temp_path)
    return {"message": result["moves"]}

        
    