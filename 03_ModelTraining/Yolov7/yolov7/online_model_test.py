import os
import cv2
import time
from pathlib import Path
import torch
from numpy import random
from utils.datasets import LoadImages
from utils.general import non_max_suppression, scale_coords, check_img_size
from utils.plots import plot_one_box
from models.experimental import attempt_load
from utils.torch_utils import select_device, time_synchronized
import logging  # Import logging module

start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"detection_log_{start_time}.txt"

# Configure logging
logging.basicConfig(
    filename=log_filename,  # Log file name
    level=logging.INFO,  # Logging level
    format="%(asctime)s - %(message)s",  # Log message format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)
logger = logging.getLogger()


class YOLOv7Detector:
    def __init__(self, weights, img_size=640, conf_thres=0.25, iou_thres=0.45, device='', classes=None, agnostic_nms=False):
        self.device = select_device(device)
        self.model = attempt_load(weights, map_location=self.device)  # Load model
        self.img_size = check_img_size(img_size, s=int(self.model.stride.max()))  # Check image size
        self.half = self.device.type != 'cpu'  # Use FP16 if on CUDA
        if self.half:
            self.model.half()
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.classes = classes
        self.agnostic_nms = agnostic_nms

        # Run a dummy inference to warm up the model (important for GPUs)
        self.model(torch.zeros(1, 3, self.img_size, self.img_size).to(self.device).type_as(next(self.model.parameters())))

    def detect(self, image_path, save_dir, save_img=True):
        dataset = LoadImages(image_path, img_size=self.img_size)
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        for path, img, im0s, vid_cap in dataset:
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.half else img.float()  # Convert to FP16 or FP32
            img /= 255.0  # Normalize to 0-1 range
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            with torch.no_grad():
                pred = self.model(img, augment=False)[0]
            t2 = time_synchronized()

            # Apply NMS
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic_nms)
            t3 = time_synchronized()

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                p = Path(path)  # Image path
                save_path = str(save_dir / p.name)  # Save path
                s = ''

                if len(det):
                    # Rescale boxes to original image size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()

                    # Draw results
                    for *xyxy, conf, cls in reversed(det):
                        label = f'{self.names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, im0s, label=label, color=self.colors[int(cls)], line_thickness=2)

                # Save results
                if save_img:
                    cv2.imwrite(save_path, im0s)
                    logger.info(f"Saved detection result to {save_path}")

            logger.info(f'Detection completed: Inference {(t2 - t1):.3f}s, NMS {(t3 - t2):.3f}s')

            # Calculate and print the prediction score
            if len(det):
                avg_confidence = det[:, 4].mean().item()  # Calculate the average confidence score
                logger.info(f'Average prediction score: {avg_confidence:.2f}')
            else:
                logger.info('No detections in this image.')

            logger.info('All detections complete.')

    def continuous_detect(self, image_path, save_dir, fps=5):
        interval = 1.0 / fps
        logger.info(f"Starting continuous detection on {image_path} with {fps} FPS...")
        while True:
            try:
                if os.path.exists(image_path):
                    self.detect(image_path, save_dir)
                else:
                    logger.warning(f"Image {image_path} not found. Skipping this iteration...")
            except Exception as e:
                logger.error(f"Error during detection: {e}. Retrying in the next iteration...")
            time.sleep(interval)


if __name__ == "__main__":
    # Parameters
    weights = "/home/dartagnan-dev/sahil-dev/model_testing/YOLOv7_test/yolov7/runs/train/exp7/weights/best.pt"
    image_path = "/home/dartagnan-dev/sahil-dev/Sensor_integration/py_mmwave_dev/py_mmwave_read/range-azimuth-2D-Histogram/frame_0000.jpg"
    save_dir = "/home/dartagnan-dev/sahil-dev/Sensor_integration/py_mmwave_dev/py_mmwave_read/detection"
    fps = 5

    # Initialize detector
    detector = YOLOv7Detector(weights=weights, img_size=640, conf_thres=0.25, iou_thres=0.45, device='0')

    # Start continuous detection
    detector.continuous_detect(image_path=image_path, save_dir=save_dir, fps=fps)
