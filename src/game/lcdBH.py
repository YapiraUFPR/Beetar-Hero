import time
from RPLCD.i2c import CharLCD
from RPi import GPIO
GPIO.setwarnings(False)

# cria lcd via modulo i2c
lcd = CharLCD("PCF8574", address=0x27, cols=20, rows=4)

# dimensoes usadas pelo LCD
COLS = lcd.cols
ROWS = lcd.rows

lines = [""] * ROWS
last = [""] * ROWS
scroll = [0] * ROWS

lastScroll = time.time()

# limpa LCD e buffers
def clear():
    lcd.clear()

    for i in range(ROWS):
        lines[i] = ""
        last[i] = ""
        scroll[i] = 0

# volta cursor para origem
def home():
    lcd.home()

# limpa tudo
def reset():
    clear()
    lcd.home()

# define texto de uma linha
def setLine(row, text):
    if row < 0 or row >= ROWS:
        return

    text = str(text).strip()

    if text != lines[row]:
        lines[row] = text
        scroll[row] = 0
        last[row] = ""

# escreve texto podendo conter N linhas
def write(string):
    text_lines = str(string).split('\n')

    for i in range(ROWS):
        setLine(i, text_lines[i] if i < len(text_lines) else "")

    update()

# atualiza LCD e scrolling
def update():
    global lastScroll

    now = time.time()

    if now - lastScroll > 0.5:
        lastScroll = now

        for i in range(ROWS):
            if len(lines[i]) > COLS:
                scroll[i] += 1

    for i in range(ROWS):
        text = lines[i]

        if len(text) <= COLS:
            show = text.ljust(COLS)
        else:
            loop = text + "   "
            pos = scroll[i] % len(loop)
            show = (loop + loop)[pos:pos + COLS]

        if show != last[i]:
            lcd.cursor_pos = (i, 0)
            lcd.write_string(show)
            last[i] = show

reset()
