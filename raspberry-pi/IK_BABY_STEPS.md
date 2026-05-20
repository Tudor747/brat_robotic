# Inverse Kinematics Baby Steps

Do not start with the joystick. Start with one tiny target, look at the angles,
then move the robot only when the numbers look safe.

## Step 1: Measure The Arm

Open `config.py` and check these numbers:

```python
ARM_GEOMETRY = {
    "shoulder_height": 139,
    "upper_arm_length": 120,
    "forearm_length": 120.0,
    "wrist_to_gripper_tip": 107.0,
}
```

Measure in millimeters:

- `shoulder_height`: table/base to shoulder pivot center
- `upper_arm_length`: shoulder pivot center to elbow pivot center
- `forearm_length`: elbow pivot center to wrist pivot center
- `wrist_to_gripper_tip`: wrist pivot center to the point you want to control

If these are wrong, IK will also be wrong.

## Step 2: Use The Preview

Open this file in your browser:

```text
raspberry-pi/arm_preview.html
```

Move the target slowly. If the preview says a servo is at `LIMIT`, that target is
too hard for the real robot right now.

## Step 3: Print IK Angles Without Moving

On the Raspberry Pi:

```bash
cd raspberry-pi
python3 ik_calibrate.py
```

Type:

```text
250 0 160
```

Read the printed servo angles. Nothing moves yet.

You can do this step without the Arduino connected. The script connects to the
robot only after you type `move`.

## Step 4: Move Only After Reading

If the angles look safe, type:

```text
move
```

The robot moves to the last printed target.

## Step 5: Fix One Problem At A Time

If the base turns the wrong way:

```python
IK_SERVO_DIRECTIONS["base_rotation"] *= -1
```

If the shoulder moves the wrong way:

```python
IK_SERVO_DIRECTIONS["base_lift"] *= -1
```

If the elbow folds the wrong way:

```python
IK_ELBOW_DIRECTION = 1
```

If the gripper is not level:

```python
IK_SERVO_OFFSETS["wrist"] = 90
```

Change one thing, test again, then change the next thing. Slow is fast here.

## Step 6: Only Then Use The Joystick

When `ik_calibrate.py` works for simple targets, run:

```bash
python3 run_joystick.py
```

Keep movements small. The joystick uses the same IK solver.
