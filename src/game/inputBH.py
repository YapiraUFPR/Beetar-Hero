import time
import socket
import serial
import threading

import configBH
import stateBH
from gpiozero import Button

#estado atual dos botoes
buttons = None
auto_holding_button = None

def reset():   
    global buttons, auto_holding_button
    buttons = [0] * configBH.NUM_LANES
    auto_holding_button = 0 

def get_green_button():        return buttons[0]
def get_red_button():          return buttons[1]
def get_yellow_button():       return buttons[2]
def get_blue_button():         return buttons[3]
def get_orange_button():       return buttons[4]
def get_auto_holding_button(): return auto_holding_button

def updatePressedKeys(i, state, fromPiano):
    global auto_holding_button

    if fromPiano != stateBH.pianoMode:
        return

    if i == 5:  # sexto botao eh a palheta (indexado em zero)
        auto_holding_button = state
    else: # botoes de nota normal
#        i = configBH.NUM_LANES - 1 - i
        buttons[i] = state

def setupPianoButton(i, pin):
    b = Button(pin, pull_up=True, bounce_time=0.1)
    b.when_pressed = lambda i=i: updatePressedKeys(i, 1, True)
    b.when_released = lambda i=i: updatePressedKeys(i, 0, True)
    return b

PIANO_PINS = [16, 8, 25, 24, 23]
pianoInput = [setupPianoButton(i, pin) for i, pin in enumerate(PIANO_PINS)]

ESP32_MAC = "30:76:F5:E5:B8:DA"
ESP32_BT_PORT = 1
ESP32_SERIAL_PORT = "/dev/ttyUSB0"
ESP32_BAUD = 115200

def process(line):
    if line.startswith("BTN/"):
        topic, value = line.strip().split(':')
        topic = topic.split('/')[1]
        updatePressedKeys(int(topic), int(value), False)

def connect(connection_type):
    while True:
        try:
            if connection_type == "bluetooth":
                c = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                c.connect((ESP32_MAC, ESP32_BT_PORT))
            else:
                c = serial.Serial(ESP32_SERIAL_PORT, ESP32_BAUD, timeout=1)

            print(f"ESP32 {connection_type} conectado")
            return c

        except Exception as e:
            print(f"Erro {connection_type}: {e}")
            time.sleep(1)

def bluetoothWorker(sock):
    while True:
        try:
            f = sock.makefile('r')
            for line in f:
                process(line)
        except:
            pass

        try: f.close()
        except: pass
        sock.close()
        sock = connect("bluetooth")

def serialWorker(ser):
    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                process(line)
        except:
            ser.close()
            ser = connect("serial")

def start(connection_type="serial"):
    con_type = connection_type.lower()
    c = connect(con_type)
    worker = bluetoothWorker if con_type == "bluetooth" else serialWorker
    reset()
    threading.Thread(target=worker, args=(c,), daemon=True).start()
