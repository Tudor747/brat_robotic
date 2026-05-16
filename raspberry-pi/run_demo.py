from arm_controller import ArmPosition, RoboticArmController
from config import HOME_POSITION


def main() -> None:
    home = ArmPosition(**HOME_POSITION)

    demo_positions = [
        home,
        ArmPosition(base_rotation=70, base_lift=100, elbow=95, wrist=90, gripper=45),
        ArmPosition(base_rotation=110, base_lift=100, elbow=95, wrist=90, gripper=45),
        ArmPosition(base_rotation=90, base_lift=85, elbow=110, wrist=90, gripper=70),
        home,
    ]

    with RoboticArmController() as arm:
        for position in demo_positions:
            print(f"Moving to {position}")
            arm.move_to(position)


if __name__ == "__main__":
    main()
