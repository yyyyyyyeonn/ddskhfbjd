
import time
import logging
import argparse

from datetime import datetime

from config import initialize_system, SYSTEM_CONFIG
from sensor_monitor import SensorMonitor
from fall_detector import FallDetector
from notification import Notification


class ElderlyFallPreventionSystem:

    def __init__(self):

        self.sensor = SensorMonitor()
        self.detector = FallDetector()
        self.notification = Notification()

        self.running = False

        self.statistics = {
            "total_measurements": 0,
            "normal_count": 0,
            "warning_count": 0,
            "danger_count": 0,
            "alert_count": 0
        }

        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s "
                "%(levelname)s "
                "%(name)s: %(message)s"
            ),
            handlers=[
                logging.FileHandler(
                    "logs/system.log",
                    encoding="utf-8"
                ),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger("MainSystem")

    def initialize(self):

        result = initialize_system()

        self.logger.info(
            "System initialized: %s",
            result
        )

        return result

    def process_sensor_data(self, sensor_data):

        analysis_input = {
            "impact": sensor_data["impact"],
            "tilt": sensor_data["tilt"],
            "inactivity": sensor_data["inactivity"]
        }

        analysis = self.detector.analyze(
            analysis_input
        )

        self.statistics["total_measurements"] += 1

        risk = analysis["risk_level"]

        if risk == "low":
            self.statistics["normal_count"] += 1

        elif risk == "medium":
            self.statistics["warning_count"] += 1

        else:
            self.statistics["danger_count"] += 1

        alert = self.notification.send_alert(
            analysis
        )

        if alert:
            self.statistics["alert_count"] += 1

        result = {
            "sensor": sensor_data,
            "analysis": analysis,
            "alert": alert
        }

        self.display_result(result)

        return result

    def display_result(self, result):

        sensor = result["sensor"]
        analysis = result["analysis"]

        print("\n" + "=" * 50)

        print("ELDERLY FALL PREVENTION SYSTEM")

        print("=" * 50)

        print(
            "Timestamp:",
            sensor["timestamp"]
        )

        print(
            "Impact:",
            sensor["impact"]
        )

        print(
            "Tilt:",
            sensor["tilt"]
        )

        print(
            "Movement:",
            sensor["movement"]
        )

        print(
            "Inactivity:",
            sensor["inactivity"]
        )

        print("-" * 50)

        print(
            "Risk Score:",
            analysis["risk_score"]
        )

        print(
            "Risk Level:",
            analysis["risk_level"]
        )

        print(
            "Detected Conditions:",
            analysis["conditions"]
        )

        print(
            "Fall Detection:",
            analysis["fall_detected"]
        )

        print("=" * 50)

    def run_simulation(self, count=20, interval=1):

        self.initialize()

        self.running = True

        try:

            for _ in range(count):

                if not self.running:
                    break

                sensor_data = self.sensor.read_sensor()

                self.process_sensor_data(sensor_data)

                time.sleep(interval)

        except KeyboardInterrupt:

            self.logger.info(
                "Simulation interrupted"
            )

        finally:

            self.stop()

    def run_manual_test(self):

        self.initialize()

        test_data = [
            {
                "impact": 0.5,
                "tilt": 10,
                "movement": True
            },
            {
                "impact": 1.2,
                "tilt": 35,
                "movement": True
            },
            {
                "impact": 3.0,
                "tilt": 75,
                "movement": False
            },
            {
                "impact": 0.8,
                "tilt": 15,
                "movement": False
            }
        ]

        for data in test_data:

            sensor_data = self.sensor.read_sensor(data)

            self.process_sensor_data(sensor_data)

    def show_statistics(self):

        print("\nSYSTEM STATISTICS")

        for key, value in self.statistics.items():

            print(
                f"{key}: {value}"
            )

        print("\nRISK STATISTICS")

        risk_statistics = (
            self.detector.get_risk_statistics()
        )

        for key, value in risk_statistics.items():

            print(
                f"{key}: {value}"
            )

    def stop(self):

        self.running = False

        self.sensor.stop_monitoring()

        self.notification.save_history()

        self.show_statistics()

        self.logger.info(
            "System shutdown completed"
        )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["simulation", "test"],
        default="test"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=20
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1
    )

    args = parser.parse_args()

    system = ElderlyFallPreventionSystem()

    if args.mode == "simulation":

        system.run_simulation(
            count=args.count,
            interval=args.interval
        )

    else:

        system.run_manual_test()


if __name__ == "__main__":
    main()
