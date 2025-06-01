from fastapi import FastAPI , File , UploadFile
import io
import numpy as np
from PIL import Image
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import sys
from yolo_project.predictor import recognize_all_cells

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

    temp_path = f"uploaded_images/temp_{datetime.now().timestamp()}.jpg"
    os.makedirs("uploaded_images", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(contents)
    recognize_all_cells(temp_path)
    # processimage fonksiyonu çağrılcak     
    # processimage(temp_path) gibi
    # processimage'ın bulunduğu hücre çıkartma klasörü backend klasörüne taşınacak       
    return {"message": "Hello World"}
