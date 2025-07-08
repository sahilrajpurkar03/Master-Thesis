import os

TRAIN_IMG_PATH = r"/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/images/train"
VAL_IMG_PATH = r"/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/images/val"
TEST_IMG_PATH = r"/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/images/test"

def save_image_paths_to_file(image_dir, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            for img_name in os.listdir(image_dir):
                img_path = os.path.join(image_dir, img_name)
                file.write(img_path + '\n')
        print(f"Image paths saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Save training and validation image paths
save_image_paths_to_file(TRAIN_IMG_PATH, '/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/train.txt')
save_image_paths_to_file(VAL_IMG_PATH, '/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/val.txt')
save_image_paths_to_file(TEST_IMG_PATH, '/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/test.txt' )
