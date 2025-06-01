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
    folder_path = 'runs/detect/batch_predict'
        
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    
    contents = await file.read()
    print("Dosya geldi mi? ->", file.filename)  # Dosya adını yazdır

    temp_dir = "uploaded_images"
    temp_path = os.path.join(temp_dir, "temp.jpg")
    
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    result = recognize_all_cells(temp_path)
    
    # processimage fonksiyonu çağrılcak     
    # processimage(temp_path) gibi
    # processimage'ın bulunduğu hücre çıkartma klasörü backend klasörüne taşınacak       
    return {"message": result["moves"]}
    