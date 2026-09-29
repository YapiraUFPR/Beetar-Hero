import stateBH
import servoBH

# valores default de cada pontuacao
SCORE_MISS = 0
SCORE_GOOD = 1
SCORE_PERFECT = 2

# define o valor de acertos em sequencia pro servo com o foguinho ficar no maximo, parece ser meio arbitrario, esperar pra ver na pratica
MAX_COMBO = 30

# vida comeca no meio e pode subir ou descer dependendo dos acertos
MAX_HEALTH = 30
DEFAULT_HEALTH = MAX_HEALTH//2

# inicia sem valor, valores default setados pela funcao de reset
currentHealth = None
comboCount = None
totalScore = None
lastJudgement = None

# criacao dos servos com normalizacao interna dos valores
servoBH.create("health_servo", 0, MAX_HEALTH, 10, 180)
servoBH.create("combo_servo_esq", 0, MAX_COMBO, 90, 180)
servoBH.create("combo_servo_dir", 0, MAX_COMBO, 90, 0)

def reset():
    global totalScore, currentHealth, comboCount, lastJudgement
    totalScore = 0
    comboCount = 0
    currentHealth = DEFAULT_HEALTH
    updateJudgement("Prepare-se !!!")
    servoBH.set("health_servo", currentHealth)
    servoBH.set("combo_servo_esq", 0)
    servoBH.set("combo_servo_dir", 0)

def updateJudgement(string_base):
    global lastJudgement

    # atualiza print da vida e estado do servo de vida
    if stateBH.countingErrors:
        string_base += f"\nVida: {currentHealth}/{MAX_HEALTH}"
        servoBH.set("health_servo", currentHealth)
    else:
        string_base += f"\nVida: Infinita"
    lastJudgement = f"{string_base}\nScore: {totalScore}"

def update(newScore):
    global lastJudgement, totalScore, comboCount, currentHealth
    
    # acerto a priori, se errar desconta
    scoreStr = ""
    totalScore += newScore # soh funciona pq newScore eh int
    comboCount = min(MAX_COMBO, comboCount + 1)
    currentHealth = min(MAX_HEALTH, currentHealth + 1)
    
    # ifs de score, soh funciona pq SCORE_<type> sao ints diferentes
    if newScore == SCORE_MISS:
        scoreStr = "Errou"
        comboCount = 0
        currentHealth = max(0, currentHealth - 2)
    elif newScore == SCORE_GOOD:
        scoreStr = "Bom"
    elif newScore == SCORE_PERFECT:
        scoreStr = "Perfeito"
    
    updateJudgement(scoreStr)

    #da pra fazer um multiplicador de pontos aqui, tipo
    # if 10 < comboCount < 20 => newScore x1.5
    # if 20 < comboCount < 30 => newScore x2
    servoBH.set("combo_servo_esq", comboCount)
    servoBH.set("combo_servo_dir", comboCount)

    if stateBH.countingErrors and currentHealth == 0:
        stateBH.runLost = True
