from ultralytics import YOLO
import cv2
import os
import numpy as np

# ✅ Eğittiğin modeli yükle
model = YOLO(r"D:\projects\chess-sim\yolo_project2\runs\detect\train\weights\best.pt")

# ✅ Girdi görüntüsü ve çıktı klasörü
image_path = r"D:\DERS\Bitirme\Hücre Çıkartma\games\test3.png"
output_dir = "processed_cells"
os.makedirs(output_dir, exist_ok=True)

# 📦 Tahmin yap
results = model(image_path, conf=0.2, imgsz=1280)[0]
boxes = results.boxes.xyxy.cpu().numpy()

# 🔢 Bbox sıralama (satır satır, soldan sağa)
def sort_boxes(boxes):
    return sorted(boxes, key=lambda box: (int(box[1] // 100), box[0]))

boxes = sort_boxes(boxes)
img = cv2.imread(image_path)
h, w, _ = img.shape
print("Orijinal görüntü boyutu:", img.shape)

# 📐 Hedef boyut
target_width = 516
target_height = 128

for i, box in enumerate(boxes):
    x1, y1, x2, y2 = map(int, box)
    margin_ratio = 0.15
    box_w, box_h = x2 - x1, y2 - y1

    # 🔲 Genişletilmiş koordinatlar
    x1m = max(0, int(x1 - margin_ratio * box_w))
    y1m = max(0, int(y1 - margin_ratio * box_h))
    x2m = min(w, int(x2 + margin_ratio * box_w))
    y2m = min(h, int(y2 + margin_ratio * box_h))

    cropped = img[y1m:y2m, x1m:x2m]

    # 🎯 Görüntü işleme: griye çevir + keskinleştir
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
    processed = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    # 📏 Oranı koruyarak yeniden boyutlandır
    h_ratio = target_height / processed.shape[0]
    w_ratio = target_width / processed.shape[1]
    resize_ratio = min(h_ratio, w_ratio)
    new_size = (int(processed.shape[1] * resize_ratio), int(processed.shape[0] * resize_ratio))
    resized = cv2.resize(processed, new_size)

    # 🧱 Padding ile sabit boyuta getir
    padded = np.full((target_height, target_width, 3), 255, dtype=np.uint8)
    x_offset = (target_width - resized.shape[1]) // 2
    y_offset = (target_height - resized.shape[0]) // 2
    padded[y_offset:y_offset + resized.shape[0], x_offset:x_offset + resized.shape[1]] = resized

    filename = f"{output_dir}/cell_{i+1:03d}.jpg"
    cv2.imwrite(filename, padded)

print(f"{len(boxes)} hücre başarıyla kaydedildi.")