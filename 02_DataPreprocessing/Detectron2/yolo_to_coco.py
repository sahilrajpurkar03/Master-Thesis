import os
import json
from PIL import Image

# Define paths
yolo_base_dir = "E:/your/path/to/Detectron2_test"
image_dirs = {"train": "train", "test": "test", "val": "val"}
label_dirs = {"train": "train", "test": "test", "val": "val"}

# Classes
class_names = ["Forklift+KLT", "Robotnik", "Forklift", "Workstation"]

# Function to process a dataset and generate COCO annotations
def generate_coco_annotations(image_dir, label_dir, output_file):
    coco_data = {"images": [], "annotations": [], "categories": []}
    for idx, class_name in enumerate(class_names):
        coco_data["categories"].append({"id": idx + 1, "name": class_name})

    annotation_id = 1
    for label_file in os.listdir(label_dir):
        if not label_file.endswith(".txt"):
            continue

        # Load corresponding image
        image_name = label_file.replace(".txt", ".jpg")
        image_file = os.path.join(image_dir, image_name)
        img = Image.open(image_file)
        width, height = img.size

        # Add image info to COCO
        image_id = len(coco_data["images"])
        coco_data["images"].append({
            "id": image_id,
            "file_name": image_name,
            "width": width,
            "height": height
        })

        # Parse YOLO labels
        label_file_path = os.path.join(label_dir, label_file)
        with open(label_file_path, "r") as f:
            for line in f.readlines():
                class_id, x_center, y_center, box_width, box_height = map(float, line.strip().split())
                class_id = int(class_id)

                # Convert to COCO format (un-normalize coordinates)
                x = (x_center - box_width / 2) * width
                y = (y_center - box_height / 2) * height
                box_width *= width
                box_height *= height
                area = box_width * box_height

                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": class_id + 1,
                    "bbox": [x, y, box_width, box_height],
                    "area": area,
                    "iscrowd": 0
                })
                annotation_id += 1

    # Save COCO format JSON
    with open(output_file, "w") as json_file:
        json.dump(coco_data, json_file, indent=4)

# Generate separate annotation files for train, test, val
for dataset_type in ["train", "test", "val"]:
    image_dir = os.path.join(yolo_base_dir, "images", image_dirs[dataset_type])
    label_dir = os.path.join(yolo_base_dir, "labels", label_dirs[dataset_type])
    output_file = f"{dataset_type}.json"

    print(f"Processing {dataset_type} dataset...")
    generate_coco_annotations(image_dir, label_dir, output_file)
    print(f"Saved {dataset_type} annotations to {output_file}")
