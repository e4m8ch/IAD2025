bool dataAcquisitionActive = false;

void setup() {
  Serial.begin(38400);  // Initialize serial communication at 38400 baud
  pinMode(LED_BUILTIN, OUTPUT);  // Set built-in LED as output
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming command
    command.trim();  // Remove any whitespace

    if (command == "GET") {  // Process only if the command is "GET"
      // int value = analogRead(A0);  // Read the analog value from pin A0
      int value = random(0, 1024);  // Generate a random value between 0 and 1023
      Serial.println(String(value) + ", " + String(millis()));  // Send value and timestamp
    } else {
      Serial.println("ERROR");  // Send an error message if the command is invalid
    }
  }
}
