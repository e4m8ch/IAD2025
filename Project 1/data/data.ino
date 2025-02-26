bool dataAcquisitionActive = false;

void setup() {
  Serial.begin(38400);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "GET") {  // Apenas processa se o comando for "GET"
      int value = analogRead(A0);
      Serial.println(String(value) + ", " + String(millis()));
    } else {
      Serial.println("ERROR");  // Envia erro para o Raspberry Pi se o comando for inválido
    }
  }
}

