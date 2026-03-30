import time
import requests

SIMULATOR_BASE = "http://simulator:8080"

EVENT_TYPES = [
    "earthquake",
    "conventional_explosion",
    "nuclear_like",
]

def wait_for_simulator():
    print("[demo] Waiting for simulator...")
    while True:
        try:
            r = requests.get(f"{SIMULATOR_BASE}/health", timeout=2)
            if r.status_code == 200:
                print("[demo] Simulator is ready")
                return
        except:
            pass
        time.sleep(2)

def fetch_sensors():
    r = requests.get(f"{SIMULATOR_BASE}/api/devices/", timeout=5)
    r.raise_for_status()
    return r.json()

def inject_event(sensor_id, event_type):
    url = f"{SIMULATOR_BASE}/api/admin/sensors/{sensor_id}/events"
    payload = {"event_type": event_type}

    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"[demo] Injected {event_type} on {sensor_id}")
        else:
            print(f"[demo] Failed injection {sensor_id}: {r.status_code}")
    except Exception as e:
        print(f"[demo] Error injecting event: {e}")

def main():
    wait_for_simulator()

    time.sleep(5)  # lascia partire broker e processing

    sensors = fetch_sensors()
    print(f"[demo] Found {len(sensors)} sensors")

    # 🔥 ciclo di injection
    for i in range(5):
        for sensor in sensors[:3]:  # usa solo alcuni sensori
            event_type = EVENT_TYPES[i % len(EVENT_TYPES)]
            inject_event(sensor["id"], event_type)

        time.sleep(3)

    print("[demo] Injection completed")


if __name__ == "__main__":
    main()