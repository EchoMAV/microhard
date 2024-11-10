import time
import serial
import os
import subprocess
from constants import BAUD_RATE, OK, PAIR_STATUS_FILE_PATH, SERIAL_PATH, SerialCommands
from microhard_service import MicrohardService


class GCSSerialListener:
    """
    This services runs on the RPi and listens for incoming serial data from the GCS.
    It is configured to continually run as a service daemon.
    """

    def __init__(self, serial_path: str = SERIAL_PATH):
        self.serial_connection = None
        self.serial_path = serial_path
        self.network_id = ""
        self.encryption_key = ""

    def _is_serial_ready(self) -> bool:
        if os.path.exists(self.serial_path):
            try:
                self.serial_connection = serial.Serial(
                    self.serial_path, BAUD_RATE, timeout=0.5
                )
                print("Serial port /dev/ttyUSB0 opened successfully.")
                return True
            except serial.SerialException as e:
                print(f"Failed to open serial port: {e}")

        # If there is no USB-C cable attached, it's important to reset the network_id and
        # encryption_key otherwise it's possible that a downed drone that is captured and
        # still powered on would have this data in readable memory.
        self.network_id = ""
        self.encryption_key = ""
        self.serial_connection = None
        return False

    def _is_logged_in(self) -> bool:
        return bool(self.encryption_key)

    def listen(self):
        # TODO how will we handle when the usb is connected to a laptop for manual picocom connection?

        while True:
            if not self._is_serial_ready():
                time.sleep(3)
                return

            command = self.serial_connection.readline().decode().strip()
            _split_command = command.split("=")
            command_type = _split_command[0].strip().upper()
            command_value = _split_command[1].strip()

            # All commands are blocking expect pairing since it involves several steps.
            # Therefore, the pair command will be run in a separate thread and status can
            # be checked with the PAIR_STATUS command.

            if command_type:
                if command_type == SerialCommands.PAIR.value:
                    if os.path.exists(PAIR_STATUS_FILE_PATH):
                        ret_msg = "Pairing is already in progress. Please wait."
                    else:
                        (
                            network_id,
                            encryption_key,
                            tx_power,
                            frequency,
                            monark_id,
                        ) = command_value.split(",")
                        # run as a thread since we need to free up the serial port for status queries
                        subprocess.run(
                            [
                                "python",
                                "-c",
                                f"from microhard_service import MicrohardService; MicrohardService().pair_monark('{network_id}', '{encryption_key}', {int(tx_power)}, {int(frequency)}, {int(monark_id)})",
                            ]
                        )
                        ret_msg = "Pairing has started..."
                elif command_type == SerialCommands.PAIR_STATUS.value:
                    if os.path.exists(PAIR_STATUS_FILE_PATH):
                        with open(PAIR_STATUS_FILE_PATH, "r") as file:
                            ret_msg = file.readline().strip()
                    else:
                        ret_msg = "Pairing is not in progress."
                elif command_type == SerialCommands.LOGIN.value:
                    is_valid_creds, _ = MicrohardService().login(
                        encryption_key=command_value
                    )
                    if is_valid_creds:
                        self.encryption_key = command_value
                        ret_msg = OK
                    else:
                        ret_msg = "Failed to login."
                elif not self._is_logged_in():
                    ret_msg = "Please login first."
                elif command_type == SerialCommands.INFO.value:
                    ret_msg = MicrohardService().get_info(
                        encryption_key=self.encryption_key
                    )
                elif command_type == SerialCommands.CHANGE_MONARK_ID.value:
                    MicrohardService().change_monark_id(monark_id=int(command_value))
                    ret_msg = OK
                elif command_type == SerialCommands.CHANGE_ENCRYPTION_KEY.value:
                    is_success, ret_msg = MicrohardService().send_commands(
                        password=self.encryption_key, at_commands=[command]
                    )
                    # if this command was successful, we need to update the encryption key
                    if is_success:
                        self.encryption_key = command_value.split(",")[
                            0
                        ]  # it's entered twice in the value
                else:
                    # all other commands are 1:1 and don't need any manipulation
                    _, ret_msg = MicrohardService().send_commands(
                        password=self.encryption_key, at_commands=[command]
                    )

            self.serial_connection.write(ret_msg.encode())
            time.sleep(0.1)  # Small delay to reduce CPU usage
