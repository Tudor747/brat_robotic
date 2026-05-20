from __future__ import annotations

from arm_controller import RoboticArmController
from config import CARTESIAN_HOME, HOME_POSITION
from kinematics import CartesianPosition, IkSolution, solve_ik


HELP_TEXT = """
Inverse kinematics baby-step tester

Type a target like this:
  250 0 160

That means:
  x = forward/back in millimeters
  y = left/right in millimeters
  z = height from the table/base in millimeters

Commands:
  move  -> send the last printed angles to the robot
  home  -> go back to the configured CARTESIAN_HOME
  quit  -> stop
""".strip()


def print_solution(solution: IkSolution) -> None:
    position = solution.arm_position
    print()
    print(
        "Target: "
        f"x={solution.target.x:.1f}mm "
        f"y={solution.target.y:.1f}mm "
        f"z={solution.target.z:.1f}mm"
    )
    print(
        "Math angles: "
        f"base={solution.base_angle_degrees:.1f} "
        f"shoulder={solution.shoulder_angle_degrees:.1f} "
        f"elbow={solution.elbow_angle_degrees:.1f} "
        f"wrist-servo-before-limit={solution.wrist_angle_degrees:.1f}"
    )
    print(
        "Servo angles: "
        f"base={position.base_rotation} "
        f"shoulder={position.base_lift} "
        f"elbow={position.elbow} "
        f"wrist={position.wrist} "
        f"gripper={position.gripper}"
    )

    if solution.target_was_clamped:
        print(
            "Note: this point was outside the arm reach, so IK used "
            f"{solution.used_wrist_reach_mm:.1f}mm instead of "
            f"{solution.requested_wrist_reach_mm:.1f}mm."
        )


def parse_target(text: str) -> CartesianPosition:
    parts = text.split()

    if len(parts) != 3:
        raise ValueError("Type exactly 3 numbers: x y z")

    return CartesianPosition(
        x=float(parts[0]),
        y=float(parts[1]),
        z=float(parts[2]),
    )


def main() -> None:
    print(HELP_TEXT)
    target = CartesianPosition(**CARTESIAN_HOME)
    solution = solve_ik(target, gripper=HOME_POSITION["gripper"])
    print_solution(solution)
    arm: RoboticArmController | None = None

    try:
        while True:
            text = input("\nIK> ").strip().lower()

            if text in {"quit", "exit", "q"}:
                break

            if text == "move":
                if arm is None:
                    arm = RoboticArmController()
                    arm.connect()

                arm.move_to(solution.arm_position)
                print("Moved.")
                continue

            if text == "home":
                target = CartesianPosition(**CARTESIAN_HOME)
            else:
                try:
                    target = parse_target(text)
                except ValueError as error:
                    print(error)
                    continue

            solution = solve_ik(target, gripper=HOME_POSITION["gripper"])
            print_solution(solution)
    finally:
        if arm is not None:
            arm.close()


if __name__ == "__main__":
    main()
