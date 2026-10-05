import time

from gpiozero import AngularServo

from foxy import config


class HeadServo:
    """Wrapper sul servo che muove testa/occhi di Foxy."""

    CENTER_ANGLE = 0
    LOOK_ANGLE = 45

    def __init__(self):
        self._servo = AngularServo(
            config.HEAD_SERVO_PIN,
            min_angle=-90,
            max_angle=90,
            min_pulse_width=0.0005,
            max_pulse_width=0.0025,
        )
        self._servo.angle = self.CENTER_ANGLE

    def look_at_presence(self):
        """Animazione semplice: la testa si gira verso chi si è avvicinato.

        Nota: un singolo sensore ultrasonico rileva solo distanza, non
        direzione. Questa animazione è un gesto fisso (destra-centro-sinistra),
        non un vero puntamento verso la persona.
        """
        self._servo.angle = self.LOOK_ANGLE
        time.sleep(0.6)
        self._servo.angle = -self.LOOK_ANGLE
        time.sleep(0.6)
        self._servo.angle = self.CENTER_ANGLE

    def close(self):
        self._servo.angle = self.CENTER_ANGLE
        self._servo.close()
