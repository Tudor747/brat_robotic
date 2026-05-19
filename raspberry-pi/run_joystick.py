from __future__ import annotations

import time

import pygame

from arm_controller import ArmPosition, RoboticArmController
from config import ANGLE_LIMITS, CARTESIAN_HOME, HOME_POSITION
from kinematics import CartesianPosition, cartesian_to_arm_position


DEADZONE = 0.25
LOOP_SECONDS = 0.05
GRIPPER_STEP = 3
MILLIMETERS_PER_TICK = 3.0


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
    left_x = axis_value(joystick, 0)
    left_y = axis_value(joystick, 1)
    right_y = axis_value(joystick, 3)

    next_cartesian_position = move_cartesian_position(
        cartesian_position,
        dx=left_x * MILLIMETERS_PER_TICK,
        dy=-left_y * MILLIMETERS_PER_TICK,
        dz=-right_y * MILLIMETERS_PER_TICK,
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
    return joystick


def log_position(cartesian_position: CartesianPosition, arm_position: ArmPosition) -> None:
    print(
        "XYZ -> "
        f"x={cartesian_position.x:.1f} y={cartesian_position.y:.1f} z={cartesian_position.z:.1f} "
        "| Angles -> "
        f"base={arm_position.base_rotation} shoulder={arm_position.base_lift} "
        f"elbow={arm_position.elbow} wrist={arm_position.wrist} "
        f"gripper={arm_position.gripper}"
    )


def main() -> None:
    pygame.init()
    pygame.joystick.init()

    joystick = wait_for_joystick()
    cartesian_position = CartesianPosition(**CARTESIAN_HOME)
    position = cartesian_to_arm_position(
        cartesian_position,
        gripper=HOME_POSITION["gripper"],
        wrist=HOME_POSITION["wrist"],
    )

    print("Joystick control started. Press Ctrl+C to stop.")
    print("Left stick: X/Y")
    print("Right stick Y: Z")
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
