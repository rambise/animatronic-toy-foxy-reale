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
