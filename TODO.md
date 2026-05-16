# Robotic Arm Project TODO

Use this checklist as your build roadmap. Do not try to finish everything at once. The goal is to make one small part work, understand it, then add the next part.

## 0. Understand The Project

- [ ] Understand the main idea: the Raspberry Pi is the brain, the Arduino is the motor controller.
- [ ] Understand that the Raspberry Pi sends text commands over USB serial.
- [ ] Understand that the Arduino reads those commands and moves servos.
- [ ] Understand that the PCA9685 board creates clean servo control signals.
- [ ] Understand that servos need their own power supply.
- [ ] Understand that all grounds must be connected together.
- [ ] Understand that software angle limits protect the arm from breaking itself.
- [ ] Understand that calibration means finding the safe angle range for each joint.

## 1. Learn What Each File Does

- [ ] Read `README.md` from top to bottom.
- [ ] Open `arduino/robotic_arm_firmware/robotic_arm_firmware.ino`.
- [ ] Find `SERVO_CHANNELS` and understand that each number maps to a PCA9685 channel.
- [ ] Find `ANGLE_MIN` and `ANGLE_MAX` and understand that these are Arduino-side safety limits.
- [ ] Find `currentAngles` and understand that these are the startup/home angles.
- [ ] Find `parseMoveCommand()` and understand that it reads commands like `MOVE 90 120 80 45 30`.
- [ ] Find `moveSmoothly()` and understand that it moves one degree at a time.
- [ ] Open `raspberry-pi/config.py`.
- [ ] Understand that `SERIAL_PORT` is the USB device path for the Arduino.
- [ ] Understand that `ANGLE_LIMITS` repeats safety limits on the Raspberry Pi side.
- [ ] Open `raspberry-pi/arm_controller.py`.
- [ ] Understand that `ArmPosition` stores one complete arm pose.
- [ ] Understand that `RoboticArmController.move_to()` sends one movement command to the Arduino.
- [ ] Open `raspberry-pi/run_demo.py`.
- [ ] Understand that the demo sends a short list of poses to the arm.

## 2. Buy Or Prepare Hardware

- [ ] Choose a 5-servo robotic arm frame with 2 base servos, 1 elbow servo, 1 wrist servo, and 1 gripper servo.
- [ ] Get a Raspberry Pi 2.
- [ ] Get an Arduino Uno, Nano, or Mega.
- [ ] Get a PCA9685 servo driver board.
- [ ] Get 5 metal gear servos.
- [ ] Get a 5V or 6V servo power supply with enough current.
- [ ] Get jumper wires.
- [ ] Get an emergency stop button.
- [ ] Get a fuse or inline fuse holder for the servo power line.
- [ ] Optional: get limit switches.
- [ ] Optional: get a camera or joystick.

## 3. Prepare The Raspberry Pi

- [ ] Install Raspberry Pi OS.
- [ ] Connect the Raspberry Pi to your network.
- [ ] Enable SSH if you want remote access.
- [ ] Update the Pi:

```bash
sudo apt update
sudo apt upgrade
```

- [ ] Install Python tooling:

```bash
sudo apt install python3-pip
```

- [ ] Install project dependencies:

```bash
cd raspberry-pi
pip3 install -r requirements.txt
```

## 4. Prepare The Arduino

- [ ] Install the Arduino IDE.
- [ ] Install the `Adafruit PWM Servo Driver Library`.
- [ ] Open `arduino/robotic_arm_firmware/robotic_arm_firmware.ino`.
- [ ] Select the correct Arduino board.
- [ ] Select the correct serial port.
- [ ] Compile the sketch.
- [ ] Upload the sketch to the Arduino.
- [ ] Open the Arduino serial monitor at `9600` baud.
- [ ] Confirm that the Arduino prints `READY robotic arm firmware`.

## 5. Wire The Electronics

- [ ] Keep servo power disconnected while wiring.
- [ ] Connect Raspberry Pi to Arduino by USB.
- [ ] Connect Arduino `5V` to PCA9685 `VCC`.
- [ ] Connect Arduino `GND` to PCA9685 `GND`.
- [ ] Connect Arduino `A4` to PCA9685 `SDA`.
- [ ] Connect Arduino `A5` to PCA9685 `SCL`.
- [ ] Connect external servo power positive to PCA9685 `V+`.
- [ ] Connect external servo power ground to PCA9685 `GND`.
- [ ] Confirm Arduino ground and servo power ground are connected together.
- [ ] Add a fuse on the servo power positive line if available.
- [ ] Connect only one servo to PCA9685 channel `0` for the first test.

## 6. First Software Test

- [ ] Plug the Arduino into the Raspberry Pi.
- [ ] Find the Arduino serial port:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
```

- [ ] Update `raspberry-pi/config.py` if the port is not `/dev/ttyACM0`.
- [ ] Run the demo:

```bash
cd raspberry-pi
python3 run_demo.py
```

- [ ] Confirm the Arduino responds with `OK`.
- [ ] Confirm the first servo moves slowly.
- [ ] Stop immediately if the servo buzzes hard, stalls, or gets hot.

## 7. Calibrate One Servo At A Time

- [ ] Test the base rotation servo on channel `0`.
- [ ] Find the minimum safe base rotation angle.
- [ ] Find the maximum safe base rotation angle.
- [ ] Write those numbers down.
- [ ] Test the base lift servo on channel `1`.
- [ ] Find the safe base lift range.
- [ ] Test the elbow servo on channel `2`.
- [ ] Find the safe elbow range.
- [ ] Test the wrist servo on channel `3`.
- [ ] Find the safe wrist range.
- [ ] Test the gripper servo on channel `4`.
- [ ] Find the safe gripper range.
- [ ] Update `ANGLE_MIN` and `ANGLE_MAX` in the Arduino firmware.
- [ ] Update `ANGLE_LIMITS` in `raspberry-pi/config.py`.
- [ ] Upload the Arduino firmware again after changing limits.

## 8. Assemble The Arm

- [ ] Move all servos to their home position before attaching horns.
- [ ] Attach the base rotation servo.
- [ ] Attach the base lift servo.
- [ ] Attach the elbow servo.
- [ ] Attach the wrist servo.
- [ ] Attach the gripper servo.
- [ ] Keep screws slightly loose until movement direction is confirmed.
- [ ] Run a tiny movement test.
- [ ] Tighten hardware only after calibration looks correct.

## 9. Improve The Code

- [ ] Add a command to move only one joint at a time.
- [ ] Add a `HOME` command to the Arduino firmware.
- [ ] Add a `STOP` command to the Arduino firmware.
- [ ] Add emergency stop input pin support.
- [ ] Add better serial error messages.
- [ ] Add logging on the Raspberry Pi.
- [ ] Add a command line tool for manual joint movement.
- [ ] Add unit tests for Raspberry Pi angle validation.

## 10. Add Manual Control

- [ ] Build a keyboard control script.
- [ ] Add small step controls, such as `+5` or `-5` degrees.
- [ ] Add a web UI with sliders.
- [x] Add joystick or gamepad support.
- [ ] Add saved poses.
- [ ] Add a button to return to home position.
- [ ] Add a button to open and close the gripper.

## 11. Add Robot Intelligence Later

- [ ] Add inverse kinematics after manual control is reliable.
- [ ] Add coordinate-based movement.
- [ ] Add camera input.
- [ ] Add object detection.
- [ ] Add pick-and-place routines.
- [ ] Add motion profiles with acceleration and deceleration.
- [ ] Add current sensing to detect stalls.
- [ ] Add limit switches for physical safety.

## 12. Safety Checklist Before Every Test

- [ ] Servo power is separate from Raspberry Pi power.
- [ ] Grounds are connected together.
- [ ] Servo power supply current is high enough.
- [ ] No fingers are inside the arm movement area.
- [ ] The arm is not holding anything heavy.
- [ ] Angles are inside calibrated limits.
- [ ] Emergency stop is reachable.
- [ ] First movement is small and slow.
- [ ] Servos are not overheating.
- [ ] The arm can return to home position safely.
