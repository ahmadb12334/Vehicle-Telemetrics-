# Telemetrics Monitoring System

A real-time telemetrics monitoring prototype that simulates vehicle telemetry using an Arduino, processes the data in Python, and uploads alert events to Firebase for cloud-based monitoring.

---

# Overview

This system demonstrates a complete telemetry pipeline:

Arduino → Python → Firebase Cloud

The Arduino acts as a simulated onboard telemetry device, generating vehicle telemetry data and reading real current values using an ACS712 current sensor. The Python application receives and processes this data in real time, applies alert logic, and uploads alert events to Firebase Realtime Database.

---

# Features

- Real-time telemetry generation
- ACS712 current sensing
- Serial communication between Arduino and Python
- Simulated vehicle data:
  - Speed
  - Fuel level
  - Engine temperature
  - Battery voltage
  - GPS location
  - Ignition state
- Rule-based alert detection
- Geofence monitoring
- Cloud alert upload using Firebase
- Duplicate alert prevention using state tracking

---

# System Architecture

```text
Arduino Device
      ↓
Python Processing Layer
      ↓
Firebase Realtime Database
```

---

# Hardware Components

- Arduino Uno
- ACS712 Current Sensor (5A)
- LED Load
- 220Ω Resistor
- Breadboard + Jumper Wires

---

# Circuit Overview

## Signal Connections

- ACS712 VCC → Arduino 5V
- ACS712 GND → Arduino GND
- ACS712 OUT → Arduino A0

## Current Path

```text
5V → IP+ → IP- → Resistor → LED → GND
```

---

# Software Stack

## Arduino
Used for:
- Telemetry simulation
- Current sensing
- Serial communication

## Python
Used for:
- Telemetry parsing
- Alert processing
- Dashboard display
- Cloud communication

## Firebase Realtime Database
Used for:
- Cloud-based alert storage
- Remote monitoring

---

# Python Libraries Used

## pyserial
Used for serial communication with the Arduino.

Install:
```bash
pip install pyserial
```

## requests
Used to send HTTP POST requests to Firebase.

Install:
```bash
pip install requests
```

## datetime
Used for timestamps.

## time
Used for serial initialization delays.

---

# Alert Logic

The system detects:
- Low Fuel
- Engine Overheating
- Low Battery Voltage
- Overspeed Events
- Abnormal Current Draw
- Harsh Braking
- Geofence Violations

Alerts are categorized into:
- WARNING
- CRITICAL

---

# Firebase Integration

Alerts are uploaded to Firebase Realtime Database using REST API POST requests.

Example endpoint:

```text
https://your-project-id-default-rtdb.firebaseio.com/alerts.json
```

Each alert is uploaded as a structured JSON object containing:
- Vehicle ID
- Severity
- Timestamp
- Telemetry values
- Alert message

---

# Duplicate Alert Prevention

The Python application tracks active alerts using a Python set:

```python
active_alerts_sent = set()
```

This prevents repeated uploads of the same alert condition every cycle.

---

# Example Telemetry Packet

```text
speed=72.0,fuel=84.8,temp=105.7,battery=12.2,ignition=1,lat=43.668224,lon=-79.373184,current=0.006
```

---

# Running the Project

## 1. Upload Arduino Code
Upload the Arduino sketch to the board using Arduino IDE.

## 2. Install Python Dependencies

```bash
pip install pyserial requests
```

## 3. Configure Firebase URL

```python
FIREBASE_URL = "https://your-project-id-default-rtdb.firebaseio.com"
```

## 4. Run Python Script

```bash
python telemetricScript.py
```

---

# Example Output

```text
================ VEHICLE STATUS ================
Speed:        72.0 km/h
Fuel:         12.4 %
Engine Temp:  108.5 C
Battery:      11.7 V
Ignition:     ON
Location:     43.654210, -79.382110
Current:      0.006 A

Alerts:
  - [WARNING] Fuel low
================================================
```

---

# Future Improvements

- Live dashboard UI
- Real GPS integration
- CAN bus communication
- Secure Firebase authentication
- MQTT support
- Multi-vehicle support

---

# Author

Ahmad Bhutta  
Computer Engineering Student  
Toronto Metropolitan University
