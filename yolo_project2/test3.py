import subprocess
import os
import cv2
import shutil

threshold = 40  # piksel cinsinden satır yüksekliği eşiği

def sort_table_by_rows(table, threshold):
    # 1) Önce Dikey (Y) olarak sırala
    table_sorted = sorted(table, key=lambda d: d['yc'])
    rows = []  # her satır bir liste olacak

    # 2) Satır gruplarını oluştur
    for d in table_sorted:
        if not rows:
            # ilk hücreyi ilk satıra ekle
            rows.append([d])
        else:
            # son satırın temsilcisi olarak ilk hücrenin yc'sini al
            last_row = rows[-1]
            lastrow_y = last_row[0]['yc']
            if abs(d['yc'] - lastrow_y) < threshold:
                # halen aynı satırda say, ekle
                last_row.append(d)
            else:
                # yeni satır başlat
                rows.append([d])

    # 3) Her satırı X'e göre sırala (soldan sağa)
    for row in rows:
        row.sort(key=lambda d: d['xc'])

    # 4) Satırları düz listeye çevir
    return [d for row in rows for d in row]

def recognize_all_cells(image_folder):
    # — YOLO’yu çalıştırıp labels klasörünü alıyoruz —
    run_name = "batch_predict"
    output_dir = os.path.join("runs", "detect", run_name)
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    image_file = next((f for f in os.listdir(image_folder)
                       if f.lower().endswith((".jpg", ".png", ".jpeg"))), None)
    if image_file is None:
        print("Resim bulunamadı.")
        return

    image_path = os.path.join(image_folder, image_file)
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    subprocess.run([
        "yolo", "task=detect", "mode=predict",
        "model=runs/detect/train/weights/best.pt",
        f"source={image_path}",
        "save_txt=True",
        "project=runs/detect",
        f"name={run_name}",
        "exist_ok=True",
        "conf=0.25"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    labels_dir = os.path.join("runs", "detect", run_name, "labels")

    txt_path = os.path.join(labels_dir, sorted(os.listdir(labels_dir))[0])
    lines = open(txt_path).read().strip().splitlines()

    # — Tüm detection’ları listeye alalım —
    dets = []
    for line in lines:
        class_id, x_c, y_c, bw, bh = map(float, line.split())
        # pixel olarak da tutuyorum
        xc, yc = x_c * w, y_c * h
        bwp, bhp = bw * w, bh * h
        x1 = int(xc - bwp/2); y1 = int(yc - bhp/2)
        x2 = int(xc + bwp/2); y2 = int(yc + bhp/2)
        dets.append({
            "xc": xc, "yc": yc,
            "box": (x1, y1, x2, y2)
        })


    # 5) Tabloları ayır
    left_table  = [d for d in dets if d['xc'] < 0.5*w]
    right_table = [d for d in dets if d['xc'] >= 0.5*w]
    ordered = sort_table_by_rows(left_table, threshold) + \
          sort_table_by_rows(right_table, threshold)
    # — Kayıt ederken index’e göre isim verelim —
        # — Mevcut klasörü baştan temizle —
    outputcells = "foundcells"
    if os.path.exists(outputcells):
        shutil.rmtree(outputcells)
    os.makedirs(outputcells, exist_ok=True)
    
    for idx, d in enumerate(ordered, start=1):
        x1,y1,x2,y2 = d["box"]
        x1 = x1 - 50
        x2 = x2 + 50
        y1 = y1 - 10
        y2 = y2 + 10
        crop = img[y1:y2, x1:x2]
        cv2.imwrite(f"foundcells/crop_{idx:03d}.jpg", crop)
    


if __name__ == "__main__":
    recognize_all_cells("testimages")
