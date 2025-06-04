import os

folder_path = r"C:\Users\sbile\Downloads\gamesforlabeling\gamesforlabeling"  # Buraya yolunu yaz (örneğin: "labels/")

for filename in os.listdir(folder_path):
    if filename.endswith(".txt") and filename != "classes.txt":
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            parts[0] = '0'  # class id'yi 0 yap
            new_lines.append(" ".join(parts) + "\n")
        
        with open(file_path, "w") as file:
            file.writelines(new_lines)

print("Tüm class id'ler 0 olarak güncellendi.")
