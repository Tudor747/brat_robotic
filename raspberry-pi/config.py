SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
SERIAL_TIMEOUT_SECONDS = 2

JOINT_ORDER = ("base_rotation", "base_lift", "elbow", "wrist", "gripper")

ANGLE_LIMITS = {
    "base_rotation": (0, 180),
    "base_lift": (30, 150),
    "elbow": (20, 160),
    "wrist": (0, 180),
    "gripper": (20, 87),
}

HOME_POSITION = {
    "base_rotation": 90,
    "base_lift": 90,
    "elbow": 90,
    "wrist": 90,
    "gripper": 87,
}

# TODO: Replace these with your real arm measurements before using XYZ control.
# Units are millimeters. Measure from pivot center to pivot center.
ARM_GEOMETRY = {
    "shoulder_height": 60.0,
    "upper_arm_length": 100.0,
    "forearm_length": 100.0,
}

# TODO: Tune these after you test one joint at a time.
# These convert math angles into your physical servo angles.
IK_SERVO_OFFSETS = {
    "base_rotation": 90,
    "base_lift": 90,
    "elbow": 90,
}

# TODO: Set this to a reachable, safe starting point for your gripper tip.
CARTESIAN_HOME = {
    "x": 120.0,
    "y": 0.0,
    "z": 80.0,
}
