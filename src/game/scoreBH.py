import stateBH
import servoBH

# valores default de cada pontuacao
SCORE_MISS = 0
SCORE_GOOD = 1
SCORE_PERFECT = 2
SCORE_SUSTAIN = 1 # pra fazer o sustain dar ponto constante // ainda n feito

# define o valor de acertos em sequencia pro servo com o foguinho ficar no maximo, parece ser meio arbitrario, esperar pra ver na pratica
MAX_COMBO_COUNT = 30

# talvez trocar nomes de  variaveis pra ter mais relacao com 'vida' do que 'erro'
# vida comeca no meio e pode subir ou descer dependendo dos acertos
MAX_ERROR_COUNT = 30
DEFAULT_ERROR_COUNT = MAX_ERROR_COUNT//2

# inicia sem valor, valores default setados pela funcao de reset
errorCount = None
comboCount = None
totalScore = None
lastJudgement = None

# criacao dos servos com normalizacao interna dos valores
servoBH.create("score_servo", 0, MAX_ERROR_COUNT)
servoBH.create("combo_servo", 0, MAX_COMBO_COUNT)

def reset():
    global totalScore, errorCount, lastJudgement
    lastJudgement = "Prepare-se !!!"
    totalScore = 0
    comboCount = 0
    errorCount = DEFAULT_ERROR_COUNT
    servoBH.set("score_servo", errorCount)
    servoBH.set("combo_servo", 0)

def update(newScore):
    global lastJudgement, totalScore, errorCount
    
    # se errou e a contagem de erros esta ativada, atualiza contador
    if stateBH.countingErrors:
        if newScore == SCORE_MISS:
            errorCount += 1
        elif errorCount > 0:
            errorCount += -1

    scoreStr = ""
    comboCount += 1
    if newScore == SCORE_MISS:
        comboCount = 0
        scoreStr = "Errou"
        if stateBH.countingErrors:
            scoreStr += f"{errorCount}/{MAX_ERROR_COUNT}"

    elif newScore == SCORE_GOOD:
        scoreStr = 'Bom'
    else: # if new_score == SCORE_PERFECT:
        scoreStr = 'Perfeito'
 
    #da pra fazer um multiplicador de pontos aqui, tipo
    # if 10 < comboCount < 20 => pontos x1.5
    # if 20 < comboCount < 30 => pontos x2
    servoBH.set("score_servo", errorCount)
    servoBH.set("combo_servo", comboCount)

    totalScore += newScore
    # printar o numero de combo tambem sera? talvez soh o foguinho do servo fique melhor
    lastJudgement = f"{scoreStr}\nScore: {totalScore}"
    
    if stateBH.countingErrors and errorCount >= MAX_ERROR_COUNT:
        stateBH.runLost = True
