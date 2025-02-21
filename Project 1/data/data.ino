void setup() {
    Serial.begin(9600); 

}

void loop() {

  int n = 5;  // Run for n seconds
  unsigned long startTime = millis();  // Record start time
  
  // Runs the code during the time interval stated in the GUI, making us have a defined time window to read data.
  while(millis() - startTime < n * 1000){
    // Only reading pin A0
    int value = analogRead(A0);

    // Change with actual communication implementation. Make sure to always return both the read value and the time it was read, since assuming it was read at 10ms intervals is wrong (which you can verify by simply running the code)
    Serial.println(String(value) + ", " + String(millis() - startTime));

    // Data is read every 10 milliseconds
    delay(10);
  }

  Serial.println("Done!");
  while (true);  // Stop execution (optional)
}
