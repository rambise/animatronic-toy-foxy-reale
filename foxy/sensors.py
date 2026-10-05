from gpiozero import DistanceSensor

from foxy import config


class PresenceSensor:
    """Wrapper sul sensore ultrasonico HC-SR04."""

    def __init__(self):
        self._sensor = DistanceSensor(
            echo=config.ULTRASONIC_ECHO_PIN,
            trigger=config.ULTRASONIC_TRIGGER_PIN,
            max_distance=config.ULTRASONIC_MAX_DISTANCE_M,
        )

    def distance_m(self) -> float:
        """Distanza rilevata in metri."""
        return self._sensor.distance

    def is_someone_near(self) -> bool:
        return self.distance_m() <= config.PRESENCE_THRESHOLD_M

    def close(self):
        self._sensor.close()
