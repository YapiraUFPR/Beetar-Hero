import time
import socket
import threading
import configBH
import stateBH
from gpiozero import Button
import traceback

# vetor correspondente as teclas de cada lane
buttons = [0] * configBH.NUM_LANES
# salva estado de apertado ou nao pra garantir que nao haja skip em algum loop
pressed = [0] * configBH.NUM_LANES

# funcao unica que altera os valores das notas apertadas
def updatePressedKeys(button_id, state, fromPiano):
    # ambos falsos ou ambos verdadeiros
    if fromPiano == stateBH.pianoMode:
        buttons[button_id] = state
        if state:
            pressed[btn_id-1] = 1

# configura funcoes disparadas por apertar/soltar o botao
def setupPianoButton(i, pin):
    b = Button(pin, pull_up=True, bounce_time=0.1)
    b.when_pressed = lambda i=i: updatePressedKeys(i, 1, True)
    b.when_released = lambda i=i: updatePressedKeys(i, 0, True)
    return b

# cria botoes do piano
PIANO_PINS = [16, 8, 25, 23, 24] # na ordem das cores
pianoInput = [setupPianoButton(i, pin) for i, pin in enumerate(PIANO_PINS)]

# pra conectar no esp32 da guitarra
ESP32_MAC = "30:76:F5:E5:B8:DA"
ESP32_PORT = 1

# fica tentando conectar no esp32 ateh conseguir
def connectGuitar():
    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)        
            sock.connect((ESP32_MAC, ESP32_PORT))
            print("ESP32 Bluetooth Conectado")
            print("Verfique se a música aparece no display", flush=True)
            return sock

        except Exception as e:
            print(f"Erro: {e}")

            traceback.print_exc()
            if sock is not None:
                try:
                    sock.close()
                except:
                    pass

            time.sleep(1)

# recebe e atribui 0 (botao foi solto) ou 1 (botao foi apertado) para cada botao
def bluetoothWorker(sock):
    while True:
        f = sock.makefile('r')

        try:
            for line in f:
                line = line.strip()
                
                # o ideal seria simplificar, mas com o esp32 morto
                # eh melhor deixar quieto isso por enquanto
                if line.startswith("BTN/"):
                    topic, value = line.split(':')
                    btn_id = int(topic.split('/')[1])
                    updatePressedKeys(btn_id - 1, int(value), False)


        except Exception as e:
            print(f"Bluetooth Thread Error: {e}")

        finally:
            f.close()
            sock.close()

# inicia processamento
def start():
    sock = connectGuitar()
    threading.Thread(target=bluetoothWorker, args=(sock,), daemon=True).start()
