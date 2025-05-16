from paddleocr import PaddleOCR
from ultralytics import YOLO
import cv2 
import os 
import re
import csv

model_detection = YOLO("yolo11n.pt")
model_ocr = PaddleOCR(use_angle_cls=True, lang='en')

def get_person(image_path):
    detection_results = model_detection(image_path)
    detection_result = detection_results[0]
    origin_img = detection_result.orig_img
    boxes = detection_result.boxes
    names = detection_result.names 

    person_crops = []

    for i, box in enumerate(boxes):
        cls_id = int(box.cls[0])
        cls_name = names[cls_id]

        if cls_name == "person":
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = origin_img[y1:y2, x1:x2]
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            person_crops.append(crop_rgb)
    
    return person_crops

def get_bib_number(person_crops):
    ocr_results = []
    for crop in person_crops:
        result = model_ocr.ocr(crop, cls=True)
        ocr_results.append(result)

    bib_numbers = []
    for i in range(len(ocr_results)):
        if not ocr_results[i] or not ocr_results[i][0]:
            continue
        for j in range(len(ocr_results[i][0])):
            text = ocr_results[i][0][j][1][0]
            bib_numbers.append(text.strip())
    return bib_numbers

if __name__ == "__main__":
    folder_path = "./downloaded_images"
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    csv_path = "bib_numbers.csv"
    total_images = len(image_paths)
    written_count = 0

    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["image_name", "bib_numbers"])  

        for image_path in image_paths:
            image_name = os.path.basename(image_path)
            person_crops = get_person(image_path)
            bib_numbers = get_bib_number(person_crops)

            if not bib_numbers:
                print(f"\033[91mCannot find bib_number from: {image_name}\033[0m")
                writer.writerow([image_name, ""])
            else:
                bib_string = "|".join(bib_numbers)
                writer.writerow([image_name, bib_string])
                print(f"\033[92mExtracted from: {image_name} → {bib_string}\033[0m")
                written_count += 1

    print(f"\n Saved {written_count} rows / {total_images} images to {csv_path}")
