SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
SERIAL_TIMEOUT_SECONDS = 2

JOINT_ORDER = ("base_rotation", "base_lift", "elbow", "wrist", "gripper")

ANGLE_LIMITS = {
    "base_rotation": (0, 180),
    "base_lift": (30, 150),
    "elbow": (20, 160),
    "wrist": (0, 180),
    "gripper": (20, 90),
}

HOME_POSITION = {
    "base_rotation": 90,
    "base_lift": 90,
    "elbow": 90,
    "wrist": 90,
    "gripper": 45,
}
