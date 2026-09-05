// 1 = Bluetooth
// 0 = USB serial
#define USE_BLUETOOTH 0

#include <Arduino.h>

#if USE_BLUETOOTH
#include "BluetoothSerial.h"
BluetoothSerial BT;
#endif

const unsigned long SERIAL_BAUD = 115200;

const int btns[] = {27, 26, 25, 33, 32};
bool last[] = {HIGH, HIGH, HIGH, HIGH, HIGH};

void setup() {
    for (int b : btns)
        pinMode(b, INPUT_PULLUP);

#if USE_BLUETOOTH
    BT.begin("ESP32_Controle");
#else
    Serial.begin(SERIAL_BAUD);
#endif
}

void loop(){
    for (int i = 0; i < 5; i++) {
        bool cur = digitalRead(btns[i]);

        if (cur != last[i]) {
#if USE_BLUETOOTH
            BT.printf("BTN/%d:%d\n", i + 1, !cur);
#else
            Serial.printf("BTN/%d:%d\n", i + 1, !cur);
#endif
            last[i] = cur;
        }
    }

    delay(10);
}
