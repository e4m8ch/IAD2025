bool dataAcquisitionActive = false;
int n = 5;  // Run for n seconds

void setup() {
  // Begins serial communication at a baud rate of 38400
  Serial.begin(38400);
  pinMode(LED_BUILTIN, OUTPUT); 
}

void loop() {
  // Check if there is incoming data, by checking if there's any over 0 bit word in the serial port
  if (Serial.available() > 0) {
    // Read the incoming byte until a newline is encountered, and remove surrounding whitespace
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    
    // If the received command is "TOGGLE", toggle the data acquisition state
    if (command == "TOGGLE" && !dataAcquisitionActive) { 
      dataAcquisitionActive = true;
      Serial.println("Data acquisition started.");
      
      // Record start time and turn on an LED
      unsigned long startTime = millis();
      digitalWrite(LED_BUILTIN, HIGH);

      // Runs the code during the time interval stated in the GUI, making us have a defined time window to read data.
      while(millis() - startTime < n * 1000){
        // Only reading pin A0
        int value = analogRead(A0);
        Serial.println(String(value) + ", " + String(millis() - startTime));

        // Data is read every 10 milliseconds
        delay(10);
      }

      // Ends data acquisition
      Serial.println("DONE");
      dataAcquisitionActive = false; // Reset flag
      digitalWrite(LED_BUILTIN, LOW); // Turn off LED after acquisition
    }
  }
}
