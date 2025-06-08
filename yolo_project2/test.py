import subprocess
import os
import cv2

def recognize_all_cells(image_folder):
    output_dir = os.path.join("runs/detect")
    run_name = f"batch_predict"
      # Klasördeki ilk resmi bul
    all_files = os.listdir(image_folder)
    image_file = next((f for f in all_files if f.lower().endswith(('.jpg', '.png', '.jpeg'))), None)
    if image_file is None:
        print("Resim bulunamadı.")
        return

    image_path = os.path.join(image_folder, image_file)
    img = cv2.imread(image_path)
    h, w, _ = img.shape

    subprocess.run([
        "yolo",
        "task=detect",
        "mode=predict",
        "model=runs/detect/train/weights/best.pt",
        f"source={image_path}",
        "save_txt=True",
        f"project=runs/detect",
        f"name={run_name}",
        "exist_ok=True",
        "conf=0.25"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    labels_dir = os.path.join("runs", "detect", run_name, "labels")
    txt_files = sorted(os.listdir(labels_dir))
    for txt_file in txt_files:
        if not txt_file.endswith(".txt"):
           continue
        full_txt_path = os.path.join(labels_dir, txt_file)    
    # Etiketleri oku
        with open(full_txt_path, "r") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            parts = line.strip().split()
            class_id, x_c, y_c, bw, bh = map(float, parts)

            # Normalize koordinatları piksele çevir
            xc = x_c * w
            yc = y_c * h
            bw = bw * w
            bh = bh * h
            # <class_id> <x_center> <y_center> <width> <height>

            # Sol üst ve sağ alt köşeleri hesapla
            x1 = int(xc - bw / 2)
            y1 = int(yc - bh / 2)
            x2 = int(xc + bw / 2)
            y2 = int(yc + bh / 2)

            # Görselin dışına taşma olmasın
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            # Kırp
            cropped = img[y1:y2, x1:x2]

            # Kaydet
            os.makedirs("foundcells", exist_ok=True)
            out_path = os.path.join("foundcells", f"crop_{i+1:03d}.jpg")
            cv2.imwrite(out_path, cropped)
if __name__ == "__main__":
    image_path = "games/test1.jfif"
    result = recognize_all_cells("testimages")
