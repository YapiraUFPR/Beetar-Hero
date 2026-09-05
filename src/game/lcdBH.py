import time
import threading

from RPLCD.i2c import CharLCD
from RPi import GPIO

GPIO.setwarnings(False)

COLS = 20
ROWS = 4

lcd = CharLCD("PCF8574", address=0x27, cols=COLS, rows=ROWS)

lines = [""] * ROWS
last = [""] * ROWS
scroll = [0] * ROWS

lock = threading.Lock()
lastScroll = time.time()

clearRequested = False
homeRequested = False

def clear():
    global clearRequested

    with lock:
        for i in range(ROWS):
            lines[i] = ""
            last[i] = ""
            scroll[i] = 0

        clearRequested = True

def home():
    global homeRequested

    with lock:
        homeRequested = True

def reset():
    clear()
    home()

def setLine(row, text):
    if row < 0 or row >= ROWS:
        return

    text = str(text).strip()

    with lock:
        if text != lines[row]:
            lines[row] = text
            scroll[row] = 0
            last[row] = ""

def write(string):
    text_lines = str(string).split('\n')

    with lock:
        for i in range(ROWS):
            text = text_lines[i] if i < len(text_lines) else ""
            text = str(text).strip()

            if text != lines[i]:
                lines[i] = text
                scroll[i] = 0
                last[i] = ""

def update():
    global lastScroll, clearRequested, homeRequested

    now = time.time()

    with lock:
        doClear = clearRequested
        doHome = homeRequested

        clearRequested = False
        homeRequested = False

        if now - lastScroll > 0.5:
            lastScroll = now

            for i in range(ROWS):
                if len(lines[i]) > COLS:
                    scroll[i] += 1

        shows = []

        for i in range(ROWS):
            text = lines[i]

            if len(text) <= COLS:
                show = text.ljust(COLS)
            else:
                loop = text + "   "
                pos = scroll[i] % len(loop)
                show = (loop + loop)[pos:pos + COLS]

            shows.append(show)

    if doClear:
        lcd.clear()

    if doHome:
        lcd.home()

    for i, show in enumerate(shows):
        with lock:
            changed = show != last[i]

        if changed:
            lcd.cursor_pos = (i, 0)
            lcd.write_string(show)

            with lock:
                last[i] = show

def worker():
    while True:
        update()
        time.sleep(0.01)

reset()
threading.Thread(target=worker, daemon=True).start()
