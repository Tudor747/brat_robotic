#include <Servo.h>

const uint8_t JOINT_COUNT = 5;

const char* JOINT_NAMES[JOINT_COUNT] = {
  "base",
  "shoulder",
  "elbow",
  "wrist",
  "gripper"
};

const uint8_t SERVO_PINS[JOINT_COUNT] = {2,3,4,5,6};
const int ANGLE_MIN[JOINT_COUNT] = {0, 30, 20, 34, 0};
const int ANGLE_MAX[JOINT_COUNT] = {120, 150, 160, 154, 90};

Servo servos[JOINT_COUNT];
int currentAngles[JOINT_COUNT] = {90, 90, 90, 94, 90};
String inputLine = "";

void writeServo(uint8_t jointIndex, int angle) {
  int safeAngle = constrain(angle, ANGLE_MIN[jointIndex], ANGLE_MAX[jointIndex]);
  servos[jointIndex].write(safeAngle);
  currentAngles[jointIndex] = safeAngle;
}

void moveSmoothly(const int targetAngles[JOINT_COUNT]) {
  bool moving = true;

  while (moving) {
    moving = false;

    for (uint8_t i = 0; i < JOINT_COUNT; i++) {
      int target = constrain(targetAngles[i], ANGLE_MIN[i], ANGLE_MAX[i]);

      if (currentAngles[i] < target) {
        writeServo(i, currentAngles[i] + 1);
        moving = true;
      } else if (currentAngles[i] > target) {
        writeServo(i, currentAngles[i] - 1);
        moving = true;
      }
    }

    delay(15);
  }
}

bool parseMoveCommand(String line, int targetAngles[JOINT_COUNT]) {
  line.trim();

  if (!line.startsWith("MOVE ")) {
    return false;
  }

  line.remove(0, 5);
  line.trim();

  int parsedCount = 0;

  while (line.length() > 0 && parsedCount < JOINT_COUNT) {
    int separatorIndex = line.indexOf(' ');
    String token;

    if (separatorIndex == -1) {
      token = line;
      line = "";
    } else {
      token = line.substring(0, separatorIndex);
      line = line.substring(separatorIndex + 1);
      line.trim();
    }

    if (token.length() == 0) {
      continue;
    }

    targetAngles[parsedCount] = token.toInt();
    parsedCount++;
  }

  return parsedCount == JOINT_COUNT;
}

void handleCommand(String line) {
  int targetAngles[JOINT_COUNT];

  if (!parseMoveCommand(line, targetAngles)) {
    Serial.println("ERR expected: MOVE base shoulder elbow wrist gripper");
    return;
  }

  moveSmoothly(targetAngles);
  Serial.println("OK");
}

void setup() {
  Serial.begin(9600);
  inputLine.reserve(64);

  for (uint8_t i = 0; i < JOINT_COUNT; i++) {
    servos[i].attach(SERVO_PINS[i]);
  }

  for (uint8_t i = 0; i < JOINT_COUNT; i++) {
    writeServo(i, currentAngles[i]);
  }

  Serial.println("READY robotic arm firmware");
}

void loop() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();

    if (incoming == '\n') {
      handleCommand(inputLine);
      inputLine = "";
    } else if (incoming != '\r') {
      inputLine += incoming;
    }
  }
}
