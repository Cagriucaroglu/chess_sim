import cv2
import numpy as np
import os
import shutil

image_folder = "games"
output_folder = "foundcells"
os.makedirs(output_folder, exist_ok=True)

def detect_lines(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Hata: {image_path} okunamadı.")
        return [], []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 75, minLineLength=75, maxLineGap=3)
    vertical_lines, horizontal_lines = [], []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) < 10:
                vertical_lines.append((x1, x2))
            elif abs(y1 - y2) < 10:
                horizontal_lines.append((y1, y2))

    vertical_lines.sort(key=lambda x: x[0])              # soldan sağa
    horizontal_lines.sort(key=lambda y: y[0], reverse=False)  # yukarıdan aşağıya

    return vertical_lines, horizontal_lines

def group_lines(lines, axis_index, threshold=30):
    grouped = []
    group = []

    for line in lines:
        val = line[axis_index]
        if not group:
            group.append(line)
        else:
            prev_val = group[-1][axis_index]
            if abs(val - prev_val) <= threshold:
                group.append(line)
            else:
                avg = tuple(int(np.mean([g[i] for g in group])) for i in range(2))
                grouped.append(avg)
                group = [line]

    if group:
        avg = tuple(int(np.mean([g[i] for g in group])) for i in range(2))
        grouped.append(avg)

    return grouped

def process_image(image_path, image_index, cell_start_index=1):
    img = cv2.imread(image_path)
    filename = os.path.basename(image_path)
    name, _ = os.path.splitext(filename)
    vertical_lines, horizontal_lines = detect_lines(image_path)
    # vertical_lines = [v for v in vertical_lines if 290 < v[0] < 3000]
    # horizontal_lines = [h for h in horizontal_lines if h[0] > 1180] 
    vertical_lines = [v for v in vertical_lines if 130 < v[0] < 2850]
    horizontal_lines = [h for h in horizontal_lines if h[0] > 830] 

    vertical_lines = group_lines(vertical_lines, 0)
    horizontal_lines = group_lines(horizontal_lines, 0)
    half = (len(vertical_lines) - 1) // 2  # Tamsayı bölme

    cell_count = cell_start_index
    with open("labels.txt", "a", encoding="utf-8") as label_file:
        # 📌 Doğru sırayla: önce yatay (satır), sonra dikey (sütun)
        # İlk yarı sütunlar
        for i in range(len(horizontal_lines) - 1):  # SATIR
            for j in range(half):  # SÜTUN (ilk yarı)
                cell_count = process_cell(img, horizontal_lines, vertical_lines, i, j, name, output_folder, cell_count, label_file)

        # İkinci yarı sütunlar
        for i in range(len(horizontal_lines) - 1):  # SATIR
            for j in range(half, len(vertical_lines) - 1):  # SÜTUN (ikinci yarı)
                cell_count = process_cell(img, horizontal_lines, vertical_lines, i, j, name, output_folder, cell_count, label_file)


        if cell_count != 81 and cell_count != 85:
            label_file.write(f"{name} sıkıntılı\n")

def process_cell(img, horizontal_lines, vertical_lines, i, j, name, output_folder, cell_count, label_file):
    try:
        y1 = int(horizontal_lines[i][0])
        y2 = int(horizontal_lines[i + 1][0])
        x1 = int(vertical_lines[j][0])
        x2 = int(vertical_lines[j + 1][0])
    except IndexError:
        print(f"❌ Satır/Sütun hatası: i={i}, j={j}")
        return cell_count

    if x2 - x1 < 150:
        return cell_count

    cell_img = img[y1:y2, x1:x2]
    cell_filename = f"{output_folder}/{name}_cell{cell_count}.png"
    label_file.write(f"{cell_filename}\n")
    cv2.imwrite(cell_filename, cell_img)
    print(f"{cell_filename} kaydedildi!")
    return cell_count + 1

def draw_lines_on_image(image_path, vertical_lines, horizontal_lines):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Hata: {image_path} okunamadı.")
        return

    for x1, x2 in vertical_lines:
        cv2.line(image, (x1, 0), (x2, image.shape[0]), (0, 255, 0), 2)

    for y1, y2 in horizontal_lines:
        cv2.line(image, (0, y1), (image.shape[1], y2), (255, 0, 0), 2)

    name, _ = os.path.splitext(os.path.basename(image_path))
    output_path = os.path.join(os.path.dirname(image_path), f"{name}_isaretli.jpg")
    cv2.imwrite(output_path, image)
    print(f"Çizgili görsel kaydedildi: {output_path}")

def main():
    image_path = "games/Image (27).jpg"
    result = recognize_all_cells(image_path)
    import json
    print("JSON çıktısı:")
    print(json.dumps(result, indent=2))

# if _name_ == "_main_":
#     main()