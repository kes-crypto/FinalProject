# ingest_simulator.py - sends simulated sensor readings to the API
import requests, time, random, datetime

API = "http://localhost:8000/ingest"

SENSORS = [
    {"sensor_id":"field-1-sensor-A","location":"Field 1"},
    {"sensor_id":"field-1-sensor-B","location":"Field 1"},
    {"sensor_id":"field-2-sensor-A","location":"Field 2"},
]

def generate_reading(sensor):
    now = datetime.datetime.utcnow().isoformat()
    # simple synthetic ranges appropriate for many soils/crops
    return {
        "sensor_id": sensor["sensor_id"],
        "location": sensor["location"],
        "timestamp": now,
        "soil_moisture": round(random.uniform(8.0, 45.0),2),
        "temperature": round(random.uniform(15.0, 35.0),2),
        "humidity": round(random.uniform(30.0, 90.0),2),
        "ph": round(random.uniform(4.5,8.5),2),
        "crop": random.choice(["maize","beans","tomatoes"])
    }

if __name__ == '__main__':
    print("Starting simulator. Press Ctrl-C to stop.")
    try:
        while True:
            s = random.choice(SENSORS)
            r = generate_reading(s)
            try:
                res = requests.post(API, json=r, timeout=5)
                if res.status_code == 201:
                    print("Sent", r["sensor_id"], r["soil_moisture"], "at", r["timestamp"])
                else:
                    print("API error", res.status_code, res.text)
            except Exception as e:
                print("Failed to send:", e)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Simulator stopped.")
