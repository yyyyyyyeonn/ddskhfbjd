
import time
import random
import logging
import threading

from datetime import datetime
from collections import deque

from config import SENSOR_CONFIG


class SensorMonitor:

    def __init__(self, history_limit=None):
        self.running = False
        self.lock = threading.Lock()

        self.history_limit = (
            history_limit or SENSOR_CONFIG["history_limit"]
        )

        self.sensor_history = deque(
            maxlen=self.history_limit
        )

        self.sensor_status = {
            "impact": 0.0,
            "tilt": 0.0,
            "movement": True,
            "inactivity": 0
        }

        self.logger = logging.getLogger("SensorMonitor")

    def generate_sensor_data(self):
        impact = round(random.uniform(0.1, 1.5), 2)
        tilt = round(random.uniform(0, 35), 2)
        movement = random.choice([True, True, True, False])

        return {
            "impact": impact,
            "tilt": tilt,
            "movement": movement
        }

    def validate_sensor_data(self, data):

        required = ["impact", "tilt", "movement"]

        if not isinstance(data, dict):
            raise TypeError("Sensor data must be dictionary")

        for key in required:
            if key not in data:
                raise ValueError(f"Missing sensor value: {key}")

        impact = float(data["impact"])
        tilt = float(data["tilt"])

        if impact < 0:
            raise ValueError("Impact cannot be negative")

        if not 0 <= tilt <= 180:
            raise ValueError("Tilt value out of range")

        if not isinstance(data["movement"], bool):
            raise ValueError("Movement must be boolean")

        return True

    def read_sensor(self, data=None):

        if data is None:
            data = self.generate_sensor_data()

        self.validate_sensor_data(data)

        with self.lock:

            current_time = datetime.now()

            if data["movement"]:
                self.sensor_status["inactivity"] = 0
            else:
                self.sensor_status["inactivity"] += (
                    SENSOR_CONFIG["measurement_interval"]
                )

            result = {
                "timestamp": current_time.isoformat(),
                "impact": float(data["impact"]),
                "tilt": float(data["tilt"]),
                "movement": data["movement"],
                "inactivity": self.sensor_status["inactivity"]
            }

            self.sensor_history.append(result)
            self.sensor_status.update(result)

            self.logger.info("Sensor data collected")

            return result

    def get_latest_data(self):

        with self.lock:
            if not self.sensor_history:
                return None

            return self.sensor_history[-1].copy()

    def get_history(self, limit=100):

        with self.lock:
            return [
                item.copy()
                for item in list(self.sensor_history)[-limit:]
            ]

    def calculate_average(self, key):

        with self.lock:
            values = [
                item[key]
                for item in self.sensor_history
                if key in item
            ]

        if not values:
            return 0

        return sum(values) / len(values)

    def start_monitoring(self, callback=None, interval=1):

        if self.running:
            return

        self.running = True

        try:
            while self.running:

                data = self.read_sensor()

                if callback:
                    callback(data)

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stop_monitoring()

        finally:
            self.running = False

    def stop_monitoring(self):
        self.running = False

    def get_sensor_status(self):

        return {
            "running": self.running,
            "history_count": len(self.sensor_history),
            "average_impact": round(
                self.calculate_average("impact"), 2
            ),
            "average_tilt": round(
                self.calculate_average("tilt"), 2
            )
        }


if __name__ == "__main__":

    monitor = SensorMonitor()

    for _ in range(10):
        result = monitor.read_sensor()
        print(result)

    print(monitor.get_sensor_status())
