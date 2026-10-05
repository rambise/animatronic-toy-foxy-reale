# Numerazione pin BCM (GPIOxx), non i numeri fisici del connettore.
# Modifica questi valori in base al tuo cablaggio reale.

# HC-SR04 ultrasonico
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24
ULTRASONIC_MAX_DISTANCE_M = 2.0  # oltre questa distanza il sensore legge "nessuno"

# Servo per testa/occhi
HEAD_SERVO_PIN = 18

# Soglia di rilevamento presenza, in metri
PRESENCE_THRESHOLD_M = 0.5

# Cartella con i file audio da riprodurre alla rilevazione
SOUNDS_DIR = "sounds"

# Intervallo minimo tra due attivazioni consecutive, in secondi
# (evita che Foxy "scatti" in continuazione se qualcuno resta fermo davanti)
COOLDOWN_SECONDS = 4.0

# --- Riconoscimento facciale ---
CAMERA_INDEX = 0
FACE_DATASET_DIR = "face_dataset"  # foto di addestramento, una sottocartella per persona
FACE_MODEL_PATH = "models/face_model.yml"
FACE_LABELS_PATH = "models/face_labels.json"
# LBPH: la "confidenza" e' in realta' una distanza, quindi piu' bassa = corrispondenza migliore.
# Sopra questa soglia il volto viene considerato sconosciuto.
FACE_CONFIDENCE_THRESHOLD = 70

# --- Riconoscimento vocale ---
VOICE_SAMPLE_RATE = 16000
VOICE_DATASET_DIR = "voice_dataset"  # campioni audio di addestramento, una sottocartella per persona
VOICE_MODEL_PATH = "models/voice_model.pkl"
# Qui invece piu' alta = piu' sicura (e' una probabilita' 0-1).
VOICE_CONFIDENCE_THRESHOLD = 0.6

# --- IA conversazionale (API Claude) ---
# La chiave va messa nella variabile d'ambiente ANTHROPIC_API_KEY, MAI scritta
# qui nel codice. Su Raspberry Pi: aggiungi "export ANTHROPIC_API_KEY=sk-ant-..."
# al tuo ~/.bashrc, oppure creane uno nuovo su https://console.anthropic.com/
CLAUDE_MODEL = "claude-sonnet-5-5"
CHAT_MAX_HISTORY_TURNS = 12  # quante battute di conversazione ricordare
CHAT_MAX_RESPONSE_TOKENS = 300  # risposte brevi: Foxy parla, non scrive saggi

# --- Speech-to-text offline (Vosk) ---
# Scarica un modello italiano da https://alphacephei.com/vosk/models
# (consigliato: vosk-model-small-it-0.22, leggero per Raspberry Pi)
VOSK_MODEL_PATH = "models/stt/vosk-model-it"
VAD_SILENCE_RMS_THRESHOLD = 500  # sotto questa soglia il microfono e' considerato "silenzio"
VAD_SILENCE_DURATION_S = 1.2  # silenzio continuo che fa capire a Foxy che hai finito di parlare
VAD_MAX_RECORDING_S = 12  # taglio di sicurezza se parli troppo a lungo

# --- Text-to-speech offline (Piper) ---
# Scarica una voce italiana da https://github.com/rhasspy/piper/blob/master/VOICES.md
PIPER_BINARY = "piper"  # deve essere nel PATH, vedi README per l'installazione
PIPER_MODEL_PATH = "models/tts/it_IT-voice.onnx"
TTS_SCRATCH_WAV_PATH = "/tmp/foxy_tts_output.wav"

# --- Trazione (ruote/cingoli nascosti) ---
MOTOR_LEFT_FORWARD_PIN = 20
MOTOR_LEFT_BACKWARD_PIN = 21
MOTOR_RIGHT_FORWARD_PIN = 16
MOTOR_RIGHT_BACKWARD_PIN = 12
DRIVE_SPEED = 0.6  # 0.0-1.0
TURN_SPEED = 0.5  # 0.0-1.0
TURN_DURATION_S = 0.6  # durata di una svolta: da calibrare a occhio sul tuo robot

# --- Navigazione autonoma ---
# Tre sensori ultrasonici aggiuntivi (diversi da ULTRASONIC_*_PIN sopra, che
# restano dedicati al rilevamento presenza/interazione). Questi tre sono
# montati sul telaio, rivolti in avanti, per evitare ostacoli mentre si muove.
NAV_LEFT_TRIGGER_PIN = 5
NAV_LEFT_ECHO_PIN = 6
NAV_CENTER_TRIGGER_PIN = 23  # puo' riusare il sensore di presenza se montato basso e in avanti
NAV_CENTER_ECHO_PIN = 24
NAV_RIGHT_TRIGGER_PIN = 13
NAV_RIGHT_ECHO_PIN = 19
NAV_OBSTACLE_DISTANCE_M = 0.3
NAV_LOOP_INTERVAL_S = 0.1

# Sensore anti-caduta (fondamentale!): un sensore IR rivolto verso il
# pavimento, montato sotto il telaio, che rileva quando il pavimento "sparisce"
# (es. in cima a una scala). Senza questo, un robot autonomo puo' cadere dalle
# scale e rompersi (o farsi male a chi gli sta vicino).
CLIFF_SENSOR_PIN = 26
# Molti moduli IR economici restituiscono True quando RILEVANO il pavimento
# (riflessione) e False quando non lo rilevano (vuoto/scalino). Se il tuo
# modulo funziona al contrario, cambia questo valore.
CLIFF_SENSOR_ACTIVE_MEANS_FLOOR_PRESENT = True

# --- Companion videogiochi (sperimentale) ---
GAME_CAMERA_INDEX = 0  # puoi usare una seconda telecamera puntata sullo schermo
GAME_COMMENT_INTERVAL_S = 15
