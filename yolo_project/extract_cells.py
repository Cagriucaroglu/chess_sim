from ultralytics import YOLO
import cv2
import os
import numpy as np

# ✅ Model yolları
cell_model = YOLO(r"D:\project\chess_sim\yolo_project2\runs\detect\train\weights\best.pt")
char_model = YOLO(r"D:\project\chess_sim\yolo_project\runs\detect\train6\weights\best.pt")  # karakter tanıyıcı

image_path = r"D:\project\chess_sim\yolo_project2\dataset\images\val\Image (9).jpg"
output_dir = "processed_cells"
os.makedirs(output_dir, exist_ok=True)

# 📦 Hücre tahmini
results = cell_model(image_path, conf=0.2, imgsz=1280)[0]
boxes = results.boxes.xyxy.cpu().numpy()

# ✅ Skor kağıdı sıralama fonksiyonu
def sort_score_sheet_boxes(boxes):
    x_coords = [box[0] for box in boxes]
    x_thresh = min(x_coords) + (max(x_coords) - min(x_coords)) * 0.5
    left_col = [box for box in boxes if box[0] <= x_thresh]
    right_col = [box for box in boxes if box[0] > x_thresh]
    left_sorted = sorted(left_col, key=lambda b: b[1])
    right_sorted = sorted(right_col, key=lambda b: b[1])
    return left_sorted + right_sorted

boxes = sort_score_sheet_boxes(boxes)

# 📐 Görüntü işleme ayarları
img = cv2.imread(image_path)
h, w, _ = img.shape
print("Orijinal görüntü boyutu:", img.shape)
target_width, target_height = 516, 128

for i, box in enumerate(boxes):
    x1, y1, x2, y2 = map(int, box)
    margin_ratio = 0.15
    box_w, box_h = x2 - x1, y2 - y1
    x1m = max(0, int(x1 - margin_ratio * box_w))
    y1m = max(0, int(y1 - margin_ratio * box_h))
    x2m = min(w, int(x2 + margin_ratio * box_w))
    y2m = min(h, int(y2 + margin_ratio * box_h))
    cropped = img[y1m:y2m, x1m:x2m]

    # 🔍 Görüntü işleme
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
    processed = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    # 📏 Yeniden boyutlandır ve padding ile ortala
    h_ratio = target_height / processed.shape[0]
    w_ratio = target_width / processed.shape[1]
    resize_ratio = min(h_ratio, w_ratio)
    new_size = (int(processed.shape[1] * resize_ratio), int(processed.shape[0] * resize_ratio))
    resized = cv2.resize(processed, new_size)
    padded = np.full((target_height, target_width, 3), 255, dtype=np.uint8)
    x_offset = (target_width - resized.shape[1]) // 2
    y_offset = (target_height - resized.shape[0]) // 2
    padded[y_offset:y_offset + resized.shape[0], x_offset:x_offset + resized.shape[1]] = resized

    filename = f"{output_dir}/cell_{i+1:03d}.jpg"
    cv2.imwrite(filename, padded)

print(f"{len(boxes)} hücre başarıyla kaydedildi.")

# 🧠 Karakter tahmini
predict_results = char_model.predict(source=output_dir, save=False, save_txt=False, conf=0.2)
recognized_cells = []
for result in predict_results:
    chars = result.names
    boxes = result.boxes
    if boxes is None or boxes.data.shape[0] == 0:
        recognized_cells.append("❌")
        continue
    xyxy = boxes.xyxy.cpu().numpy()
    cls_ids = boxes.cls.cpu().numpy().astype(int)
    sorted_chars = [x for _, x in sorted(zip(xyxy[:, 0], cls_ids))]
    label_str = ''.join([chars[i] for i in sorted_chars])
    recognized_cells.append(label_str)

# 📝 Sıralı çıktı
print("\n♟️ Sıralı Hamleler:")
for i in range(0, len(recognized_cells), 2):
    move_num = (i // 2) + 1
    white = recognized_cells[i]
    black = recognized_cells[i+1] if i+1 < len(recognized_cells) else ""
    print(f"{move_num:2d}. {white:<6} {black}")
