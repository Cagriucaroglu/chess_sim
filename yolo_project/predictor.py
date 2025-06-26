import os
import subprocess
import shutil
import glob
import json
from movedetect import process_image_v2  # main2.py aynı klasörde olmalı
import re
import uuid

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

def extract_number(filename):
    match = re.search(r"_cell(\d+)\.txt$", filename)
    return int(match.group(1)) if match else -1


def recognize_all_cells(image_path):
    import glob
    for f in glob.glob("foundcells/*.png"):
        os.remove(f)
    # 2. Hücreleri kes
    foundcells_dir = process_image_v2(image_path)

    # 3. Sınıf isimlerini yükle
    class_map = load_class_map("classes.txt")

    run_name = f"batch_predict{uuid.uuid4()}{uuid.uuid4()}"
    output_dir = os.path.join("runs", "detect", run_name)

    predictions = []

    # subprocess ile toplu predict
    subprocess.run([
        "yolo",
        "task=detect",
        "mode=predict",
        "model=runs/detect/train6/weights/best.pt",
        f"source={foundcells_dir}",
        "save_txt=True",
        f"project=runs/detect",
        f"name={run_name}",
        "exist_ok=True",
        "conf=0.25"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    labels_dir = os.path.join(output_dir, "labels")
    
    txt_files = sorted(os.listdir(labels_dir), key=extract_number)
    for txt_file in txt_files:
        if not txt_file.endswith(".txt"):
            continue
        full_txt_path = os.path.join(labels_dir, txt_file)
        boxes = parse_prediction_txt(full_txt_path, class_map)
        if not boxes:
            # Eğer bu hücrede hiç karakter yakalanmadıysa, "" döner
            predictions.append("")
        else:
            # x konumuna göre sıraladıktan sonra karakterleri birleştir
            boxes.sort(key=lambda b: b["x"])
            preds = "".join([b["char"] for b in boxes])
            predictions.append(preds)
    # for file in sorted(os.listdir(foundcells_dir)):
    #     if file.endswith(".png"):
    #         full_path = os.path.join(foundcells_dir, file)
    #         prediction = recognize_character_from_image(
    #             image_path=full_path,
    #             model_path="runs/detect/train6/weights/best.pt",
    #             class_map=class_map
    #         )
    #         if prediction.strip():
    #             predictions.append(prediction
        # 4. İşlem bittikten sonra klasörü sil

    # 5. API için JSON olarak döndür
    result_json = {
        "moves": predictions
    }
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    if os.path.exists(foundcells_dir):
        shutil.rmtree(foundcells_dir)

    return result_json

if __name__ == "__main__":
    image_path = "gamesfortest/temp.jpg"
    result = recognize_all_cells(image_path)

    print("hamleler:")
    print(result["moves"])

    # print("Siyah hamleler:")
    # print(result["black"])

    # # API'ye string olarak göndermek için JSON'a çevir
    # json_string = json.dumps(result, ensure_ascii=False)
    # print("\nJSON çıktısı:")
    # print(json_string)