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

## Riconoscimento facciale e vocale

Sistema di riconoscimento "famiglia" per distinguere te, tua mamma e
gli altri membri della famiglia da estranei, usando la telecamera e il
microfono del Raspberry Pi.

### Volto

```bash
python -m foxy.enroll_face "Mario"      # scatta 30 foto automaticamente dalla webcam
python -m foxy.enroll_face "Mamma"      # ripeti per ogni persona
python -m foxy.train_face               # addestra il modello su tutte le persone registrate
python -m foxy.demo_face                # test: stampa il nome riconosciuto in tempo reale
```

### Voce

```bash
python -m foxy.enroll_voice "Mario"     # registra 10 campioni da 3s a microfono
python -m foxy.enroll_voice "Mamma"     # ripeti per ogni persona (minimo 2 persone)
python -m foxy.train_voice              # addestra il classificatore
python -m foxy.demo_voice               # test: registra 3s e dice chi ha parlato
```

Le foto, i campioni audio e i modelli addestrati finiscono in
`face_dataset/`, `voice_dataset/` e `models/` — cartelle escluse dal
repository (`.gitignore`) perché contengono dati personali/di famiglia.
Vanno tenute solo sul Raspberry Pi.

**Limiti onesti:** il riconoscimento facciale con LBPH (invece di reti
neurali più pesanti tipo `dlib`/`face_recognition`) è scelto perché
gira bene anche su un Raspberry Pi, ma è meno robusto con cambi di
luce/angolazione: se sbaglia spesso, registra più foto in condizioni di
luce diverse. Il riconoscimento vocale con MFCC+SVM funziona bene per
poche persone (famiglia), non è pensato per scalare a decine di voci.

## Prossimi passi (roadmap)

Il progetto è ambizioso (corpo completo, locomozione autonoma, IA
affettiva, interazione con videogiochi): lo costruiamo a fasi.

1. ~~Testa/volto espressivo di base~~ (servo testa, impostato)
2. **Riconoscimento volto + voce** (questa fase)
3. Personalità IA conversazionale (chat calda/empatica, conoscenza sui
   videogiochi)
4. Locomozione autonoma su ruote/cingoli nascosti + evitamento ostacoli
5. Fase sperimentale: interazione con videogiochi (commento via
   videocamera sullo schermo, o input automatico per giochi semplici)

## Collegare il robot a Claude

Questa sessione non ha accesso fisico al Raspberry Pi: il codice va
scaricato/clonato sul Raspberry Pi stesso e lanciato lì. Se vuoi che
Claude ti aiuti a debuggare in tempo reale, copia qui gli errori o
l'output del terminale del Raspberry Pi.
