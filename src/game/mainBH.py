import time

import ledsBH
import lcdBH
import stateBH
import filesBH
import notesBH
import scoreBH
import audioBH
import inputBH
import configBH

def select_music():
    level = None
    elements = configBH.LEVELS
    idx = 0
    input_locked = False

    def unlock_input():
        nonlocal input_locked
        while any(inputBH.buttons):
            time.sleep(0.005)
        input_locked = False

    def update_lcd():
        option = '\n'.join(elements[idx].split(" - ", 1))
        if elements == configBH.LEVELS:
            option+='\n\n\n'
        else:
            option+='\n\n'
        option += "Modo Piano" if stateBH.pianoMode else "Modo Guitarra"
        lcdBH.write(option)

    update_lcd()
    ledsBH.light()
    
    while True:
        if input_locked:
            if not any(inputBH.buttons):
                input_locked = False
            time.sleep(1 / 60)
            continue

        delta = inputBH.get_green_button() - inputBH.get_red_button()

        if delta:
            idx = (idx + delta) % len(elements)
            update_lcd()
            input_locked = True
            continue

        if inputBH.get_yellow_button():
            input_locked = True
            if not level:
                level = elements[idx]
                elements = filesBH.getPlaylist(level)
                idx = 0
                update_lcd()
                continue

            stateBH.countingErrors = level != configBH.LEVEL_EASY
            return filesBH.getMusicPath(elements[idx], level)

        if inputBH.get_blue_button() and level:
            level = None
            elements = configBH.LEVELS
            idx = 0
            update_lcd()
            input_locked = True
            continue

        if inputBH.get_orange_button():
            stateBH.pianoMode = not stateBH.pianoMode
            update_lcd()
            inputBH.reset()
            input_locked = True
            continue

        time.sleep(1 / 60)


def render(now_ms, display_txt):
    ledsBH.blank()
    notesBH.updateNotes(now_ms)
    notesBH.updateInput(now_ms)
    ledsBH.show()
    lcdBH.write(display_txt)

def ms_to_mmss(ms):
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes}:{seconds:02d}"

def start_music(music_path):
    FPS = 60
    FRAME_TIME = 1 / FPS

    def limit_fps(frame_start):
        delay = FRAME_TIME - (time.monotonic() - frame_start)
        if delay > 0:
            time.sleep(delay)

    start_ms, end_ms = filesBH.getTimestamps(music_path)
    duration_ms = end_ms - start_ms
    formated_duration_time = ms_to_mmss(duration_ms)

    event_index = 0
    events = notesBH.loadNotes(music_path)
    while event_index < len(events) and events[event_index].time_ms <= start_ms:
        event_index += 1

    audioBH.start(music_path, start_ms, end_ms)
    configBH.timeCorrection()
    base_ms = time.monotonic_ns() // 1_000_000

    while True:
        frame_start = time.monotonic()
        played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
        now_ms = played_ms + start_ms

        while event_index < len(events) and events[event_index].time_ms <= now_ms:
            if events[event_index].time_ms <= end_ms:
                e = events[event_index]
                notesBH.spawnNote(e.mask, e.time_ms, e.length_leds)
            event_index += 1

        formated_time = f"\nTime: {ms_to_mmss(min(played_ms, duration_ms))}/{formated_duration_time}"
        display_txt = scoreBH.lastJudgement + formated_time
        render(now_ms, display_txt)

        if stateBH.runLost:
            audioBH.stop()
            return 0

        if stateBH.endGame:
            audioBH.stop()
            return -1

        if played_ms >= duration_ms:
            while notesBH.hasActive():
                frame_start = time.monotonic()
                now_ms = start_ms + (time.monotonic_ns() // 1_000_000) - base_ms
                display_txt = scoreBH.lastJudgement + formated_time
                render(now_ms, display_txt)
                limit_fps(frame_start)

            delay_start_ms = now_ms
            while now_ms - delay_start_ms <= configBH.NOTE_TRAVEL_TIME_MS:
                frame_start = time.monotonic()
                now_ms = start_ms + (time.monotonic_ns() // 1_000_000) - base_ms
                display_txt = scoreBH.lastJudgement + formated_time
                render(now_ms, display_txt)
                limit_fps(frame_start)

            audioBH.stop()
            return scoreBH.totalScore

        limit_fps(frame_start)

def main():
    # retorna somente depois de conectar o input
    inputBH.start()

    while True:
        # reseta estados, como 'runLost', 'total_score' e posicao dos servos
        scoreBH.reset()
        stateBH.reset()

        # em menu, permite modificacao de canhoto/destro e guitarra/piano
        stateBH.onMenu = True
        music = select_music()
        stateBH.onMenu = False
        
        final_score = start_music(music)

        match final_score:
            case -1:
                lcdBH.write("Jogo Cancelado")
            case 0:
                lcdBH.write("Jogo Perdido")
            case _:
                lcdBH.write(f"Pontuacao Final:\n{final_score}")
        ledsBH.clear()
        time.sleep(1)

        if final_score > 0:
            ledsBH.blinkLanes()
            ledsBH.slideLanes()
            ledsBH.blinkLanes()
        else:
            ledsBH.blinkRed()


if __name__ == "__main__":
    main()
