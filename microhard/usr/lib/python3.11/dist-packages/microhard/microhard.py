#!/usr/bin/env python3

import subprocess
import sys
import os
from typing import Final

INSTALL_PATH: Final = "/usr/lib/python3.11/dist-packages/microhard/"
sys.path.insert(0, INSTALL_PATH)

import argparse
from constants import (
    CHECKSUM_FILE_NAME,
    MONARK_ID_FILE_NAME,
    NAMESPACE_URI,
    NEWEK,
    NO,
    YES,
    ActionTypes,
)
from microhard_service import MicrohardService
from validator import Validator


class Microhard:
    def __init__(
        self,
        action: str,
        network_id: str,
        tx_power: int,
        frequency: int,
        monark_id: int,
        verbose: bool,
    ) -> None:
        self.action = action
        self.network_id = network_id
        with open(CHECKSUM_FILE_NAME, "r") as f:
            self.ek = "".join(
                chr(b ^ ord(NAMESPACE_URI[i % len(NAMESPACE_URI)]))
                for i, b in enumerate(bytes.fromhex(f.read().strip()))
            )
        self.nek = os.environ.get(NEWEK, "").strip()
        self.tx_power = tx_power
        self.frequency = frequency
        self.monark_id = monark_id
        self.verbose = verbose

        # The MONARK ID is saved every time this service is invoked. It's value is 1-255.
        if not os.path.exists(MONARK_ID_FILE_NAME):
            if self.action == ActionTypes.RSSI.value:
                raise Exception("MONARK ID must exist for RSSI mode.")
            print("MONARK ID file not found- creating it now.")
            os.makedirs(os.path.dirname(MONARK_ID_FILE_NAME), exist_ok=True)

        os.chmod(MONARK_ID_FILE_NAME, 0o777)
        with open(MONARK_ID_FILE_NAME, "w") as file:
            file.write(str(self.monark_id))

        if self.verbose:
            print(f"MONARK ID: {self.monark_id}")

    def run(self):
        ret_msg = "Error."
        ret_status = False

        if self.action == ActionTypes.PAIR.value:
            ret_status, responses = MicrohardService(
                action="pair", monark_id=self.monark_id, verbose=self.verbose
            ).pair_monark(
                network_id=self.network_id,
                ek=self.ek,
                tx_power=self.tx_power,
                frequency=self.frequency,
            )
            if self.verbose:
                print(f"Microhard pair responses: {responses}")
            ret_msg = "Pairing is successful." if ret_status else "Pairing failed."
        elif self.action == ActionTypes.INFO.value:
            ret_msg = MicrohardService(
                action=self.action, verbose=self.verbose, monark_id=self.monark_id
            ).get_info(ek=self.ek)
            ret_status = bool(ret_msg)
        # elif self.action == ActionTypes.RSSI.value:
        #     ret_msg = MicrohardService(
        #         action=self.action, verbose=self.verbose, monark_id=self.monark_id
        #     ).rssi_loop()
        elif self.action == ActionTypes.IS_FACTORY.value:
            ret_status = MicrohardService(
                action=self.action, verbose=self.verbose, monark_id=self.monark_id
            ).is_default_microhard
            ret_msg = YES if ret_status else NO
        elif self.action == ActionTypes.UPDATE.value:
            _at_commands = []
            ret_status = True

            if self.tx_power:
                _at_commands.append(f"AT+MWTXPOWER={self.tx_power}")
            if self.frequency:
                _at_commands.append(f"AT+MWFREQ={self.frequency}")
            if self.network_id:
                _at_commands.append(f"AT+MWNETWORKID={self.network_id}")

            if _at_commands:
                _at_commands.append("AT&W")

            # update commands are done async
            command = [
                "/usr/bin/python3",
                "-c",
                (
                    "import sys; "
                    f"sys.path.insert(0, '{INSTALL_PATH}'); "
                    "from microhard_service import MicrohardService; "
                    f"microhard_service = MicrohardService(action='{self.action}', verbose={self.verbose}, monark_id={self.monark_id}); "
                    f"microhard_service.send_commands(ek='{self.ek}', at_commands={_at_commands}); "
                ),
            ]
            subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            ret_status = True
            ret_msg = "Update in progress..."
        elif self.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            _at_commands = [
                f"AT+MSPWD={self.nek},{self.nek}" f"AT+MWVENCRYPT=2,{self.nek}",
            ]
            command = [
                "/usr/bin/python3",
                "-c",
                (
                    "import sys; "
                    f"sys.path.insert(0, '{INSTALL_PATH}'); "
                    "from microhard_service import MicrohardService; "
                    f"microhard_service = MicrohardService(action={self.action}, verbose={self.verbose}, monark_id={self.monark_id}); "
                    f"microhard_service.send_commands(ek={self.ek}, at_commands={_at_commands}); "
                ),
            ]
            subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _checksum = "".join(
                f"{b:02x}"
                for b in [
                    ord(c) ^ ord(NAMESPACE_URI[i % len(NAMESPACE_URI)])
                    for i, c in enumerate(self.nek)
                ]
            )
            subprocess.run(
                ["sudo", "bash", "-c", f'echo "{_checksum}" > {CHECKSUM_FILE_NAME}'],
                check=True,
            )
            ret_status = True
            ret_msg = "Encryption key update is in progress..."
        else:
            raise ValueError(f"Invalid action type {self.action}.")

        print({"is_success": ret_status, "message": ret_msg})
        return ret_status, ret_msg


def main():
    try:
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
            "--tx_power",
            type=int,
            default=0,
            help="The transmission power (in dBm) for the Microhard radio.",
        )
        parser.add_argument(
            "--monark_id",
            type=int,
            required=True,
            help="ID of the drone 1-255 which controls the IP of the microhard slave radio.",
        )
        parser.add_argument(
            "--frequency",
            type=int,
            default=0,
            help="The frequency (in MHz) for the Microhard radio.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output.",
        )

        args = parser.parse_args()
        Validator(args)

        monark = Microhard(
            action=args.action,
            network_id=args.network_id,
            tx_power=args.tx_power,
            frequency=args.frequency,
            monark_id=args.monark_id,
            verbose=args.verbose,
        )

        monark.run()

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
