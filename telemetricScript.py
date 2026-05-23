import serial
import time
from datetime import datetime
import requests


# ================= CONFIG =================
PORT = "COM4"
BAUD_RATE = 9600
FIREBASE_URL = "https://alerts-8d801-default-rtdb.firebaseio.com"


GEOFENCE = {
    "lat_min": 43.6520,
    "lat_max": 43.6600,
    "lon_min": -79.3900,
    "lon_max": -79.3750,
}

active_alerts_sent = set()


# ================= PARSE DATA =================
def parse_vehicle_data(data_string: str) -> dict:
    data = {}
    parts = data_string.split(",")

    for item in parts:
        key, value = item.split("=")
        key = key.strip()
        value = value.strip()

        if key == "ignition":
            data[key] = int(value)
        else:
            data[key] = float(value)

    return data


# ================= ALERT LOGIC =================
def get_alerts(data: dict, previous_speed):
    alerts = []

    fuel = data["fuel"]
    temp = data["temp"]
    battery = data["battery"]
    speed = data["speed"]
    ignition = data["ignition"]
    lat = data["lat"]
    lon = data["lon"]
    current = data["current"]

    # Fuel
    if fuel < 8:
        alerts.append("[CRITICAL] Fuel extremely low")
    elif fuel < 15:
        alerts.append("[WARNING] Fuel low")

    # Temperature
    if temp > 115:
        alerts.append("[CRITICAL] Engine overheating")
    elif temp > 105:
        alerts.append("[WARNING] Engine temperature high")

    # Battery
    if ignition == 1:
        if battery < 11.2:
            alerts.append("[CRITICAL] Battery critically low")
        elif battery < 11.8:
            alerts.append("[WARNING] Battery low")

    # Speed
    if speed > 120:
        alerts.append("[WARNING] Overspeed detected")

    # Current
    if current > 0.30:
        alerts.append("[WARNING] Abnormal current draw")

    # Harsh braking
    if previous_speed is not None and (previous_speed - speed) > 20:
        alerts.append("[WARNING] Harsh braking event")

    # Geofence
    outside_geofence = (
        lat < GEOFENCE["lat_min"]
        or lat > GEOFENCE["lat_max"]
        or lon < GEOFENCE["lon_min"]
        or lon > GEOFENCE["lon_max"]
    )

    if outside_geofence:
        alerts.append("[WARNING] Outside geofence")

    return alerts


# ================= DASHBOARD =================
def print_dashboard(data: dict, alerts: list):
    print("\n================ VEHICLE STATUS ================")
    print(f"Time:         {datetime.now().strftime('%H:%M:%S')}")
    print(f"Speed:        {data['speed']:.1f} km/h")
    print(f"Fuel:         {data['fuel']:.1f} %")
    print(f"Engine Temp:  {data['temp']:.1f} C")
    print(f"Battery:      {data['battery']:.2f} V")
    print(f"Ignition:     {'ON' if data['ignition'] == 1 else 'OFF'}")
    print(f"Location:     {data['lat']:.6f}, {data['lon']:.6f}")
    print(f"Current:      {data['current']:.3f} A")

    if alerts:
        print("\nAlerts:")
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print("\nAlerts: None")

    print("================================================")


# ================= CLOUD UPLOAD =================
def send_alert_to_cloud(alert_payload: dict):
    url = f"{FIREBASE_URL}/alerts.json"

    try:
        response = requests.post(url, json=alert_payload, timeout=5)

        if response.status_code == 200:
            print("🌐 Alert sent to Firebase")
        else:
            print(f"❌ Upload failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Request error: {e}")


def upload_new_alerts_only(data: dict, alerts: list):
    global active_alerts_sent

    current_alerts = set(alerts)
    new_alerts = current_alerts - active_alerts_sent
    cleared_alerts = active_alerts_sent - current_alerts

    # Remove cleared alerts
    for cleared in cleared_alerts:
        active_alerts_sent.remove(cleared)

    # Send only NEW alerts
    for alert in new_alerts:
        severity = "CRITICAL" if "[CRITICAL]" in alert else "WARNING"

        alert_payload = {
            "vehicle_id": "vehicle_001",
            "severity": severity,
            "type": alert.replace("[CRITICAL] ", "").replace("[WARNING] ", ""),
            "message": alert,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "speed": data["speed"],
            "fuel": data["fuel"],
            "temp": data["temp"],
            "battery": data["battery"],
            "lat": data["lat"],
            "lon": data["lon"],
            "current": data["current"],
        }

        send_alert_to_cloud(alert_payload)
        active_alerts_sent.add(alert)


# ================= MAIN LOOP =================
def main():
    previous_speed = None

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Connected to {PORT}")

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            try:
                data = parse_vehicle_data(line)
                alerts = get_alerts(data, previous_speed)

                print_dashboard(data, alerts)
                upload_new_alerts_only(data, alerts)

                previous_speed = data["speed"]

            except Exception as e:
                print(f"Parse error: {e}")
                print(f"Raw data: {line}")

    except serial.SerialException as e:
        print(f"Serial error: {e}")

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial closed.")


if __name__ == "__main__":
    main()