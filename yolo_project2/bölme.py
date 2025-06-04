import os
import shutil
import random

image_dir = r"C:\Users\sbile\Downloads\gamesforlabeling\gamesforlabeling"
output_dir = r"D:\project\chess_sim\yolo_project2\dataset"

# Yol yapılarını oluştur
os.makedirs(os.path.join(output_dir, 'images/train'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'images/val'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'labels/train'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'labels/val'), exist_ok=True)

images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
random.shuffle(images)

split_idx = int(len(images) * 0.8)  # %80 train
train_images = images[:split_idx]
val_images = images[split_idx:]

for img_set, set_name in [(train_images, 'train'), (val_images, 'val')]:
    for img_name in img_set:
        txt_name = img_name.replace('.jpg', '.txt')
        shutil.copy(os.path.join(image_dir, img_name), os.path.join(output_dir, f'images/{set_name}', img_name))
        shutil.copy(os.path.join(image_dir, txt_name), os.path.join(output_dir, f'labels/{set_name}', txt_name))

print("Veri başarıyla train/val olarak bölündü.")
