import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

SYSTEM_CONFIG = {
    "system_name": "Elderly Fall Prevention System",
    "version": "1.0.0",
    "debug": True,
    "language": "ko",
    "timezone": "Asia/Seoul"
}

SENSOR_CONFIG = {
    "impact_threshold": 2.5,
    "tilt_threshold": 60.0,
    "inactivity_threshold": 1800,
    "measurement_interval": 1,
    "history_limit": 1000
}

RISK_CONFIG = {
    "low": 0,
    "medium": 40,
    "high": 70,
    "critical": 90
}

ALERT_CONFIG = {
    "enabled": True,
    "repeat_interval": 300,
    "max_retry": 3,
    "save_history": True
}

DATABASE_CONFIG = {
    "file": str(DATA_DIR / "elderly_data.db"),
    "timeout": 30,
    "check_same_thread": False
}

LOG_CONFIG = {
    "file": str(LOG_DIR / "system.log"),
    "level": "INFO",
    "max_bytes": 10485760,
    "backup_count": 5
}


def get_config(section):
    if section not in globals():
        raise KeyError(f"Unknown configuration: {section}")

    value = globals()[section]

    if not isinstance(value, dict):
        raise TypeError("Configuration must be dictionary")

    return value.copy()


def validate_config():
    required_values = [
        SENSOR_CONFIG["impact_threshold"],
        SENSOR_CONFIG["tilt_threshold"],
        SENSOR_CONFIG["inactivity_threshold"]
    ]

    for value in required_values:
        if not isinstance(value, (int, float)):
            raise ValueError("Invalid sensor configuration")

        if value <= 0:
            raise ValueError("Configuration must be positive")

    if SENSOR_CONFIG["tilt_threshold"] > 180:
        raise ValueError("Invalid tilt threshold")

    return True


def initialize_system():
    validate_config()

    for directory in [DATA_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    return {
        "system": SYSTEM_CONFIG["system_name"],
        "version": SYSTEM_CONFIG["version"],
        "status": "initialized"
    }


if __name__ == "__main__":
    result = initialize_system()
    print(result)
