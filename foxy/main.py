import time

from foxy import config
from foxy.actuators import HeadServo
from foxy.audio import SoundPlayer
from foxy.sensors import PresenceSensor


def run():
    sensor = PresenceSensor()
    servo = HeadServo()
    player = SoundPlayer()

    last_trigger_time = 0.0

    print("Foxy pronto. In ascolto sul sensore ultrasonico...")
    try:
        while True:
            distance = sensor.distance_m()
            now = time.time()

            if distance <= config.PRESENCE_THRESHOLD_M and (
                now - last_trigger_time
            ) >= config.COOLDOWN_SECONDS:
                print(f"Presenza rilevata a {distance:.2f} m")
                last_trigger_time = now
                player.play_random()
                servo.look_at_presence()

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Arresto di Foxy...")
    finally:
        sensor.close()
        servo.close()
        player.close()


if __name__ == "__main__":
    run()
