# Master Thesis: **Towards 6G-Driven Sensing: Development of Machine Learning-based Object Detection for Logistics Entities using mmWave Radar Sensor**

---

## 📄 Thesis Overview

This thesis investigates the potential of mmWave radar sensors for object detection in logistics environments, offering an alternative to traditional camera and LiDAR-based systems. These conventional systems suffer from drawbacks such as high costs, sensitivity to lighting and weather conditions, privacy concerns, and occlusion issues in complex warehouse environments.

To address these limitations, the study integrates the Texas Instruments **IWR6843ISK** mmWave radar sensor into a logistics setting and develops a machine learning-based object detection pipeline. Models such as **YOLOv7**, **Detectron2**, and **OpenPCDet** are trained and evaluated for detecting logistics entities like forklifts, mobile robots, and small load carriers (KLTs). The system is assessed for real-time performance in dynamic and cluttered environments, demonstrating the benefits of radar-based sensing—such as high resolution, environmental robustness, and reliable operation in low-visibility conditions.

This research contributes to the vision of 6G-driven smart logistics by offering a cost-effective, scalable, and privacy-preserving sensing alternative for industrial automation.

---

## 📚 Repository Index

1. [Sensor Integration](#01-sensor-integration)
2. [Data Collection](#02-data-collection)
3. [Preprocessing and Annotation](#03-preprocessing-and-annotation)
4. [Model Training & Evaluation](#04-model-training--evaluation)
5. [Real-Time Testing](#05-real-time-testing)
6. [Results & Analysis](#06-results--analysis)
7. [Future Work](#07-future-work)

---

## 01. Sensor Integration

This section outlines the integration of the mmWave radar sensor used for data collection. The sensors used are:

- **[IWR6843ISK](https://www.ti.com/tool/IWR6843ISK)**  
- **[MMWAVEICBOOST](https://www.ti.com/tool/MMWAVEICBOOST)**  
by Texas Instruments (TI).

---

### Flashing the Default Firmware

Begin by flashing the IWR6843ISK with TI's default firmware:  
🔗 **[Download from TI – mmWave SDK](https://www.ti.com/tool/MMWAVE-SDK)**

#### 🔧 S1 Switch Configuration for Flash Mode

| Mode          | S1.1 | S1.2 | S1.3 | S1.4 | S1.5 | S1.6 |
|---------------|------|------|------|------|------|------|
| Flash Mode    | On   | Off  | On   | On   | Off  | N/A  |

#### 💻 Flashing Steps (Using [UniFlash](https://www.ti.com/tool/UNIFLASH) on Windows)

1. Launch **UniFlash**.
2. In **New Configuration**, select your device and click **Start**.
3. Go to **Settings & Utilities**:
   - Set the COM port of the **CFG Port**.
4. Go to the **Program** tab:
   - Click **Browse** under *Meta Image 1* and select the `.bin` file.
5. Toggle the **NRST** switch to power cycle the board.
6. Click **Load Image** to flash.

> ✅ Firmware is now successfully flashed.

---

### 🧰 Hardware Setup

Refer to the image for physical connection and jumper setup:  
<p align="center">
  <img src="docs/hardware_setup.png" alt="Hardware Setup" width="400"/>
</p>

---

#### 🔄 Switch Configuration for MMWAVEICBOOST Mode

| Mode                 | S1.1 | S1.2 | S1.3 | S1.4 | S1.5 | S1.6 |
|----------------------|------|------|------|------|------|------|
| MMWAVEICBOOST Mode   | Off  | Off  | Off  | Off  | On   | —    |

---

### 🚀 Running the Radar Sensor

1. Use the provided configuration file:  
   [`xwr68xx_profile_2.cfg`](./01.%20Sensor%20Integration/mmwave_radar_read/config/xwr68xx_profile_2.cfg)

2. Run the following command to start data capture:

   ```bash
   cd 01_SensorIntegration
   python py_mmw_main.py

3.  Captured Output Data
   - Saved in: `01_SensorIntegration/log/` as `.txt` files
   - Contains per timestamp:
      - Number of points detected
      - Range, azimuth, elevation
      - x,y,z coordinates
      - Velocity (v)
      - Range profile and SNR

## 02. Data Collection

The datasets used in this project include both raw and arranged data, which have been made publicly available on Kaggle.

- **Kaggle Repository – Arranged Dataset:**  
  [https://www.kaggle.com/mmwave-radar-dataset](https://kaggle.com/datasets/a5860c7266e6d1191bf4a4aa9ae23b057b86e63d9d10982285d128fb0957a796)

- **Kaggle Repository – Raw Dataset:**  
  [https://www.kaggle.com/mmwave-radar-dataset-raw](https://kaggle.com/datasets/f7de6334ad0bf5c2c828f40989f076e88b08063e22bbbd680a722276482816fc)

## 03. Preprocessing and Annotation

### Range-Azimuth Dataset Creation
To convert collected raw log files into range-azimuth 2D histogram frames, execute the following command:
```bash
cd 02_DataPreprocessing/Yolov7/
python3 Gen-Range-Azimuth-2D-Histogram.py
```

### Annotation Process
Use [LabelImg](https://github.com/HumanSignal/labelImg) for annotation:
   - Load images
   - Draw bounding boxes
   - Save annotations in YOLOv7 format

This process generates labels in YOLOv7 format.

<p align="center">
  <img src="docs/labelimg_example.png" alt="LabelImg Interface" width="800"/>
</p>

### Dataset Directory Structure

#### For YOLOv7:
Organize the dataset in the following structure for train/test/validation splits:
```
-images/
   ├── test/
   │   ├── frame0001.jpg
   │   └── ...
   ├── train/
   │   ├── frame0100.jpg
   │   └── ...
   └── val/
       ├── frame0150.jpg
       └── ...
-labels/
   ├── test/
   │   ├── frame0001.txt
   │   └── ...
   ├── train/
   │   ├── frame0100.txt
   │   └── ...
   └── val/
       ├── frame0150.txt
       └── ...
```
**Label Format:**  
`<class_id> <x_center> <y_center> <width> <height>`

#### For Detectron2:
Organize the dataset as follows:
```
-images/
   ├── train/
   │   ├── annotations.coco.json
   │   ├── frame0001.jpg
   │   └── ...
   └── test/
       ├── annotations.coco.json
       ├── frame0100.jpg
       └── ...
```

To convert YOLO annotations to COCO format for Detectron2, run:
```bash
cd 02_DataPreprocessing/Detectron2/
python3 yolo_to_coco.py
```



## 04. Model Training & Evaluation
## 05. Real-Time Testing
## 06. Results & Analysis
## 07. Future Work

---

## Project Information

**University:**  
Technical University Dortmund (Technische Universität Dortmund)  
Faculty of Mechanical Engineering  
Chair of Material Handling and Warehousing  

**Thesis Title:**  
Towards 6G-Driven Sensing: Development of Machine Learning-based Radar Object Detection for Logistics Entities  

**Degree Program:**  
Master of Science in Automation and Robotics  

**Presented by:**  
Sahil Sanjay Rajpurkar    

**Supervisors:**  
- First Examiner: Prof.’in Dr.-Ing. Alice Kirchheim  
- Second Examiner: Irfan Fachrudin Priyanta, M.Sc.   

**Place of Submission:** Dortmund, Germany  

---

© 2025 Sahil Sanjay Rajpurkar.  
This repository is intended solely for academic and study purposes. Commercial use is not permitted.