bool dataAcquisitionActive = false;
int acquisitionInterval = 50;  // Default interval in milliseconds

void setup() {
  Serial.begin(38400);  // Initialize serial communication at 38400 baud
  pinMode(LED_BUILTIN, OUTPUT);  // Set built-in LED as output
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming command
    command.trim();  // Remove any whitespace

    // Start acquisition
    if (command == "GET") {
      dataAcquisitionActive = true;  
    }
    else if (command.startsWith("SET_INTERVAL")) {
      // Remove the string, keeping only the interval integer
      command.replace("SET_INTERVAL", "");  
      command.trim();

      // Checks if the command still exists after trimming the string
      if (command.length() > 0) {
        // Converts into integer, and checks if set interval wasn't 0
        int newInterval = command.toInt();  
        if (newInterval > 0) {
          acquisitionInterval = newInterval;  
        }
      }
    }
    // Stop acquisition
    else if (command == "STOP") {  
      dataAcquisitionActive = false;  
    } 
    // Invalid command
    else {
      Serial.println("ERROR");  
    }
  }

  if (dataAcquisitionActive) {
    // Read the analog value from pin A0 and send it along with the current timestamp
    int value = analogRead(A0);  
    Serial.println(String(value) + ", " + String(millis()));
    // Wait before next reading
    delay(acquisitionInterval);
  }
}