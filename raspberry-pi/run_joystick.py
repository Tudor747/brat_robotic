from __future__ import annotations

import time
from dataclasses import replace

import pygame

from arm_controller import ArmPosition, RoboticArmController
from config import ANGLE_LIMITS, HOME_POSITION


DEADZONE = 0.25
LOOP_SECONDS = 0.05
DEGREES_PER_TICK = 2
GRIPPER_STEP = 3

LEFT_X_AXIS = 0
LEFT_Y_AXIS = 1
RIGHT_X_AXIS = 3
RIGHT_Y_AXIS = 4


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


def move_position(position: ArmPosition, joint: str, delta: int) -> ArmPosition:
    current = getattr(position, joint)
    return replace(position, **{joint: clamp_joint(joint, current + delta)})


def position_from_joystick(
    joystick: pygame.joystick.Joystick,
    position: ArmPosition,
) -> ArmPosition:
    left_x = axis_value(joystick, LEFT_X_AXIS)
    left_y = axis_value(joystick, LEFT_Y_AXIS)
    right_x = axis_value(joystick, RIGHT_X_AXIS)
    right_y = axis_value(joystick, RIGHT_Y_AXIS)

    next_position = position
    next_position = move_position(
        next_position,
        "base_rotation",
        round(left_x * DEGREES_PER_TICK),
    )
    next_position = move_position(
        next_position,
        "base_lift",
        round(-left_y * DEGREES_PER_TICK),
    )
    next_position = move_position(
        next_position,
        "elbow",
        round(-right_y * DEGREES_PER_TICK),
    )
    next_position = move_position(
        next_position,
        "wrist",
        round(right_x * DEGREES_PER_TICK),
    )

    if button_pressed(joystick, 4):
        next_position = move_position(next_position, "gripper", -GRIPPER_STEP)
    if button_pressed(joystick, 5):
        next_position = move_position(next_position, "gripper", GRIPPER_STEP)

    if button_pressed(joystick, 0):
        next_position = ArmPosition(**HOME_POSITION)

    return next_position


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


def log_position(position: ArmPosition) -> None:
    print(
        f"Position -> base_rotation={position.base_rotation}, base_lift={position.base_lift}, "
        f"elbow={position.elbow}, wrist={position.wrist}, gripper={position.gripper}"
    )


def log_axis_snapshot(joystick: pygame.joystick.Joystick) -> None:
    pygame.event.pump()
    values = [
        f"{axis}={joystick.get_axis(axis):+.2f}"
        for axis in range(joystick.get_numaxes())
    ]
    print("Axis snapshot -> " + ", ".join(values))
    print(
        "Mapping -> "
        f"left_x={LEFT_X_AXIS}, left_y={LEFT_Y_AXIS}, "
        f"right_x/wrist={RIGHT_X_AXIS}, right_y/elbow={RIGHT_Y_AXIS}"
    )


def main() -> None:
    pygame.init()
    pygame.joystick.init()

    joystick = wait_for_joystick()
    log_axis_snapshot(joystick)
    position = ArmPosition(**HOME_POSITION)

    print("Joystick control started. Press Ctrl+C to stop.")
    print("Left stick: base rotation/lift")
    print("Right stick: wrist/elbow")
    print("LB/RB: close/open gripper")
    print("A: home position")

    try:
        with RoboticArmController() as arm:
            arm.move_to(position)
            log_position(position)

            while True:
                pygame.event.pump()

                next_position = position_from_joystick(joystick, position)

                if next_position != position:
                    arm.move_to(next_position)
                    position = next_position
                    log_position(position)

                time.sleep(LOOP_SECONDS)
    except KeyboardInterrupt:
        print("\nJoystick control stopped.")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
