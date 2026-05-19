from __future__ import annotations

import math
from dataclasses import dataclass

from arm_controller import ArmPosition
from config import ANGLE_LIMITS, ARM_GEOMETRY, HOME_POSITION, IK_SERVO_OFFSETS


@dataclass(frozen=True)
class CartesianPosition:
    x: float
    y: float
    z: float


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def clamp_joint(joint: str, angle: int) -> int:
    minimum, maximum = ANGLE_LIMITS[joint]
    return max(minimum, min(maximum, angle))


def cartesian_to_arm_position(
    target: CartesianPosition,
    gripper: int,
    wrist: int | None = None,
) -> ArmPosition:
    shoulder_height = ARM_GEOMETRY["shoulder_height"]
    upper_arm = ARM_GEOMETRY["upper_arm_length"]
    forearm = ARM_GEOMETRY["forearm_length"]

    horizontal_distance = math.hypot(target.x, target.y)
    vertical_distance = target.z - shoulder_height
    reach = math.hypot(horizontal_distance, vertical_distance)

    # TODO: When you give your exact arm measurements, test this with the
    # gripper disconnected first. If a servo moves opposite to expected,
    # invert that servo in the conversion below instead of rewiring.
    min_reach = abs(upper_arm - forearm) + 1.0
    max_reach = upper_arm + forearm - 1.0
    safe_reach = clamp(reach, min_reach, max_reach)

    base_rotation = math.degrees(math.atan2(target.y, target.x))
    base_rotation += IK_SERVO_OFFSETS["base_rotation"]

    shoulder_to_target = math.atan2(vertical_distance, horizontal_distance)
    shoulder_cosine = (
        upper_arm**2 + safe_reach**2 - forearm**2
    ) / (2 * upper_arm * safe_reach)
    shoulder_angle = shoulder_to_target + math.acos(clamp(shoulder_cosine, -1.0, 1.0))

    elbow_cosine = (
        upper_arm**2 + forearm**2 - safe_reach**2
    ) / (2 * upper_arm * forearm)
    elbow_angle = math.pi - math.acos(clamp(elbow_cosine, -1.0, 1.0))

    base_lift = IK_SERVO_OFFSETS["base_lift"] - math.degrees(shoulder_angle)
    elbow = IK_SERVO_OFFSETS["elbow"] + math.degrees(elbow_angle)

    return ArmPosition(
        base_rotation=clamp_joint("base_rotation", round(base_rotation)),
        base_lift=clamp_joint("base_lift", round(base_lift)),
        elbow=clamp_joint("elbow", round(elbow)),
        wrist=clamp_joint("wrist", wrist if wrist is not None else HOME_POSITION["wrist"]),
        gripper=clamp_joint("gripper", gripper),
    )
