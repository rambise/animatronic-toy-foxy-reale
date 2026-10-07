"""Locomozione autonoma: Cassidy gira per casa evitando ostacoli.

Uso:
    python -m foxy.autonomous_drive

ATTENZIONE: testa sempre prima con il robot sollevato da terra (ruote
libere di girare a vuoto) per controllare che le direzioni dei motori
siano corrette, prima di farlo camminare davvero sul pavimento. Se
"avanti" lo fa andare indietro, inverti i fili di quel motore oppure
scambia i pin FORWARD/BACKWARD in config.py.

Testa anche il sensore anti-caduta da solo prima di lasciare Cassidy libero
vicino alle scale: tienilo sollevato sul bordo di un tavolo e controlla
che si fermi e giri invece di "cadere".
"""
import time

from foxy import config
from foxy.navigation import Navigator


def run():
    navigator = Navigator()
    print("Cassidy si muove in autonomia. CTRL+C per fermarlo.")
    try:
        while True:
            navigator.step()
            time.sleep(config.NAV_LOOP_INTERVAL_S)
    except KeyboardInterrupt:
        print("Arresto di Cassidy.")
    finally:
        navigator.close()


if __name__ == "__main__":
    run()
