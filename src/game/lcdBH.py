import time
import threading

from RPLCD.i2c import CharLCD
from RPi import GPIO

GPIO.setwarnings(False)

COLS = 20
ROWS = 4
SCROLL_INTERVAL = 1

lcd = CharLCD("PCF8574", address=0x27, cols=COLS, rows=ROWS)

lines = [""] * ROWS
scroll = [0] * ROWS
displayed = [" " * COLS for _ in range(ROWS)]

lock = threading.Lock()
condition = threading.Condition(lock)

generation = 0
clearRequested = False
homeRequested = False
running = True


def _changed():
    global generation
    generation += 1
    condition.notify()


def clear():
    global clearRequested

    with condition:
        for i in range(ROWS):
            lines[i] = ""
            scroll[i] = 0

        clearRequested = True
        _changed()


def home():
    global homeRequested

    with condition:
        homeRequested = True
        _changed()


def reset():
    global clearRequested, homeRequested

    with condition:
        for i in range(ROWS):
            lines[i] = ""
            scroll[i] = 0

        clearRequested = True
        homeRequested = True
        _changed()


def setLine(row, text):
    if not 0 <= row < ROWS:
        return

    text = str(text).strip()

    with condition:
        if lines[row] == text:
            return

        lines[row] = text
        scroll[row] = 0
        _changed()


def write(string):
    text_lines = str(string).split("\n")

    with condition:
        changed = False

        for i in range(ROWS):
            text = text_lines[i].strip() if i < len(text_lines) else ""

            if lines[i] != text:
                lines[i] = text
                scroll[i] = 0
                changed = True

        if changed:
            _changed()


def _visible(text, offset):
    if len(text) <= COLS:
        return text.ljust(COLS)

    loop = text + "   "
    pos = offset % len(loop)

    while len(loop) < pos + COLS:
        loop += loop

    return (loop + loop)[pos:pos + COLS]


def _write_diff(row, old, new):
    i = 0

    while i < COLS:
        while i < COLS and old[i] == new[i]:
            i += 1

        if i >= COLS:
            return

        start = i

        while i < COLS and old[i] != new[i]:
            i += 1

        lcd.cursor_pos = (row, start)
        lcd.write_string(new[start:i])


def _update(target, do_clear, do_home):
    global displayed

    if do_clear:
        lcd.clear()
        displayed = [" " * COLS for _ in range(ROWS)]

    if do_home:
        lcd.home()

    for row in range(ROWS):
        old = displayed[row]
        new = target[row]

        if old == new:
            continue

        _write_diff(row, old, new)
        displayed[row] = new


def _worker():
    global clearRequested, homeRequested

    processed_generation = -1
    last_scroll = time.monotonic()

    while running:
        with condition:
            while True:
                now = time.monotonic()
                has_scroll = any(len(line) > COLS for line in lines)

                if generation != processed_generation:
                    break

                if has_scroll:
                    remaining = SCROLL_INTERVAL - (now - last_scroll)

                    if remaining <= 0:
                        break

                    condition.wait(timeout=remaining)
                else:
                    condition.wait()

            now = time.monotonic()

            if now - last_scroll >= SCROLL_INTERVAL:
                for i in range(ROWS):
                    if len(lines[i]) > COLS:
                        scroll[i] += 1

                last_scroll = now

            target = [_visible(lines[i], scroll[i]) for i in range(ROWS)]

            do_clear = clearRequested
            do_home = homeRequested

            clearRequested = False
            homeRequested = False

            snapshot_generation = generation

        # I2C fica totalmente fora do lock.
        _update(target, do_clear, do_home)

        with condition:
            processed_generation = snapshot_generation


reset()

threading.Thread(target=_worker, daemon=True, name="LCD").start()
