import random
import time

from gpiozero import DigitalInputDevice, DistanceSensor

from foxy import config
from foxy.motors import DriveBase


class CliffSensor:
    """Sensore IR rivolto verso il pavimento, montato sotto il telaio.

    Rileva quando il pavimento "sparisce" (es. in cima a una scala).
    E' il sensore di sicurezza piu' importante di tutto il robot: senza
    questo, un robot autonomo puo' cadere dalle scale.
    """

    def __init__(self):
        self._sensor = DigitalInputDevice(config.CLIFF_SENSOR_PIN)

    def floor_detected(self) -> bool:
        is_active = self._sensor.is_active
        if config.CLIFF_SENSOR_ACTIVE_MEANS_FLOOR_PRESENT:
            return is_active
        return not is_active

    def close(self):
        self._sensor.close()


class Navigator:
    """Evitamento ostacoli reattivo con 3 sensori ultrasonici + anti-caduta.

    Comportamento reattivo semplice (vai avanti, se trovi un ostacolo
    gira dalla parte piu' libera): non e' una vera mappatura/SLAM. Per
    una navigazione con mappa vera e propria servirebbe hardware
    aggiuntivo (es. LIDAR) e software dedicato (es. ROS2) - fuori dallo
    scope di un primo robot hobbistico, ma e' il prossimo upgrade
    naturale se questa versione reattiva non basta.
    """

    def __init__(self):
        self._drive = DriveBase()
        self._left_sensor = DistanceSensor(
            trigger=config.NAV_LEFT_TRIGGER_PIN, echo=config.NAV_LEFT_ECHO_PIN
        )
        self._center_sensor = DistanceSensor(
            trigger=config.NAV_CENTER_TRIGGER_PIN, echo=config.NAV_CENTER_ECHO_PIN
        )
        self._right_sensor = DistanceSensor(
            trigger=config.NAV_RIGHT_TRIGGER_PIN, echo=config.NAV_RIGHT_ECHO_PIN
        )
        self._cliff_sensor = CliffSensor()

    def _avoid_obstacle(self):
        self._drive.stop()
        self._drive.backward()
        time.sleep(0.4)

        left_clear = self._left_sensor.distance > config.NAV_OBSTACLE_DISTANCE_M
        right_clear = self._right_sensor.distance > config.NAV_OBSTACLE_DISTANCE_M

        if left_clear and not right_clear:
            self._drive.turn_left()
        elif right_clear and not left_clear:
            self._drive.turn_right()
        else:
            # entrambi i lati liberi o entrambi bloccati: gira a caso
            turn = self._drive.turn_left if random.random() < 0.5 else self._drive.turn_right
            turn()

        time.sleep(config.TURN_DURATION_S)
        self._drive.stop()

    def _handle_cliff(self):
        self._drive.stop()
        self._drive.backward()
        time.sleep(0.6)
        turn = self._drive.turn_left if random.random() < 0.5 else self._drive.turn_right
        turn()
        time.sleep(config.TURN_DURATION_S * 1.5)
        self._drive.stop()

    def step(self):
        """Un singolo passo del comportamento reattivo. Chiamalo in loop."""
        if not self._cliff_sensor.floor_detected():
            print("Attenzione: nessun pavimento rilevato, mi fermo e giro.")
            self._handle_cliff()
            return

        obstacle_ahead = self._center_sensor.distance <= config.NAV_OBSTACLE_DISTANCE_M
        if obstacle_ahead:
            self._avoid_obstacle()
        else:
            self._drive.forward()

    def close(self):
        self._drive.close()
        self._left_sensor.close()
        self._center_sensor.close()
        self._right_sensor.close()
        self._cliff_sensor.close()
