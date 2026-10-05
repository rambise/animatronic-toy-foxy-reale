from gpiozero import Robot

from foxy import config


class DriveBase:
    """Trazione differenziale su due motori (ruote o cingoli nascosti sotto il corpo).

    Nota hardware: gpiozero.Robot pilota solo le direzioni (avanti/indietro)
    dei due motori. Se usi un driver tipo L298N con pin ENA/ENB separati,
    collegali fissi a 5V (o a un GPIO sempre alto) - gpiozero non li gestisce.
    Driver come TB6612FNG/DRV8833 di solito non ne hanno bisogno.
    """

    def __init__(self):
        self._robot = Robot(
            left=(config.MOTOR_LEFT_FORWARD_PIN, config.MOTOR_LEFT_BACKWARD_PIN),
            right=(config.MOTOR_RIGHT_FORWARD_PIN, config.MOTOR_RIGHT_BACKWARD_PIN),
        )

    def forward(self, speed: float = config.DRIVE_SPEED):
        self._robot.forward(speed)

    def backward(self, speed: float = config.DRIVE_SPEED):
        self._robot.backward(speed)

    def turn_left(self, speed: float = config.TURN_SPEED):
        self._robot.left(speed)

    def turn_right(self, speed: float = config.TURN_SPEED):
        self._robot.right(speed)

    def stop(self):
        self._robot.stop()

    def close(self):
        self._robot.stop()
        self._robot.close()
