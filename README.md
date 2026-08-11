# Camel Thermal Stress & Workload Telemetry System

A custom hardware-to-dashboard pipeline designed to monitor environmental 
heat stress and movement load in high performance racing camels during 
extreme heat training in the Gulf region.

---

## Overview & Background

Camel racing requires balancing intense athletic conditioning with extreme 
environmental safety. Because camels exhibit heterothermy—fluctuating 
their core body temperature by up to 6°C across the day—standard human 
heat stress formulas fail to accurately measure their physiological 
strain.

I designed and built this system to give camel trainers real-time 
visibility into microclimate conditions and training intensity on the 
track. By pairing dynamic sensor sampling with livestock-specific thermal 
formulas, the platform calculates immediate heat safety bounds and tracks 
physical workload over time to help prevent heat stroke and overtraining 
injuries.

---

## System Architecture


On-Animal Sensing Unit ]
├── DHT22 Temp & Relative Humidity Sensor (GPIO 4)
└── MPU-6050 6-DoF Accelerometer / Gyroscope (I2C SDA/SCL)
│
│ (1000ms Interrupt Driven Sampling / Serial Output @ 115200 Baud)
v
[ Local Ingestion & Analytics Engine ]
├── Non-blocking Serial Processing (Python)
├── Livestock Weather Safety Index (LWSI) Calculation
└── Exponentially Weighted ACWR Workload Engine (7-day vs 28-day)
│
v
[ Field Web Dashboard ]
└── Interactive Streamlit Interface (Dark Mode / High-Visibility 
Alerts)---

## Hardware Pinout & Specs

| Component | Interface | ESP32 GPIO Pin | Function / Operating Notes |
| :--- | :--- | :--- | :--- |
| **DHT22** | Single-Wire Data | GPIO 4 | Ambient temperature & relative 
humidity (requires 10kΩ pull-up) |
| **MPU-6050** | I2C Data (SDA) | GPIO 21 | 3-axis motion acceleration for 
gait/workload tracking |
| **MPU-6050** | I2C Clock (SCL) | GPIO 22 | Hardware clock sync for 
motion vector polling |
| **ESP32** | USB / Serial | UART (115200) | Local power & real-time 
telemetry streaming |

---

## Applied Engineering & Mathematical Models

### 1. Livestock Weather Safety Index (LWSI)
To accurately quantify heat stress for dromedary camels, raw temperature 
($T_{db}$ in °C) and relative humidity ($RH$ as a decimal) are processed 
using a specialized livestock index rather than standard human heat index 
models:

$$\text{THI} = (1.8 \cdot T_{\text{db}} + 32) - \left[(0.55 - 0.55 \cdot 
\text{RH}) \cdot (1.8 \cdot T_{\text{db}} - 26)\right]$$

* **Normal:** $\text{THI} < 74$
* **Alert:** $74 \le \text{THI} < 79$
* **Danger:** $79 \le \text{THI} < 84$
* **Emergency:** $\text{THI} \ge 84$

### 2. Motion Vector Isolation & ACWR Calculation
To measure movement workload independent of gravity, static acceleration 
($9.81 \text{ m/s}^2$) is isolated from the 3-axis magnitude vector:

$$\text{Accel}_{\text{net}} = \left| \sqrt{a_x^2 + a_y^2 + a_z^2} - 9.81 
\right|$$

Using Exponentially Weighted Moving Averages (EWMA), daily intensity is 
tracked across a 7-day acute window and a 28-day chronic baseline:

$$\text{ACWR} = \frac{\text{Acute Workload (7-Day Average)}}{\text{Chronic 
Workload (28-Day Average)}}$$

* **Under-trained Zone:** $\text{ACWR} < 0.8$
* **Optimal Conditioning:** $0.8 \le \text{ACWR} \le 1.3$
* **High Injury Risk:** $\text{ACWR} > 1.5$

---

## Engineering Challenges & Field Observations

Building and testing a physical sensor package for field use revealed 
several practical constraints that required specific software and hardware 
adjustments:

1. **Thermal Sensor Inertia:**
   * *Problem:* Moving the sensor housing between air-conditioned stables 
and the hot track caused a 90–120 second thermal lag in raw DHT22 
readings.
   * *Solution:* Implemented a 3-point rolling median filter in the Python 
ingestion engine (`modules/data_engine.py`) to smooth transient spikes 
while preserving rapid trend detection.

2. **PCB Heat Bleed & Solar Radiation:**
   * *Problem:* Direct solar radiation on dark sensor housing caused raw 
ambient temperature readings to drift upwards by approximately 1.5°C to 
2.5°C.
   * *Solution:* Added a software calibration offset (`TEMP_OFFSET_C`) in 
the C++ firmware (`firmware/main.cpp`) during initial field testing, with 
plans for a vented, 3D-printed double-walled solar shield in V2.

3. **Serial Reliability & Data Packetizing:**
   * *Problem:* High movement vibrations during track runs occasionally 
corrupted raw string transmissions over the USB serial interface.
   * *Solution:* Standardized the payload structure to framed ASCII lines 
(`$CAMEL_TEL,temp,humidity,accel*CHECKSUM`) with lightweight checksum 
verification before parsing into the analytics engine.

---

## Quickstart & Setup

### Prerequisites
* Python 3.9+
* ESP32 microcontroller with DHT22 and MPU-6050 wired as noted in the 
pinout table.

### Local Installation

bash
# Clone the repository
git clone https://github.com/saeedalnuaimi2008/camel-stress-monitor.git
cd camel-stress-monitor# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Launch the interactive Streamlit dashboard
streamlit run app.py---

## Project Roadmap & Future Iterations

* [ ] **V2 Wireless Telemetry:** Transition from continuous USB-serial 
connection to an ESP-NOW / LoRaWAN wireless transceiver operating at 915 
MHz for long-range track coverage.
* [ ] **Enclosure Design:** CAD modeling and 3D printing a custom, 
lightweight harness enclosure with passive airflow channels for direct 
on-camel mounting.
* [ ] **Persistent Storage:** Integrating SQLite/PostgreSQL logging to 
track multi-season workload trends for individual animals across training 
cycles.

## Mechanical Enclosure & CAD Architecture

The sensor package is housed in a custom double-walled, ventilated 
enclosure designed to withstand desert field conditions. 

- **Outer Shield:** Matte white ASA to reflect direct solar radiation and 
prevent thermal drift.
- **Inner Core:** PETG housing to secure the ESP32 and sensor stack.
- **Air Gap:** 2mm dead-air insulation layer to mitigate internal heat 
buildup.

Source and build files are located in the `cad/` directory, including the 
parametric generator script (`generate_cad.py`).

[Inspect 3D Enclosure Model (GLB)](cad/enclosure_v1.glb)
