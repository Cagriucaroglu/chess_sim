import os
import subprocess
import shutil
import glob
import json
from main2 import process_image  # main2.py aynı klasörde olmalı
from ultralytics import YOLO
import numpy as np
from PIL import Image

def load_class_map(class_file_path):
    with open(class_file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def parse_prediction_txt(txt_path, class_map):
    boxes = []
    with open(txt_path, "r") as f:
        for line in f:
            class_id, x_center, y_center, width, height = map(float, line.strip().split())
            boxes.append({
                "char": class_map[int(class_id)],
                "x": x_center
            })
    return boxes

def recognize_character_from_image(image_path, model_path, class_map):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = f"runs/detect/predict_{image_name}"

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    subprocess.run([
        "yolo", "task=detect", "mode=predict",
        f"model={model_path}",
        f"source={image_path}",
        "save_txt=True",
        f"project=runs/detect",
        f"name=predict_{image_name}",
        "exist_ok=True",
        "conf=0.25"
    ], stdout=subprocess.DEVNULL)

    txt_path = os.path.join(output_dir, "labels", image_name + ".txt")
    if not os.path.exists(txt_path):
        print(f"Tahmin yok: {image_path}")
        return ""

    boxes = parse_prediction_txt(txt_path, class_map)
    boxes.sort(key=lambda b: b["x"])
    return "".join([box["char"] for box in boxes])

def recognize_all_cells(image_path):
    # 1. Hücre klasörünü temizle
    for f in glob.glob("foundcells/*.png"):
        os.remove(f)

    # 2. Hücreleri kes
    process_image(image_path, image_index=1)

    # 3. Sınıf haritasını yükle
    class_map = load_class_map("classes.txt")

    # 4. Modeli yükle (bir kere yükle, reuse edebilirsin)
    model = YOLO("runs/detect/train6/weights/best.pt")

    # 5. Foundcells klasöründen tüm görüntüleri oku ve belleğe yükle
    foundcells_dir = "foundcells"
    image_files = sorted([
        os.path.join(foundcells_dir, f) for f in os.listdir(foundcells_dir)
        if f.endswith(".png")
    ])

    # 6. Tüm resimleri belleğe yükle
    image_data = [np.array(Image.open(img_path).convert("RGB")) for img_path in image_files]

    # 7. Modelle tahmin et (toplu)
    results = model.predict(source=image_data, conf=0.25, save=False, verbose=False)

    predictions = []
    for result in results:
        boxes = []
        for box in result.boxes:
            cls_id = int(box.cls[0])
            x_center = float(box.xywh[0][0])
            boxes.append({
                "char": class_map[cls_id],
                "x": x_center
            })
        if not boxes:
            predictions.append("")
        else:
            boxes.sort(key=lambda b: b["x"])
            pred = "".join([b["char"] for b in boxes])
            predictions.append(pred)

    return {
        "moves": predictions
    }

if __name__ == "__main__":
    image_path = "games/test1.jfif"
    result = recognize_all_cells(image_path)

    print("hamleler:")
    print(result["moves"])

    # print("Siyah hamleler:")
    # print(result["black"])

    # # API'ye string olarak göndermek için JSON'a çevir
    # json_string = json.dumps(result, ensure_ascii=False)
    # print("\nJSON çıktısı:")
    # print(json_string)