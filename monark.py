import argparse
import os
import sys
import subprocess
from constants import OK, PAIR_STATUS_FILE_PATH, ActionTypes
from microhard_service import MicrohardService
from validator import Validator


class MONARK:
    def __init__(
        self,
        action: str,
        network_id: str,
        encryption_key: str,
        new_encryption_key: str,
        tx_power: int,
        frequency: int,
        monark_id: int,
    ) -> None:
        self.action = action
        self.network_id = network_id
        self.encryption_key = encryption_key
        self.new_encryption_key = new_encryption_key
        self.tx_power = tx_power
        self.frequency = frequency
        self.monark_id = monark_id

    def run(self):
        ret_msg = "Error."
        ret_status = True
        if self.action == ActionTypes.PAIR.value:
            if os.path.exists(PAIR_STATUS_FILE_PATH):
                ret_msg = "Pairing is already in progress. Please wait."
            else:
                subprocess.run(
                    [
                        "python",
                        "-c",
                        f"from microhard_service import MicrohardService; MicrohardService().pair_monark('{self.network_id}', '{self.encryption_key}', {int(self.tx_power)}, {int(self.frequency)}, {int(self.monark_id)})",
                    ]
                )
                ret_msg = "Pairing has started."
        elif self.action == ActionTypes.PAIR_STATUS.value:
            if os.path.exists(PAIR_STATUS_FILE_PATH):
                with open(PAIR_STATUS_FILE_PATH, "r") as file:
                    ret_msg = file.readline().strip()
            else:
                ret_msg = "Pairing is not in progress."
                ret_status = False
        elif self.action == ActionTypes.LOGIN.value:
            is_valid_creds, _ = MicrohardService().login(
                encryption_key=self.encryption_key
            )
            if is_valid_creds:
                ret_msg = OK
            else:
                ret_msg = "Failed to login."
                ret_status = False
        elif self.action == ActionTypes.INFO.value:
            ret_msg = MicrohardService().get_info(encryption_key=self.encryption_key)
        elif self.action == ActionTypes.UPDATE_PARAM.value:
            _at_commands = []
            _ret_status1 = True
            _ret_status2 = True

            if self.monark_id:
                _ret_status1, _ = MicrohardService().change_monark_id(
                    encryption_key=self.encryption_key, monark_id=self.monark_id
                )

            if self.tx_power:
                _at_commands.append(f"AT+MWTXPOWER={self.tx_power}")
            if self.frequency:
                _at_commands.append(f"AT+MWFREQ={self.frequency}")
            if self.network_id:
                _at_commands.append(f"AT+MWNETWORKID={self.network_id}")
            if self.encryption_key:
                _at_commands.append(f"AT+MSPWD={self.encryption_key}")

            if _at_commands:
                _ret_status2, _ = MicrohardService().send_commands(
                    encryption_key=self.encryption_key, at_commands=_at_commands
                )

            ret_status = _ret_status1 and _ret_status2
            if ret_status:
                ret_msg = OK
            else:
                ret_msg = "Failed to update parameters."

        elif self.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            ret_status, _ = MicrohardService().send_commands(
                encryption_key=self.encryption_key,
                at_commands=[
                    f"AT+MSPWD={self.new_encryption_key},{self.new_encryption_key}"
                ],
            )
            if ret_status:
                ret_msg = OK

        else:
            raise ValueError(f"Invalid action type {self.action}.")

        return ret_status, ret_msg


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="Proxy app for provisioning the MONARK's Microhard radio."
    )

    # Action is required but based on the action, different arguments are required
    parser.add_argument(
        "--action",
        type=str,
        help="The types of command actions the GCS can perform. See `ActionTypes` in constants.py.",
    )
    parser.add_argument(
        "--network_id",
        type=str,
        default="",
        help="The network ID for the Microhard radio.",
    )
    parser.add_argument(
        "--encryption_key",
        type=str,
        default="",
        help="The encryption key for the Microhard radio.",
    )
    parser.add_argument(
        "--new_encryption_key",
        type=str,
        default="",
        help="The new encryption key for the Microhard radio.",
    )
    parser.add_argument(
        "--tx_power",
        type=int,
        default="",
        help="The transmission power (in dBm) for the Microhard radio.",
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default="",
        help="The frequency (in MHz) for the Microhard radio.",
    )
    parser.add_argument(
        "--monark_id",
        type=int,
        default=0,
        help="The ID of the MONARK drone which controls the IP address of the Microhard radio.",
    )
    args = parser.parse_args()

    try:
        Validator(args)
    except Exception as e:
        print(f"Validation Error: {e}")
        sys.exit(1)

    monark = MONARK(
        action=args.action,
        network_id=args.network_id,
        encryption_key=args.encryption_key,
        new_encryption_key=args.new_encryption_key,
        tx_power=args.tx_power,
        frequency=args.frequency,
        monark_id=args.monark_id,
    )

    monark.run()
