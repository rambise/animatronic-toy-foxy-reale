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
