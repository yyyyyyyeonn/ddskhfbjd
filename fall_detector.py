
import logging

from collections import deque
from datetime import datetime

from config import SENSOR_CONFIG, RISK_CONFIG


class FallDetector:

    def __init__(self):

        self.impact_threshold = (
            SENSOR_CONFIG["impact_threshold"]
        )

        self.tilt_threshold = (
            SENSOR_CONFIG["tilt_threshold"]
        )

        self.inactivity_threshold = (
            SENSOR_CONFIG["inactivity_threshold"]
        )

        self.detection_history = deque(maxlen=1000)

        self.logger = logging.getLogger("FallDetector")

        self.previous_risk = "low"

    def calculate_impact_score(self, impact):

        if impact >= self.impact_threshold:
            return 100

        score = (
            impact / self.impact_threshold
        ) * 100

        return round(score, 2)

    def calculate_tilt_score(self, tilt):

        if tilt >= self.tilt_threshold:
            return 100

        score = (
            tilt / self.tilt_threshold
        ) * 100

        return round(score, 2)

    def calculate_inactivity_score(self, inactivity):

        if inactivity >= self.inactivity_threshold:
            return 100

        score = (
            inactivity / self.inactivity_threshold
        ) * 100

        return round(score, 2)

    def calculate_risk_score(self, data):

        impact_score = self.calculate_impact_score(
            data["impact"]
        )

        tilt_score = self.calculate_tilt_score(
            data["tilt"]
        )

        inactivity_score = self.calculate_inactivity_score(
            data["inactivity"]
        )

        total_score = (
            impact_score * 0.45
            + tilt_score * 0.35
            + inactivity_score * 0.20
        )

        return round(total_score, 2)

    def classify_risk(self, score):

        if score >= RISK_CONFIG["critical"]:
            return "critical"

        elif score >= RISK_CONFIG["high"]:
            return "high"

        elif score >= RISK_CONFIG["medium"]:
            return "medium"

        return "low"

    def detect_fall_conditions(self, data):

        conditions = []

        if data["impact"] >= self.impact_threshold:
            conditions.append("HIGH_IMPACT")

        if data["tilt"] >= self.tilt_threshold:
            conditions.append("ABNORMAL_TILT")

        if data["inactivity"] >= self.inactivity_threshold:
            conditions.append("LONG_INACTIVITY")

        if (
            data["impact"] >= self.impact_threshold
            and data["tilt"] >= self.tilt_threshold
        ):
            conditions.append("POSSIBLE_FALL")

        return conditions

    def analyze(self, data):

        required = [
            "impact",
            "tilt",
            "inactivity"
        ]

        for key in required:
            if key not in data:
                raise ValueError(
                    f"Missing analysis field: {key}"
                )

        score = self.calculate_risk_score(data)

        risk_level = self.classify_risk(score)

        conditions = self.detect_fall_conditions(data)

        result = {
            "timestamp": datetime.now().isoformat(),
            "risk_score": score,
            "risk_level": risk_level,
            "conditions": conditions,
            "fall_detected": "POSSIBLE_FALL" in conditions,
            "previous_risk": self.previous_risk
        }

        self.previous_risk = risk_level

        self.detection_history.append(result)

        self.logger.info(
            "Risk analysis completed: %s",
            risk_level
        )

        return result

    def get_detection_history(self, limit=100):

        return list(self.detection_history)[-limit:]

    def get_risk_statistics(self):

        statistics = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }

        for result in self.detection_history:

            level = result["risk_level"]

            statistics[level] += 1

        return statistics

    def reset_history(self):

        self.detection_history.clear()
        self.previous_risk = "low"


if __name__ == "__main__":

    detector = FallDetector()

    sample = {
        "impact": 3.0,
        "tilt": 75,
        "inactivity": 100
    }

    result = detector.analyze(sample)

    print(result)
    print(detector.get_risk_statistics())
