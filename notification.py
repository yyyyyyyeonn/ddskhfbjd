
import json
import logging

from pathlib import Path
from datetime import datetime

from config import DATA_DIR, ALERT_CONFIG


class Notification:

    def __init__(self, guardian_name="Guardian"):

        self.guardian_name = guardian_name

        self.alert_history = []

        self.alert_file = DATA_DIR / "alert_history.json"

        self.logger = logging.getLogger("Notification")

        self.load_history()

    def create_message(self, analysis):

        risk = analysis["risk_level"]
        score = analysis["risk_score"]
        conditions = analysis["conditions"]

        if risk == "critical":
            message = "Critical fall risk detected."

        elif risk == "high":
            message = "High fall risk detected."

        elif risk == "medium":
            message = "Abnormal activity detected."

        else:
            message = "Normal activity."

        return {
            "guardian": self.guardian_name,
            "message": message,
            "risk_level": risk,
            "risk_score": score,
            "conditions": conditions,
            "timestamp": datetime.now().isoformat()
        }

    def send_alert(self, analysis):

        if not ALERT_CONFIG["enabled"]:
            return False

        risk = analysis["risk_level"]

        if risk not in ["high", "critical"]:
            return False

        alert = self.create_message(analysis)

        self.alert_history.append(alert)

        self.logger.warning(
            "Alert generated: %s",
            alert["message"]
        )

        self.save_history()

        return alert

    def save_history(self):

        if not ALERT_CONFIG["save_history"]:
            return

        self.alert_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary_file = self.alert_file.with_suffix(".tmp")

        try:
            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.alert_history,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            temporary_file.replace(self.alert_file)

        except OSError as error:

            self.logger.error(
                "Failed to save alert history: %s",
                error
            )

            raise

    def load_history(self):

        if not self.alert_file.exists():
            self.alert_history = []
            return

        try:
            with open(
                self.alert_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, list):
                    self.alert_history = data

        except (OSError, json.JSONDecodeError) as error:

            self.logger.error(
                "Failed to load alert history: %s",
                error
            )

            self.alert_history = []

    def get_alert_history(self):

        return self.alert_history.copy()

    def get_alert_count(self):

        return len(self.alert_history)

    def filter_alerts(self, risk_level):

        return [
            alert
            for alert in self.alert_history
            if alert["risk_level"] == risk_level
        ]

    def clear_history(self):

        self.alert_history.clear()
        self.save_history()


if __name__ == "__main__":

    notification = Notification()

    test_analysis = {
        "risk_level": "high",
        "risk_score": 85,
        "conditions": [
            "HIGH_IMPACT",
            "ABNORMAL_TILT"
        ]
    }

    result = notification.send_alert(test_analysis)

    print(result)
    print(notification.get_alert_count())
