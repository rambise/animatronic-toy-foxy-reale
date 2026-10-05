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

## IA conversazionale (chat + voce)

Foxy parla con te usando l'API Claude, con una personalità calda e
affettuosa (vedi `foxy/personality.py`), speech-to-text offline (Vosk) e
text-to-speech offline (Piper) — l'unica parte che richiede internet è
la chiamata all'IA per generare la risposta.

### Setup

1. **Chiave API Claude**: crea una chiave su
   [console.anthropic.com](https://console.anthropic.com/) e impostala
   sul Raspberry Pi:
   ```bash
   echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.bashrc
   source ~/.bashrc
   ```
2. **Vosk** (speech-to-text): scarica un modello italiano da
   [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
   (consigliato `vosk-model-small-it-0.22`, leggero) ed estrailo in
   `models/stt/vosk-model-it`.
3. **Piper** (text-to-speech): scarica il binario precompilato per la
   tua architettura (incluso ARM/Raspberry Pi) e una voce italiana da
   [github.com/rhasspy/piper](https://github.com/rhasspy/piper), metti
   il binario nel PATH e il modello voce in
   `models/tts/it_IT-voice.onnx`.

### Avvio

```bash
python -m foxy.conversation
```

Quando il sensore di presenza rileva qualcuno, Foxy:

1. prova a riconoscerti dal volto e **ti saluta lei per prima**, di sua
   iniziativa, se sei qualcuno che conosce (non aspetta che tu parli)
2. ascolta (non serve premere nulla, capisce da solo quando
   inizi/finisci di parlare) e risponde con l'IA quando le parli
3. se resti vicino senza parlarle per un po' (`CHAT_IDLE_COMMENT_AFTER_S`,
   default 25s), **dice qualcosa di sua iniziativa** invece di startene
   zitta — un'osservazione, una domanda, una battuta

In ogni risposta parla con Piper e fa un piccolo gesto con la testa in
base all'emozione della risposta.

**Limite onesto sul "volersi bene":** il calore/affetto di Foxy è una
personalità scritta nel prompt (`foxy/personality.py`), non coscienza o
emozioni reali — lo stesso principio di un Tamagotchi o un Furby. È un
compagno con cui interagire, non un essere senziente.

## Locomozione autonoma

Foxy si muove da solo su ruote o cingoli nascosti sotto il corpo
(**non** cammina su gambe vere: per un bipede che cammina in autonomia
servirebbe un progetto di robotica molto più avanzato — equilibrio,
motori ad alta coppia, feedback continuo). Evita gli ostacoli con 3
sensori ultrasonici e ha un sensore anti-caduta per non cadere dalle
scale.

### Collegamenti aggiuntivi (BCM)

| Componente | Pin |
|---|---|
| Motore sinistro (avanti/indietro) | GPIO20 / GPIO21 |
| Motore destro (avanti/indietro) | GPIO16 / GPIO12 |
| Ultrasonico sinistra TRIG/ECHO | GPIO5 / GPIO6 |
| Ultrasonico destra TRIG/ECHO | GPIO13 / GPIO19 |
| Sensore anti-caduta (IR verso il pavimento) | GPIO26 |

Il sensore ultrasonico centrale di navigazione riusa i pin del sensore
di presenza (GPIO23/24) — presuppone che sia montato in basso e rivolto
in avanti. Se hai un sensore dedicato, cambia `NAV_CENTER_*_PIN` in
`foxy/config.py`.

### Avvio

```bash
python -m foxy.autonomous_drive
```

**Prima di lasciarla libera per casa:**
1. Testalo con le ruote sollevate da terra per controllare che "avanti"
   vada davvero avanti (altrimenti inverti i fili di un motore).
2. Testa il sensore anti-caduta tenendo Foxy sul bordo di un tavolo:
   deve fermarsi e girare, non "cadere".
3. La prima volta, resta vicino e pronto a staccare l'alimentazione.

## Companion videogiochi (sperimentale)

```bash
python -m foxy.game_companion
```

Punta una telecamera verso lo schermo: Foxy guarda e commenta a voce
ogni tanto quello che vede, usando la vision dell'IA.

**Limite onesto:** questo NON fa "giocare" Foxy con te — è una compagna
che guarda e commenta, non preme pulsanti e non conosce lo stato interno
del gioco. Automatizzare davvero l'input richiederebbe hardware
aggiuntivo (es. un microcontrollore come gamepad USB) ed è realistico
solo per giochi molto semplici.

## Roadmap

Il progetto è ambizioso (corpo completo, locomozione autonoma, IA
affettiva, interazione con videogiochi): lo stiamo costruendo a fasi.

1. ~~Testa/volto espressivo di base~~ (servo testa)
2. ~~Riconoscimento volto + voce~~
3. ~~Personalità IA conversazionale (chat calda/empatica + voce)~~
4. ~~Locomozione autonoma su ruote/cingoli nascosti + evitamento ostacoli~~
5. ~~Companion sperimentale per videogiochi~~ (commento, non "gioca")

Prossimi possibili step, da valutare in base a cosa funziona meglio dal
vivo:
- Più servo per espressioni facciali vere (mascella, palpebre, orecchie)
  invece del solo movimento della testa
- Braccia/mani con più gradi di libertà
- Navigazione con mappa (SLAM) se l'evitamento reattivo non basta in
  casa tua

## Collegare il robot a Claude

Questa sessione non ha accesso fisico al Raspberry Pi: il codice va
scaricato/clonato sul Raspberry Pi stesso e lanciato lì. Se vuoi che
Claude ti aiuti a debuggare in tempo reale, copia qui gli errori o
l'output del terminale del Raspberry Pi.
