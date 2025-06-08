from ultralytics import YOLO
import cv2
import os
import numpy as np

# ✅ Model yolları
cell_model = YOLO(r"D:\projects\chess-sim\yolo_project2\runs\detect\train\weights\best.pt")
char_model = YOLO(r"D:\projects\chess-sim\yolo_project\runs\detect\train6\weights\best.pt")  # karakter tanıyıcı

image_path = r"D:\DERS\Bitirme\Hücre Çıkartma\games\test3.png"
output_dir = "processed_cells"
os.makedirs(output_dir, exist_ok=True)

# 📦 Hücre tahmini
results = cell_model(image_path, conf=0.2, imgsz=1280)[0]
boxes = results.boxes.xyxy.cpu().numpy()

def stabilize_sort_by_y_then_x(lst, y_thresh=25):
    """
    lst: list of [x1, y1, x2, y2]
    y_thresh: aynı satır sayılacak y1 fark eşiği (piksel)
    """
    lst = lst.copy()
    i = 0
    while i < len(lst) - 1:
        x0, y0 = lst[i][0], lst[i][1]
        x1, y1 = lst[i+1][0], lst[i+1][1]
        # eğer y farkı küçükse ve soldaki kutu sağdakinden daha sağdaysa takas et
        if abs(y0 - y1) < y_thresh and x0 > x1:
            lst[i], lst[i+1] = lst[i+1], lst[i]
            i = max(i-1, 0)  # bir adım geri dön, tekrar kontrol et
        else:
            i += 1
    return lst

# ✅ Skor kağıdı sıralama fonksiyonu
def sort_score_sheet_boxes(boxes, y_thresh=25):
    x_coords = [box[0] for box in boxes]
    x_thresh = min(x_coords) + ((max(x_coords) - min(x_coords)) * 0.5)
    left_cols = [box for box in boxes if box[0] <= x_thresh]
    right_cols = [box for box in boxes if box[0] > x_thresh]
    left_sorted = sorted(left_cols, key=lambda b: b[1])
    right_sorted = sorted(right_cols, key=lambda b: b[1])
    left_sorted = stabilize_sort_by_y_then_x(left_sorted)
    right_sorted = stabilize_sort_by_y_then_x(right_sorted)

    return left_sorted , right_sorted

boxes1 , boxes2 = sort_score_sheet_boxes(boxes , y_thresh=25)

# 📐 Görüntü işleme ayarları
img = cv2.imread(image_path)
h, w, _ = img.shape
print("Orijinal görüntü boyutu:", img.shape)
target_width, target_height = 516, 128

def cropimage(boxes):
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


cropimage(boxes1)
cropimage(boxes2)
# # 🧠 Karakter tahmini
# predict_results = char_model.predict(source=output_dir, save=False, save_txt=False, conf=0.2)
# recognized_cells = []
# for result in predict_results:
#     chars = result.names
#     boxes = result.boxes
#     if boxes is None or boxes.data.shape[0] == 0:
#         recognized_cells.append("❌")
#         continue
#     xyxy = boxes.xyxy.cpu().numpy()
#     cls_ids = boxes.cls.cpu().numpy().astype(int)
#     sorted_chars = [x for _, x in sorted(zip(xyxy[:, 0], cls_ids))]
#     label_str = ''.join([chars[i] for i in sorted_chars])
#     recognized_cells.append(label_str)

# # 📝 Sıralı çıktı
# print("\n♟️ Sıralı Hamleler:")
# for i in range(0, len(recognized_cells), 2):
#     move_num = (i // 2) + 1
#     white = recognized_cells[i]
#     black = recognized_cells[i+1] if i+1 < len(recognized_cells) else ""
#     print(f"{move_num:2d}. {white:<6} {black}")
