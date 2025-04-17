#include <Servo.h>
#include <avr/wdt.h>


// Create servo objects for each motor
Servo servo3, servo4, servo5, servo6;

// Store current positions of servos
int position3 = 90, position4 = 90, position5 = 90, position6 = 90; 

// Define a structure to hold servo command information
struct ServoCommand {
  int pin;
  int targetPosition;
  bool active;
};

// Initialize the current command structure with default values
ServoCommand currentCommand = {0, 0, false};  
unsigned long lastMoveTime = 0;                
const int moveInterval = 15;                   

// Function to return the corresponding servo object based on the pin number
Servo* getServo(int pin) {
  switch (pin) {
    case 3: return &servo3;
    case 4: return &servo4;
    case 5: return &servo5;
    case 6: return &servo6;
    default: return nullptr;  
  }
}

// Function to return the current position of a servo based on the pin number
int* getServoPosition(int pin) {
  switch (pin) {
    case 3: return &position3;
    case 4: return &position4;
    case 5: return &position5;
    case 6: return &position6;
    default: return nullptr;  
  }
}

// Function to move a servo to position 0 (reset to 0 degrees)
void moveToZero(int pin) {
  int* currentPosition = getServoPosition(pin);
  if (currentPosition) {
    currentCommand = {pin, 0, true};  
  } else {
    Serial.print("Error: Invalid pin in moveToZero: ");
    Serial.println(pin);
  }
}

// Function to move a servo by a specified angle (positive or negative)
void moveServo(int pin, int angle) {
  int* currentPosition = getServoPosition(pin);
  if (currentPosition) {
    int newPosition = constrain(*currentPosition + angle, 0, 180);  
    currentCommand = {pin, newPosition, true};  
  } else {
    Serial.print("Error: Invalid pin in moveServo: ");
    Serial.println(pin);
  }
}

// Function to gradually move the servo to its target position
void processMovement() {
  if (!currentCommand.active) return;  

  Servo* selectedServo = getServo(currentCommand.pin);  
  int* currentPosition = getServoPosition(currentCommand.pin);  

  if (!selectedServo || !currentPosition) {
    Serial.println("Error: Invalid servo or position pointer in processMovement.");
    currentCommand.active = false;
    return;
  }

  unsigned long now = millis();  
  if (now - lastMoveTime >= moveInterval) {
    lastMoveTime = now;  

    if (*currentPosition < currentCommand.targetPosition) {
      (*currentPosition)++;
    } else if (*currentPosition > currentCommand.targetPosition) {
      (*currentPosition)--;
    }

    selectedServo->write(*currentPosition);

    if (*currentPosition == currentCommand.targetPosition) {
      currentCommand.active = false;
    }
  }
}

// Function to reset all servos to position 0
void resetPosition() {
  moveToZero(3);
  delay(200);
  moveToZero(4);
  delay(200);
  moveToZero(5);
  delay(200);
  moveToZero(6);
  delay(200);
};

void softwareReset() {
  wdt_enable(WDTO_15MS); // Set watchdog timer to reset in 15 ms
  while (1) {}           // Wait for reset
}


// -------------------------------------------------- BOX 1 -------------------------------------------------

// Function to move Box 1 down
void MoveDown1() {
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 60);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 50);
  while (currentCommand.active) processMovement();
  moveServo(5, -80);
  while (currentCommand.active) processMovement();
  moveServo(6, 60);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 50);
  while (currentCommand.active) processMovement();
  moveServo(5, -80);
  while (currentCommand.active) processMovement();
  moveServo(3, -50);
  while (currentCommand.active) processMovement();
}

// Function to move Box 1 up
void MoveUp() {
  moveServo(6, -35);
  while (currentCommand.active) processMovement();
  moveServo(5, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, -30);
  while (currentCommand.active) processMovement();
  moveServo(5, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, -30);
  while (currentCommand.active) processMovement();
  moveServo(6, -50);
  while (currentCommand.active) processMovement();
  moveServo(4, 2);
  while (currentCommand.active) processMovement();
}

// Function to move Box 1 by executing specific moves
void moveBox1() {
  moveServo(4, -2);
  while (currentCommand.active) processMovement();
  MoveDown1();
  delay(1000);
  MoveUp();
  moveServo(4, 2);
  softwareReset();
}

// -------------------------------------------------- BOX 2 -------------------------------------------------

// Function to move Box 2 down
void MoveDown2() {
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 60);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 50);
  while (currentCommand.active) processMovement();
  moveServo(3, -50);
  while (currentCommand.active) processMovement();
}

// Function to move Box 2 by executing specific moves
void moveBox2() {
  moveServo(4, 23);
  while (currentCommand.active) processMovement();
  MoveDown2();
  delay(1000);
  MoveUp();
  moveServo(4, -23);
  softwareReset();
}

// -------------------------------------------------- BOX 3 -------------------------------------------------

// Function to move Box 3 down
void MoveDown3() {
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(6, 90);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(5, -60);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(5, -10);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(6, 40);
  while (currentCommand.active) processMovement();
  delay(200);

  moveServo(3, -50);
  while (currentCommand.active) processMovement();
  delay(200);
}

// Function to move Box 3 up
void MoveUp3() {
  moveServo(6, -60);
  while (currentCommand.active) processMovement();
  moveServo(5, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, -30);
  while (currentCommand.active) processMovement();
  moveServo(5, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, -30);
  while (currentCommand.active) processMovement();
  moveServo(6, -50);
  while (currentCommand.active) processMovement();
  moveServo(4, 2);
  while (currentCommand.active) processMovement();
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
}

// Function to move Box 3 by executing specific moves
void moveBox3() {
  moveServo(4, 41);
  while (currentCommand.active) processMovement();
  MoveDown3();
  delay(1000);
  MoveUp();
  moveServo(4, -41);
  softwareReset();
}

// Setup function to initialize the servos and communication
void setup() {
  Serial.begin(9600);

  // Attach servos to pins
  servo3.attach(3);
  servo4.attach(4);
  servo5.attach(5);
  servo6.attach(6);

  resetPosition();

  Serial.println("Servos initialized. Use move(pin, angle) to move.");
}

// Main loop function to process movement commands from Serial input
void loop() {
  processMovement();

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    Serial.print("Raw input: ");
    Serial.println(command);
    command.trim();
    Serial.print("Received: ");
    Serial.println(command);

    // Handle move(pin, angle)
    if (command.startsWith("move(") && command.endsWith(")")) {
      int firstComma = command.indexOf(',');
      if (firstComma != -1) {
        int pin = command.substring(5, firstComma).toInt();
        int angle = command.substring(firstComma + 1, command.length() - 1).toInt();

        if (pin >= 3 && pin <= 6) {
          moveServo(pin, angle);
          Serial.print("Moving servo on pin ");
          Serial.print(pin);
          Serial.print(" by ");
          Serial.print(angle);
          Serial.println(" degrees.");
        } else {
          Serial.println("Invalid pin! Use pin 3, 4, 5, or 6.");
        }
      } else {
        Serial.println("Malformed move command. Use move(pin, angle)");
      }

    // Handle named commands
    } else if (command.equals("moveBox1")) {
      Serial.println("Executing moveBox1()");
      moveBox1();
    } else if (command.equals("moveBox2")) {
      Serial.println("Executing moveBox2()");
      moveBox2();
    } else if (command.equals("moveBox3")) {
      Serial.println("Executing moveBox3()");
      moveBox3();

    // Handle numeric string or comma-separated list
    } else {
      int fromIndex = 0;
      while (fromIndex < command.length()) {
        int commaIndex = command.indexOf(',', fromIndex);
        String numStr;
        if (commaIndex == -1) {
          numStr = command.substring(fromIndex);
          fromIndex = command.length(); 
        } else {
          numStr = command.substring(fromIndex, commaIndex);
          fromIndex = commaIndex + 1;
        }

        numStr.trim();
        int num = numStr.toInt();

        switch (num) {
          case 0:
            Serial.println("Executing moveBox1()");
            moveBox3();
            break;
          case 1:
            Serial.println("Executing moveBox2()");
            moveBox2();
            break;
          case 2:
            Serial.println("Executing moveBox3()");
            moveBox1();
            break;
          default:
            Serial.print("Unknown box number: ");
            Serial.println(num);
            break;
        }
      }
    }
  }
}
