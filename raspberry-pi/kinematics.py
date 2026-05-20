from __future__ import annotations

import math
from dataclasses import dataclass

from arm_controller import ArmPosition
from config import (
    ANGLE_LIMITS,
    ARM_GEOMETRY,
    IK_ELBOW_DIRECTION,
    GRIPPER_LEVEL_ANGLE_DEGREES,
    IK_SERVO_DIRECTIONS,
    IK_SERVO_OFFSETS,
)


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
    wrist_to_gripper_tip = ARM_GEOMETRY.get("wrist_to_gripper_tip", 0.0)

    horizontal_distance = math.hypot(target.x, target.y)
    base_rotation = IK_SERVO_OFFSETS["base_rotation"] + (
        IK_SERVO_DIRECTIONS["base_rotation"] * math.degrees(math.atan2(target.y, target.x))
    )

    gripper_pitch = math.radians(GRIPPER_LEVEL_ANGLE_DEGREES)
    wrist_horizontal = horizontal_distance - wrist_to_gripper_tip * math.cos(gripper_pitch)
    wrist_vertical = (
        target.z
        - shoulder_height
        - wrist_to_gripper_tip * math.sin(gripper_pitch)
    )

    wrist_reach = math.hypot(wrist_horizontal, wrist_vertical)
    min_reach = abs(upper_arm - forearm) + 1.0
    max_reach = upper_arm + forearm - 1.0
    safe_reach = clamp(wrist_reach, min_reach, max_reach)

    if wrist_reach > 0 and safe_reach != wrist_reach:
        scale = safe_reach / wrist_reach
        wrist_horizontal *= scale
        wrist_vertical *= scale

    elbow_cosine = clamp(
        (wrist_horizontal**2 + wrist_vertical**2 - upper_arm**2 - forearm**2)
        / (2 * upper_arm * forearm),
        -1.0,
        1.0,
    )
    elbow_sine = IK_ELBOW_DIRECTION * math.sqrt(max(0.0, 1.0 - elbow_cosine**2))
    elbow_relative_angle = math.atan2(elbow_sine, elbow_cosine)

    shoulder_angle = math.atan2(wrist_vertical, wrist_horizontal) - math.atan2(
        forearm * elbow_sine,
        upper_arm + forearm * elbow_cosine,
    )
    elbow_bend_angle = abs(elbow_relative_angle)
    forearm_angle = shoulder_angle + elbow_relative_angle

    base_lift = IK_SERVO_OFFSETS["base_lift"] + (
        IK_SERVO_DIRECTIONS["base_lift"] * math.degrees(shoulder_angle)
    )
    elbow = IK_SERVO_OFFSETS["elbow"] + (
        IK_SERVO_DIRECTIONS["elbow"] * math.degrees(elbow_bend_angle)
    )
    auto_level_wrist = IK_SERVO_OFFSETS["wrist"] + (
        IK_SERVO_DIRECTIONS["wrist"]
        * (GRIPPER_LEVEL_ANGLE_DEGREES - math.degrees(forearm_angle))
    )
    wrist_angle = wrist if wrist is not None else round(auto_level_wrist)

    return ArmPosition(
        base_rotation=clamp_joint("base_rotation", round(base_rotation)),
        base_lift=clamp_joint("base_lift", round(base_lift)),
        elbow=clamp_joint("elbow", round(elbow)),
        wrist=clamp_joint("wrist", wrist_angle),
        gripper=clamp_joint("gripper", gripper),
    )
