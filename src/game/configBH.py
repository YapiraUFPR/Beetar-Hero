import time
import os
import filesBH

# disposicao dos leds
NUM_LANES = 5
LEDS_PER_LANE = 24
HIT_LINE = 20

# arquivo csv com 'user;score' onde ficam salvos as pontuacoes finais
# relativo ao ponto de entrada comum "run.sh"
FINAL_SCORES_LOG_FILE = "src/game/final_scores.csv"

# velocidade das notas
NOTE_TRAVEL_TIME_MS = 3000
NOTE_SPEED = (LEDS_PER_LANE - 1) / NOTE_TRAVEL_TIME_MS

# texto exibido no display lcd e nome dos diretorios dentro de 'Musicas/'
LEVEL_ORDER = ["Facil", "Medio", "Dificil", "Expert"]
LEVELS = [l for l in LEVEL_ORDER if l in os.listdir(filesBH.AUDIO_ROOT)]


# delay adicionado entre inicio da musica e inicio das notas
# necessario porque nossa HIT_LINE nao condiz com a original
def timeCorrection():
    time.sleep(1)
