from __future__ import annotations

import time

import pygame

from arm_controller import ArmPosition, RoboticArmController
from config import (
    ANGLE_LIMITS,
    CARTESIAN_HOME,
    CARTESIAN_STEP_MM,
    HOME_POSITION,
    JOYSTICK_AXES,
    JOYSTICK_AXIS_DIRECTIONS,
)
from kinematics import CartesianPosition, cartesian_to_arm_position


DEADZONE = 0.25
LOOP_SECONDS = 0.05
GRIPPER_STEP = 3


def clamp_joint(joint: str, angle: int) -> int:
    minimum, maximum = ANGLE_LIMITS[joint]
    return max(minimum, min(maximum, angle))


def axis_value(joystick: pygame.joystick.Joystick, axis: int) -> float:
    if axis >= joystick.get_numaxes():
        return 0.0

    value = joystick.get_axis(axis)
    return 0.0 if abs(value) < DEADZONE else value


def button_pressed(joystick: pygame.joystick.Joystick, button: int) -> bool:
    return button < joystick.get_numbuttons() and joystick.get_button(button) == 1


def move_cartesian_position(
    position: CartesianPosition,
    dx: float,
    dy: float,
    dz: float,
) -> CartesianPosition:
    # TODO: After you give the arm dimensions, add workspace limits here so
    # joystick input cannot ask for an unreachable or unsafe XYZ position.
    return CartesianPosition(
        x=position.x + dx,
        y=position.y + dy,
        z=position.z + dz,
    )


def position_from_joystick(
    joystick: pygame.joystick.Joystick,
    cartesian_position: CartesianPosition,
    arm_position: ArmPosition,
) -> tuple[CartesianPosition, ArmPosition]:
    x_axis = axis_value(joystick, JOYSTICK_AXES["x"])
    y_axis = axis_value(joystick, JOYSTICK_AXES["y"])
    z_axis = axis_value(joystick, JOYSTICK_AXES["z"])

    next_cartesian_position = move_cartesian_position(
        cartesian_position,
        dx=x_axis * JOYSTICK_AXIS_DIRECTIONS["x"] * CARTESIAN_STEP_MM,
        dy=y_axis * JOYSTICK_AXIS_DIRECTIONS["y"] * CARTESIAN_STEP_MM,
        dz=z_axis * JOYSTICK_AXIS_DIRECTIONS["z"] * CARTESIAN_STEP_MM,
    )

    gripper = arm_position.gripper

    if button_pressed(joystick, 4):
        gripper = clamp_joint("gripper", gripper - GRIPPER_STEP)
    if button_pressed(joystick, 5):
        gripper = clamp_joint("gripper", gripper + GRIPPER_STEP)

    if button_pressed(joystick, 0):
        next_cartesian_position = CartesianPosition(**CARTESIAN_HOME)
        gripper = HOME_POSITION["gripper"]

    next_arm_position = cartesian_to_arm_position(
        next_cartesian_position,
        gripper=gripper,
        wrist=arm_position.wrist,
    )
    return next_cartesian_position, next_arm_position


def wait_for_joystick() -> pygame.joystick.Joystick:
    while pygame.joystick.get_count() == 0:
        print("Waiting for joystick/gamepad...")
        pygame.event.pump()
        time.sleep(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Using joystick: {joystick.get_name()}")
    print(f"Axes: {joystick.get_numaxes()}, buttons: {joystick.get_numbuttons()}")
    return joystick


def log_axis_snapshot(joystick: pygame.joystick.Joystick) -> None:
    pygame.event.pump()
    values = [
        f"{axis}={joystick.get_axis(axis):+.2f}"
        for axis in range(joystick.get_numaxes())
    ]
    print("Axis snapshot -> " + ", ".join(values))
    print(
        "Mapping -> "
        f"x=axis{JOYSTICK_AXES['x']}*{JOYSTICK_AXIS_DIRECTIONS['x']}, "
        f"y=axis{JOYSTICK_AXES['y']}*{JOYSTICK_AXIS_DIRECTIONS['y']}, "
        f"z=axis{JOYSTICK_AXES['z']}*{JOYSTICK_AXIS_DIRECTIONS['z']}"
    )


def log_position(cartesian_position: CartesianPosition, arm_position: ArmPosition) -> None:
    def format_joint(joint: str, angle: int) -> str:
        minimum, maximum = ANGLE_LIMITS[joint]
        marker = " LIMIT" if angle == minimum or angle == maximum else ""
        return f"{angle}{marker}"

    print(
        "XYZ -> "
        f"x={cartesian_position.x:.1f} y={cartesian_position.y:.1f} z={cartesian_position.z:.1f} "
        "| Angles -> "
        f"base={format_joint('base_rotation', arm_position.base_rotation)} "
        f"shoulder={format_joint('base_lift', arm_position.base_lift)} "
        f"elbow={format_joint('elbow', arm_position.elbow)} "
        f"wrist={format_joint('wrist', arm_position.wrist)} "
        f"gripper={format_joint('gripper', arm_position.gripper)}"
    )


def main() -> None:
    pygame.init()
    pygame.joystick.init()

    joystick = wait_for_joystick()
    log_axis_snapshot(joystick)
    cartesian_position = CartesianPosition(**CARTESIAN_HOME)
    position = cartesian_to_arm_position(
        cartesian_position,
        gripper=HOME_POSITION["gripper"],
        wrist=HOME_POSITION["wrist"],
    )

    print("Joystick control started. Press Ctrl+C to stop.")
    print("Configured joystick axes control X/Y/Z")
    print("LB/RB: close/open gripper")
    print("A: home position")

    try:
        with RoboticArmController() as arm:
            arm.move_to(position)
            log_position(cartesian_position, position)

            while True:
                pygame.event.pump()
                next_cartesian_position, next_position = position_from_joystick(
                    joystick,
                    cartesian_position,
                    position,
                )

                if next_position != position:
                    arm.move_to(next_position)
                    cartesian_position = next_cartesian_position
                    position = next_position
                    log_position(cartesian_position, position)

                time.sleep(LOOP_SECONDS)
    except KeyboardInterrupt:
        print("\nJoystick control stopped.")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
