import time
import os
import filesBH

# disposicao dos leds
NUM_LANES = 5
LEDS_PER_LANE = 24
HIT_LINE = 20

# velocidade das notas
NOTE_TRAVEL_TIME_MS = 3000
NOTE_SPEED = (LEDS_PER_LANE - 1) / NOTE_TRAVEL_TIME_MS

# texto exibido no display lcd e nome dos diretorios dentro de 'Musicas/'
LEVELS = os.listdir(filesBH.AUDIO_ROOT)
LEVEL_EASY = "Facil" # modo que nao conta erros, mesmo nome da pasta de dificuldade

# delay adicionado entre inicio da musica e inicio das notas
# necessario porque nossa HIT_LINE nao condiz com a original
def timeCorrection():
    time.sleep(0.9)
