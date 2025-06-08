import subprocess
import os
import cv2
import shutil

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

    # — Sütunları ayırmak için normalize x_c kullanabiliriz —
    #    Burada x_c zaten [0,1] arasındaydı, eğer piksel ise xc<w/2 diyebilirsin.
    #    Küçük olanlar -> soldaki tablo, büyük olanlar -> sağdaki tablo.
    #    Ardından (tablo_index, yc, xc) ile sıralıyoruz.
    ordered = sorted(
        dets,
        key=lambda d: (
            0 if d["xc"] < 0.5*w else 1,  # soldaki tablo önce
            d["yc"],                      # yukarıdan aşağı
            d["xc"]                       # satır içi: önce beyaz sonra siyah
        )
    )

    # — Kayıt ederken index’e göre isim verelim —
        # — Mevcut klasörü baştan temizle —
    outputcells = "foundcells"
    if os.path.exists(outputcells):
        shutil.rmtree(outputcells)
    os.makedirs(outputcells, exist_ok=True)
    
    for idx, d in enumerate(ordered, start=1):
        x1,y1,x2,y2 = d["box"]
        crop = img[y1:y2, x1:x2]
        cv2.imwrite(f"foundcells/crop_{idx:03d}.jpg", crop)

if __name__ == "__main__":
    recognize_all_cells("testimages")
