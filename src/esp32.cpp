#include "BluetoothSerial.h"

BluetoothSerial BT;

const int GuitarBtns[] = {27, 26, 25, 33, 32};
const int PianoBtns[] = {1, 2, 3, 4, 5};//placeholder pra caralho

int* btns = GuitarBtns;
bool isPiano = False;

bool last[] = {1, 1, 1, 1, 1}; // 1 == HIGH == Botao Solto

void setup() {
  for (int b : GuitarBtns)
    pinMode(b, INPUT_PULLUP);
  for (int b : PianoBtns)
    pinMode(b, INPUT_PULLUP);

  BT.begin("ESP32_Controle");
}

void loop(){
  
      if(BT.available()) {
        String msg = BT.readStringUntil('\n');
        msg.trim();    

        //Se recebeu
        if(msg == 'TOGGLE_KEYS') {
            //Troca dos pinos da guitarra pro teclado e vice-versa
            if(!isKeyboard) 
                btns = KeyboardBtns;
            else 
                btns = GuitarBtns;
        }
        //Reseta os lasts pra nao dar merda
        for(int i = 0; i < 5; i++) {
            last[i] = digitalRead(btns[i]);
        }
    }

  for (int i = 0; i < 5; i++) {
    bool cur = digitalRead(btns[i]);

    if (cur != last[i]) {
      BT.printf("BTN/%d:%d\n", i + 1, !cur);
      last[i] = cur;
    }
  }

  delay(10);
}
