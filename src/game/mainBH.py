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
    lcdBH.clear()
    ledsBH.light()

    # comeca escolhendo pela dificuldade
    elements = configBH.LEVELS
    level = None
    idx = 0
    input_locked = False # flag pra mudar apenas 1 vez por aperto de botao
    
    while True:
        # thread separada permite alterar estado da ordem das cores
        if stateBH.sideSwitchChanged:
            stateBH.sideSwitchChanged = False
            lcdBH.write("Verifique a\nOrdem das Cores")
            ledsBH.light()
            time.sleep(1)

        # todos os botoes soltos liberam o input pra apertar de novo
        if all(not b for b in inputBH.buttons):
            input_locked = False

        # nao processa inputs enquanto estiver bloqueado
        if input_locked:
            time.sleep(0.001) # evitar 100% de uso de CPU
            continue

        # 0 = nao muda | 1 = vai pro proximo | -1 = vai pro anterior
        delta = inputBH.buttons[0] - inputBH.buttons[1]
        if delta:
            idx = (idx + delta) % len(elements)
            input_locked = True
            continue

        # botao de 'enter'
        if inputBH.buttons[2]:
            input_locked = True
            if not level: # escolheu a dificuldade agora
                level = elements[idx]
                elements = filesBH.getPlaylist(level)
                idx = 0
                continue
            else: # escolheu a musica agora
                # dificuldade 0 nao conta erros
                stateBH.countingErrors = level != configBH.LEVELS[0]
                return filesBH.getMusicPath(elements[idx], level)
        
        # botao de "voltar"
        if inputBH.buttons[3] and level:
            level = None
            elements = configBH.LEVELS
            idx = 0

        # botao de trocar o input mode
        if inputBH.buttons[4]:
            # limpa estado atual dos botoes ja que trocou de input
            inputBH.buttons[:] = [0] * configBH.NUM_LANES
            stateBH.pianoMode = not stateBH.pianoMode 
            if stateBH.pianoMode:
                lcdBH.write("Modo de Entrada:\nPiano")
            else:
                lcdBH.write("Modo de Entrada:\nGuitarra")
            time.sleep(1)

        lcdBH.write('\n'.join(elements[idx].split(" - ", 1)))

def render(now_ms, display_txt):
    ledsBH.blank()
    notesBH.updateNotes(now_ms)
    notesBH.updateInput(now_ms)
    ledsBH.show()
    lcdBH.write(display_txt)

def start_music(music_path):
    # carrega duracao da musica e suas notas
    start_ms, end_ms = filesBH.getTimestamps(music_path)
    duration_ms = end_ms - start_ms
    formated_duration_time = audioBH.to_mmss(duration_ms)
    
    event_index = 0
    events = notesBH.loadNotes(music_path)
    while (event_index < len(events) and events[event_index].time_ms <= start_ms):
        event_index+=1

    audioBH.start(music_path, start_ms, end_ms) # comeca a tocar a musica com os timestamps
    configBH.timeCorrection() # delay para sincronizacao de hit line com a musica
    base_ms = time.monotonic_ns() // 1_000_000 # relogio base em ms
    while True:
        played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
        now_ms = played_ms + start_ms

        while (event_index < len(events) and events[event_index].time_ms <= now_ms):
            if events[event_index].time_ms <= end_ms:
                e = events[event_index]
                notesBH.spawnNote(e.mask, e.time_ms, e.length_leds)
            event_index += 1
        
        # adiciona tempo decorrido na exibicao do display
        formated_time = f"\nTempo: {audioBH.to_mmss(min(played_ms, duration_ms))}/{formated_duration_time}"
        display_txt = scoreBH.lastJudgement + formated_time
        render(now_ms, display_txt)

        if stateBH.runLost: # zerou a vida
            audioBH.stop()
            return 0

        if stateBH.endGame: # jogo morto no meio pelo botao especial
            audioBH.stop()
            return -1

        #acabou a musica
        if played_ms >= duration_ms:
            # espera nao ter mais notas ativas
            while notesBH.hasActive():
                now_ms = start_ms + (time.monotonic_ns() // 1_000_000) - base_ms
                display_txt = scoreBH.lastJudgement + formated_time
                render(now_ms, display_txt)

            # adiciona um pequeno delay pra n ficar estranho qnd acaba as notas
            delay_start_ms = now_ms
            while now_ms - delay_start_ms <= configBH.NOTE_TRAVEL_TIME_MS:
                now_ms = start_ms + (time.monotonic_ns() // 1_000_000) - base_ms
                display_txt = scoreBH.lastJudgement + formated_time
                render(now_ms, display_txt)

            return scoreBH.totalScore


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

        if final_score == -1:
            lcdBH.write("Jogo Cancelado")
            ledsBH.clear()
            time.sleep(1)
            continue

        lcdBH.write(f"Pontuacao Final:\n{final_score}")

        if final_score:
            ledsBH.blinkLanes()
            ledsBH.slideLanes()
            ledsBH.blinkLanes()
        else:
            ledsBH.blinkRed()


if __name__ == "__main__":
    main()
