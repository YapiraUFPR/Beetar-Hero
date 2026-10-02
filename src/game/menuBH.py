import time
import csv
import os

import ledsBH
import lcdBH
import filesBH
import inputBH
import configBH
import stateBH

def update_option(elements, idx):
    option = '\n'.join(elements[idx].split(" - ", 1))
    if elements == configBH.LEVELS:
        option+='\n\n\n'
    else:
        option+='\n\n'
    option += "Modo Piano" if stateBH.pianoMode else "Modo Guitarra"
    lcdBH.write(option)

def select_music():
    level = None
    elements = configBH.LEVELS
    idx = 0
    input_locked = False

    update_option(elements, idx)
    ledsBH.light()
    
    while True:
        update_option(elements, idx)

        if input_locked:
            if not any(inputBH.buttons):
                input_locked = False
            time.sleep(1 / 60)
            continue

        delta = inputBH.get_green_button() - inputBH.get_red_button()
        if delta:
            idx = (idx + delta) % len(elements)
            input_locked = True
            continue

        if inputBH.get_yellow_button():
            input_locked = True
            if not level:
                level = elements[idx]
                elements = filesBH.getPlaylist(level)
                idx = 0
                continue
            
            # dificuldade 'Facil' nao conta erros
            stateBH.countingErrors = level != configBH.LEVELS[0]
            return filesBH.getMusicPath(elements[idx], level)

        if inputBH.get_blue_button() and level:
            level = None
            elements = configBH.LEVELS
            idx = 0
            input_locked = True
            continue

        if inputBH.get_orange_button():
            stateBH.pianoMode = not stateBH.pianoMode
            inputBH.reset()
            input_locked = True
            continue

        time.sleep(1 / 60)

def saveFinalScore(score):
    ledsBH.light()

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    name = ""
    char_idx = 0
    input_locked = False

    blink_time = time.time()
    blink_on = True
    while True:
        if time.time() - blink_time >= 0.5:
            blink_on = not blink_on
            blink_time = time.time()

        current_char = chars[char_idx] if blink_on else "_"
        preview = (name + current_char + "_" * 10)[:10]
        lcdBH.write(f"Digite seu nome:\n{preview}\nScore: {score}")

        if input_locked:
            if not any(inputBH.buttons):
                input_locked = False
            time.sleep(1 / 60)
            continue

        delta = inputBH.get_green_button() - inputBH.get_red_button()
        if delta:
            char_idx = (char_idx + delta) % len(chars)
            input_locked = True
            continue

        if inputBH.get_yellow_button():
            if len(name) < 10:
                name += chars[char_idx]
                char_idx = 0
            input_locked = True
            continue

        if inputBH.get_blue_button():
            if name:
                name = name[:-1]
            input_locked = True
            continue

        if inputBH.get_orange_button():
            name = name.strip()
            if not name:
                name = "Anonimo"
            break

        time.sleep(1 / 60)

    scores = []
    if os.path.exists(configBH.FINAL_SCORES_LOG_FILE):
        with open(configBH.FINAL_SCORES_LOG_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    scores.append({"name": row[0], "score": int(row[1]), "new": False})
    
    # adiciona novo score a lista e ordena
    scores.append({"name": name, "score": score, "new": True})
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    position = next(i for i, entry in enumerate(scores, start=1) if entry["new"])

    with open(configBH.FINAL_SCORES_LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "score"])
        for entry in scores:
            writer.writerow([entry["name"], entry["score"]])

    lines = []
    for i in range(3):
        if i < len(scores):
            entry = scores[i]
            lines.append(f"{i + 1:>2}o {entry['name']:<10}{entry['score']:>6}")
        else:
            lines.append("")

    lines.append(f"{position:>2}o {name:<10}{entry['score']:>6}")
    lcdBH.write("\n".join(lines))
    time.sleep(5)
