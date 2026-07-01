# src/yolo_detect.py
import os
import csv
from ultralytics import YOLO
from utils import get_logger

logger = get_logger("YOLODetector")

def classify_image(detected_objects):
    """
    Business logic rules mapping based on detected items:
    - promotional: contains a person AND a product asset (bottle/cup/container)
    - product_display: contains a product asset, NO person
    - lifestyle: contains a person, NO product asset
    - other: fallback general categorization
    """
    has_person = 'person' in detected_objects
    has_product = any(obj in detected_objects for obj in ['bottle', 'cup', 'vase', 'bowl', 'box'])

    if has_person and has_product:
        return 'promotional'
    elif has_product and not has_person:
        return 'product_display'
    elif has_person and not has_product:
        return 'lifestyle'
    return 'other'

def run_object_detection():
    # Load hyper-efficient YOLOv8 Nano weights
    logger.info("Initializing YOLOv8n network...")
    model = YOLO("yolov8n.pt") 

    image_root = "data/raw/images"
    output_csv = "data/yolo_detections.csv"

    if not os.path.exists(image_root):
        logger.error(f"Image directory path missing: {image_root}")
        return

    # Set up CSV logging structure
    csv_headers = ["message_id", "channel_name", "detected_class", "confidence_score", "image_category"]
    records = []

    # Iterating through channel directories inside our data lake
    for channel_name in os.listdir(image_root):
        channel_path = os.path.join(image_root, channel_name)
        if not os.path.isdir(channel_path):
            continue

        logger.info(f"Scanning media assets inside channel: {channel_name}")
        for img_file in os.listdir(channel_path):
            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            img_path = os.path.join(channel_path, img_file)
            # Pull original message id directly out of image file name matching pattern
            message_id = os.path.splitext(img_file)[0]

            try:
                # Execute inferencing step
                results = model(img_path, verbose=False)[0]
                
                detected_names = []
                highest_conf = 0.0
                primary_class = "none"

                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf = float(box.conf[0])
                    detected_names.append(label)
                    
                    if conf > highest_conf:
                        highest_conf = conf
                        primary_class = label

                img_category = classify_image(detected_names)
                
                records.append([
                    message_id,
                    channel_name,
                    primary_class,
                    round(highest_conf, 4),
                    img_category
                ])

            except Exception as e:
                logger.error(f"Failed processing matrix for {img_file}: {str(e)}")

    # Flush all analytical results directly to CSV storage
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(records)

    logger.info(f"Object tracking complete! Output recorded securely to {output_csv}")

if __name__ == "__main__":
    run_object_detection()