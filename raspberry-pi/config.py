SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
SERIAL_TIMEOUT_SECONDS = 2

JOINT_ORDER = ("base_rotation", "base_lift", "elbow", "wrist", "gripper")

ANGLE_LIMITS = {
    "base_rotation": (30, 150),
    "base_lift": (30, 150),
    "elbow": (20, 160),+
    "wrist": (0, 180),
    "gripper": (0, 87),
}

HOME_POSITION = {
    "base_rotation": 90,
    "base_lift": 90,
    "elbow": 90,
    "wrist": 90,
    "gripper": 90,
}

# TODO: Replace these with your real arm measurements before using XYZ control.
# Units are millimeters. Measure from pivot center to pivot center.
ARM_GEOMETRY = {
    "shoulder_height": 139,
    "upper_arm_length": 120,
    "forearm_length": 120.0,
    "wrist_to_gripper_tip": 107.0
}

# Choose which side the elbow bends toward in the side-view IK solve.
# Change this to -1 if the shoulder/elbow try to fold the wrong way.
IK_ELBOW_DIRECTION = -1

# TODO: Tune these after you test one joint at a time.
# These convert math angles into your physical servo angles.
IK_SERVO_OFFSETS = {
    "base_rotation": 90,
    "base_lift": 120,
    "elbow": 45,
    "wrist": 90,
}

# Change one of these to -1 if an IK-controlled joint moves opposite to what
# the XYZ target needs. Keep gripper tuning separate; LB/RB still control it.
IK_SERVO_DIRECTIONS = {
    "base_rotation": 1,
    "base_lift": -1,
    "elbow": 1,
    "wrist": 1,
}

# Wrist/gripper pitch target for carrying a cup. 0 means level with the ground.
# Tune IK_SERVO_OFFSETS["wrist"] and IK_SERVO_DIRECTIONS["wrist"] if the cup
# tilts while shoulder/elbow move.
GRIPPER_LEVEL_ANGLE_DEGREES = 0.0

# TODO: Set this to a reachable, safe starting point for your gripper tip.
CARTESIAN_HOME = {
    "x": 300.0,
    "y": 0.0,
    "z": 139.0,
}

# Joystick axis indexes vary by controller. Watch the startup "Axis snapshot"
# output in run_joystick.py, then change these if your controller reports
# right stick Y on a different axis.
JOYSTICK_AXES = {
    "x": 1,
    "y": 0,
    "z": 3,
}

# Change one of these to -1 if that XYZ direction feels backwards.
JOYSTICK_AXIS_DIRECTIONS = {
    "x": -1,
    "y": 1,
    "z": -1,
}

CARTESIAN_STEP_MM = 3.0
