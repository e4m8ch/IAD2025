// Variable declaration
bool dataAcquisitionActive = false;
int acquisitionInterval = 50;
unsigned long resetTime = 0;  

void setup() {
  // Initialize serial communication at 38400 baud
  Serial.begin(38400);
}

void loop() {
  if (Serial.available() > 0) {

    // Read the incoming command and remove whitespace
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Stop acquisition if the incoming command is STOP
    if (command == "STOP") {  
      dataAcquisitionActive = false;  
    } 

    // Start acquisition if the incoming command is GET
    else if (command == "GET") {
      dataAcquisitionActive = true;  
    }

    // Set the interval to what was sent by the user if the incoming command is SET_INTERVAL
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

    // Restarts the timer is the incoming command is CLEAR
    else if (command == "CLEAR") {
      dataAcquisitionActive = false;  
      resetTime = millis();
    }
    // Invalid command
    else {
      Serial.println("ERROR");  
    }
  }

  if (dataAcquisitionActive) {
    // Read the analog value from pin A0 and send it along with the current timestamp
    int value = analogRead(A0);  
    Serial.println(String(value) + ", " + String(millis() - resetTime));
    // Wait before next reading
    delay(acquisitionInterval);
  }
}