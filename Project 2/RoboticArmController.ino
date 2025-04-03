#include <Servo.h>

// Create servo objects for each motor
Servo servo3, servo4, servo5, servo6;

// Store current positions of servos
int position3 = 90, position4 = 90, position5 = 90, position6 = 90; // Assume initial position is 90°

struct ServoCommand {
  int pin;
  int targetPosition;
  bool active;
};

ServoCommand currentCommand = {0, 0, false};
unsigned long lastMoveTime = 0;
const int moveInterval = 15; // Milliseconds per movement step

// Function to get the correct servo object
Servo* getServo(int pin) {
  if (pin == 3) return &servo3;
  if (pin == 4) return &servo4;
  if (pin == 5) return &servo5;
  if (pin == 6) return &servo6;
  return nullptr;
}

// Function to get the reference position of a servo
int* getServoPosition(int pin) {
  if (pin == 3) return &position3;
  if (pin == 4) return &position4;
  if (pin == 5) return &position5;
  if (pin == 6) return &position6;
  return nullptr;
}

// Function to move a servo to zero smoothly
void moveToZero(int pin) {
  int* currentPosition = getServoPosition(pin);
  if (currentPosition) {
    currentCommand = {pin, 0, true}; // Set a command to move to 0°
  }
}

// Function to queue a servo movement
void moveServo(int pin, int angle) {
  int* currentPosition = getServoPosition(pin);
  if (currentPosition) {
    int newPosition = constrain(*currentPosition + angle, 0, 180);
    currentCommand = {pin, newPosition, true}; // Queue the command
  }
}

void MoveDown(){
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(5, -30);
  while (currentCommand.active) processMovement();
  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 35);
  while (currentCommand.active) processMovement();
  moveServo(3, -50);
  while (currentCommand.active) processMovement();
}

void MoveDown3(){
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 50);
  while (currentCommand.active) processMovement();
  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(5, -30);
  while (currentCommand.active) processMovement();
  moveServo(6, 30);
  while (currentCommand.active) processMovement();
  moveServo(5, -50);
  while (currentCommand.active) processMovement();
  moveServo(6, 60);
  while (currentCommand.active) processMovement();
  moveServo(3, -50);
  while (currentCommand.active) processMovement();
}

void MoveUp(){
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
  moveServo(3, 50);
  while (currentCommand.active) processMovement();
}

void MoveUp3(){
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

void moveBox1() {
  moveServo(4, -2);
  while (currentCommand.active) processMovement();
  MoveDown();
  delay(1000);
  MoveUp();
}

void moveBox2() {
  moveServo(4, 20);
  while (currentCommand.active) processMovement();
  MoveDown();
  delay(1000);
  MoveUp();
}

void moveBox3() {
  moveServo(4, 40);
  while (currentCommand.active) processMovement();
  MoveDown3();
  delay(1000);
  MoveUp();
}

void processMovement() {
  if (!currentCommand.active) return; // No movement needed

  Servo* selectedServo = getServo(currentCommand.pin);
  int* currentPosition = getServoPosition(currentCommand.pin);
  
  if (!selectedServo || !currentPosition) return;

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
      currentCommand.active = false; // Stop movement when target is reached
    }
  }
}

void setup() {
  Serial.begin(9600);

  servo3.attach(3);
  servo4.attach(4);
  servo5.attach(5);
  servo6.attach(6);

  // Move all servos to 0° at startup smoothly
  moveToZero(3);
  moveToZero(4);
  moveToZero(5);
  moveToZero(6);

  Serial.println("Servos initialized. Use move(pin, angle) to move.");
}

void loop() {
  processMovement(); // Continuously check if a servo needs movement

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print("Received: ");
    Serial.println(command);

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
      }
    } else if (command.equals("moveBox1")) {
      Serial.println("Executing moveBox1()");
      moveBox1();
    } else if (command.equals("moveBox2")) {
      Serial.println("Executing moveBox2()");
      moveBox2();
    }else if (command.equals("moveBox3")) {
      Serial.println("Executing moveBox3()");
      moveBox3();
    } else {
      Serial.println("Invalid command! Use format: move(pin, angle), gatherCenter, gatherLeft, gatherRight, or moveBox1");
    }
  }
}

// 3 - Pinça (abre: positivo, fecha: negativo) [limit ±50°]
// 4 - Rotação (positivo: anti-horário, negativo: horário) [limit ±90°]
// 5 - Vertical (positivo: cima, negativo: baixo) [limit +100°] Começa no 0
// 6 - Frente/trás (negativo:trás , positivo: frente) [mimit +180º] Começa no 0
