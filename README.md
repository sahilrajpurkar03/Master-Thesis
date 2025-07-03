# Master Thesis  
**Towards 6G-Driven Sensing: Development of Machine Learning-based Object Detection for Logistics Entities using mmWave Radar Sensor**

## 01. Sensor Integration

This section details the integration of the mmWave radar sensor used for data acquisition. The sensors employed are **IWR6843ISK** mounted on the **MMWAVEICBOOST** evaluation module by Texas Instruments (TI).

### Flashing the Default Firmware

To begin, flash the IWR6843ISK with the default TI firmware.  
🔗 **[Download Firmware from TI](https://www.ti.com/tool/MMWAVE-SDK)** 

#### S1 Switch Configuration for Flash Mode

| Mode           | S1.1 | S1.2 | S1.3 | S1.4 | S1.5 | S1.6 |
|----------------|------|------|------|------|------|------|
| Flashing Mode  | On   | Off  | On   | On   | Off  | N/A  |

#### Flash Steps (using UniFlash on Windows)

1. Launch **UniFlash**.
2. In *New Configuration*, select your device and click **Start**.
3. Go to the *Settings & Utilities* tab:
   - Set the COM port of the **CFG Port**.
4. Go to the *Program* tab:
   - Click **Browse** under *Meta Image 1* and select the `.bin` firmware file.
5. Toggle the **NRST** switch to power cycle the board.
6. Click **Load Image** to begin flashing.

Once complete, the firmware is successfully flashed.

---

### Hardware Setup

Refer to the image for physical setup:  
📷 `docs/hardware_setup.png`

#### Switch Configuration for MMWAVEICBOOST Mode

| Mode               | S1.1 | S1.2 | S1.3 | S1.4 | S1.5 | S1.6 |
|--------------------|------|------|------|------|------|------|
| MMWAVEICBOOST Mode | Off  | Off  | Off  | Off  | On   | —    |

---

### Running the Radar Sensor

1. Use the provided configuration file:  
   `01. Sensor Integration/mmwave_radar_read/config/xwr68xx_profile_2.cfg`

2. Navigate to the script directory and run:

   ```bash
   cd "01. Sensor Integration"
   python py_mmw_main.py
