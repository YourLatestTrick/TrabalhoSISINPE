import serial
import time
import sys

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
DISTANCE_LIMIT = 5.0

current_state = {
    "flood_alert": None,
    "trash_needs_pickup": None,
}

def flood_alert(water):
    return {
        "event": "flood_alert",
        "water": water,
    }

def trash_alert(distance):
    return {
        "event": "trash_needs_pickup",
        "distance_cm": distance,
    }

def monitor_system():
    print(f"Conectando ao Arduino")
    flood_alerted = False
    trash_alerted = False
    connection = None

    try:
        connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        
        while True:
            if connection.in_waiting > 0:
                line = connection.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                print(f"{line}")

                if "DIST:" not in line or "|WATER:" not in line:
                    continue

                try:
                    dist_part, water_part = line.split("|")
                    distance = float(dist_part.replace("DIST:", ""))
                    water = water_part.replace("WATER:", "").strip() == "1"
                except ValueError:
                    continue

                # Water alert
                if water and not flood_alerted:
                    flood_alerted = True
                    alert = flood_alert(water)
                    current_state["flood_alert"] = alert
                    print(alert)
                elif not water:
                    flood_alerted = False
                    current_state["flood_alert"] = None

                # Trash alert
                if 0 < distance <= DISTANCE_LIMIT and not trash_alerted:
                    trash_alerted = True
                    alert = trash_alert(distance)
                    current_state["trash_needs_pickup"] = alert
                    print(alert)
                elif distance > DISTANCE_LIMIT or distance < 0:
                    trash_alerted = False
                    current_state["trash_needs_pickup"] = None
            else:
                time.sleep(0.01)
                
    except serial.SerialException as e:
        print(f"Falha na porta serial: {e}")
    except KeyboardInterrupt:
        print("Monitoramento interrompido")
        sys.exit(0)
    finally:
        if connection is not None and connection.is_open:
            connection.close()
