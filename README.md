# Master Thesis  
**Towards 6G-Driven Sensing: Development of Machine Learning-based Object Detection for Logistics Entities using mmWave Radar Sensor**

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
![Hardware Setup](docs/hardware_setup.png)

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
   cd "01. Sensor Integration"
   python py_mmw_main.py
