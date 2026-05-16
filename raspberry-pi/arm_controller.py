from __future__ import annotations

import time
from dataclasses import dataclass

import serial

from config import ANGLE_LIMITS, BAUD_RATE, JOINT_ORDER, SERIAL_PORT, SERIAL_TIMEOUT_SECONDS


@dataclass(frozen=True)
class ArmPosition:
    base_rotation: int
    base_lift: int
    elbow: int
    wrist: int
    gripper: int

    def as_command_values(self) -> list[int]:
        return [getattr(self, joint) for joint in JOINT_ORDER]


class RoboticArmController:
    def __init__(
        self,
        port: str = SERIAL_PORT,
        baud_rate: int = BAUD_RATE,
        timeout_seconds: int = SERIAL_TIMEOUT_SECONDS,
    ) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.timeout_seconds = timeout_seconds
        self.serial_connection: serial.Serial | None = None

    def connect(self) -> None:
        self.serial_connection = serial.Serial(
            self.port,
            self.baud_rate,
            timeout=self.timeout_seconds,
        )
        time.sleep(2)
        self._drain_startup_messages()

    def close(self) -> None:
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def move_to(self, position: ArmPosition) -> str:
        self._require_connection()
        self._validate_position(position)

        values = position.as_command_values()
        command = "MOVE " + " ".join(str(value) for value in values) + "\n"

        assert self.serial_connection is not None
        self.serial_connection.write(command.encode("ascii"))
        response = self.serial_connection.readline().decode("ascii", errors="replace").strip()

        if response != "OK":
            raise RuntimeError(f"Arduino rejected command: {response or 'no response'}")

        return response

    def _validate_position(self, position: ArmPosition) -> None:
        for joint in JOINT_ORDER:
            angle = getattr(position, joint)
            minimum, maximum = ANGLE_LIMITS[joint]

            if angle < minimum or angle > maximum:
                raise ValueError(
                    f"{joint} angle {angle} is outside safe range {minimum}-{maximum}"
                )

    def _require_connection(self) -> None:
        if not self.serial_connection or not self.serial_connection.is_open:
            raise RuntimeError("Controller is not connected to the Arduino")

    def _drain_startup_messages(self) -> None:
        assert self.serial_connection is not None

        while self.serial_connection.in_waiting:
            self.serial_connection.readline()

    def __enter__(self) -> "RoboticArmController":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
