# Foxy Animatronic

Progetto per animatronic Foxy su Raspberry Pi: sensore ultrasonico HC-SR04
per rilevare la presenza, un servo per muovere testa/occhi e riproduzione
audio alla rilevazione.

## Collegamenti (GPIO in numerazione BCM)

| Componente          | Pin Raspberry Pi (BCM) |
|---------------------|-------------------------|
| HC-SR04 TRIG        | GPIO23                  |
| HC-SR04 ECHO        | GPIO24 (tramite partitore di tensione 5V->3.3V) |
| Servo testa (segnale)| GPIO18                 |

Modifica `foxy/config.py` se usi pin diversi.

**Attenzione:** l'ECHO dell'HC-SR04 lavora a 5V, mentre i GPIO del
Raspberry Pi leggono 3.3V. Serve un partitore di tensione (es. due
resistenze, 1kΩ e 2kΩ) tra ECHO e il GPIO, altrimenti rischi di
danneggiare il pin.

## Installazione

```bash
pip install -r requirements.txt
```

Metti i file audio (`.wav`, `.ogg` o `.mp3`) che vuoi far riprodurre a
Foxy nella cartella `sounds/`.

## Avvio

```bash
python -m foxy.main
```

## Come funziona

Il loop principale legge continuamente la distanza dal sensore
ultrasonico. Quando qualcuno si avvicina sotto la soglia configurata
(`PRESENCE_THRESHOLD_M`, default 0.5 m), Foxy:

1. riproduce un suono a caso dalla cartella `sounds/`
2. muove la testa con un'animazione fissa (destra-centro-sinistra)

Un singolo sensore ultrasonico rileva solo la **distanza**, non la
direzione: l'animazione della testa non punta davvero verso la persona,
è un gesto fisso. Per un vero inseguimento direzionale servirebbero più
sensori o una videocamera.

## Collegare il robot a Claude

Questa sessione non ha accesso fisico al Raspberry Pi: il codice va
scaricato/clonato sul Raspberry Pi stesso e lanciato lì. Se vuoi che
Claude ti aiuti a debuggare in tempo reale, copia qui gli errori o
l'output del terminale del Raspberry Pi.
