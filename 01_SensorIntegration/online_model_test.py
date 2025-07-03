import os
import time
import cv2
import torch
from pathlib import Path
from utils.datasets import LoadImages
from utils.general import check_img_size, scale_coords, non_max_suppression
from utils.plots import plot_one_box
from utils.torch_utils import select_device
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Class to handle new files in the directory
class FileHandler(FileSystemEventHandler):
    def __init__(self, model, device, imgsz, source, save_dir):
        self.model = model
        self.device = device
        self.imgsz = imgsz
        self.source = source
        self.save_dir = save_dir

    def on_created(self, event):
        if event.is_directory:
            return

        # When a new file is created, run detection
        self.process_file(event.src_path)

    def process_file(self, file_path):
        # Process the new image file
        print(f"Processing file: {file_path}")
        img = cv2.imread(file_path)

        # Resize image and process it with the model
        img = cv2.resize(img, (self.imgsz, self.imgsz))
        img = torch.from_numpy(img).to(self.device).float()  # Convert image to tensor
        img /= 255.0  # Normalize

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        with torch.no_grad():
            pred = self.model(img)[0]

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

        # Process detections
        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img.shape).round()

                # Plot results on the image
                for *xyxy, conf, cls in reversed(det):
                    label = f'{self.model.names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, img, label=label)

        # Save the output image
        save_path = str(self.save_dir / Path(file_path).name)
        cv2.imwrite(save_path, img)
        print(f"Saved result to {save_path}")


def continuous_detection(model, device, imgsz, source, save_dir):
    event_handler = FileHandler(model, device, imgsz, source, save_dir)
    observer = Observer()
    observer.schedule(event_handler, source, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Keeps the observer running
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    # Setup parameters
    weights = '/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/yolov7/runs/train/exp7/weights/best.pt'
    source = '/home/dartagnan-dev/sahil-dev/Sensor_integration/py_mmwave_dev/py_mmwave_read/range-azimuth-2D-Histogram/frame_0000.jpg'
    save_dir = Path('/home/dartagnan-dev/sahil-dev/Sensor_integration/py_mmwave_dev/py_mmwave_read/detection')
    save_dir.mkdir(parents=True, exist_ok=True)

    # Initialize model and device
    device = select_device('')
    model = torch.load(weights, map_location=device)['model'].float().eval()

    # Set image size
    imgsz = 640
    imgsz = check_img_size(imgsz)

    # Start continuous detection
    continuous_detection(model, device, imgsz, source, save_dir)
