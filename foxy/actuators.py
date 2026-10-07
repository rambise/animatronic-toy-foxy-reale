import time

from gpiozero import AngularServo

from foxy import config


class HeadServo:
    """Wrapper sul servo che muove testa/occhi di Cassidy."""

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

    def express_emotion(self, emotion: str):
        """Piccolo gesto con la testa legato all'emozione della risposta IA.

        Con un solo servo (pan della testa) non si possono fare vere
        espressioni facciali: sono gesti simbolici in attesa di avere
        servo dedicati a mascella/orecchie/occhi (vedi roadmap nel README).
        """
        gesture = {
            "felice": self._gesture_happy,
            "sorpreso": self._gesture_surprised,
            "triste": self._gesture_sad,
            "curioso": self._gesture_curious,
            "affettuoso": self._gesture_affectionate,
        }.get(emotion, self._gesture_neutral)
        gesture()

    def _gesture_happy(self):
        for _ in range(2):
            self._servo.angle = 20
            time.sleep(0.15)
            self._servo.angle = -20
            time.sleep(0.15)
        self._servo.angle = self.CENTER_ANGLE

    def _gesture_surprised(self):
        self._servo.angle = self.LOOK_ANGLE
        time.sleep(0.15)
        self._servo.angle = self.CENTER_ANGLE

    def _gesture_sad(self):
        self._servo.angle = -15
        time.sleep(1.0)
        self._servo.angle = self.CENTER_ANGLE

    def _gesture_curious(self):
        self._servo.angle = 25
        time.sleep(0.8)
        self._servo.angle = self.CENTER_ANGLE

    def _gesture_affectionate(self):
        self._servo.angle = 10
        time.sleep(0.4)
        self._servo.angle = -10
        time.sleep(0.4)
        self._servo.angle = self.CENTER_ANGLE

    def _gesture_neutral(self):
        self._servo.angle = self.CENTER_ANGLE

    def close(self):
        self._servo.angle = self.CENTER_ANGLE
        self._servo.close()
