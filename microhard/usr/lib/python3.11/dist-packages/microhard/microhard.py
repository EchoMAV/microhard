#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, "/usr/lib/python3.11/dist-packages/microhard/")

import argparse
from constants import (
    ENCRYPTION_KEY,
    MONARK_ID_FILE_NAME,
    NEW_ENCRYPTION_KEY,
    NO,
    OK,
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
        self.encryption_key = os.environ.get(ENCRYPTION_KEY, "").strip()
        self.new_encryption_key = os.environ.get(NEW_ENCRYPTION_KEY, "").strip()
        self.tx_power = tx_power
        self.frequency = frequency
        self.monark_id = monark_id
        self.verbose = verbose

        # The MONARK ID is saved every time this service is invoked. It's value is 1-255.
        if not os.path.exists(MONARK_ID_FILE_NAME):
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
                encryption_key=self.encryption_key,
                tx_power=self.tx_power,
                frequency=self.frequency,
            )
            if self.verbose:
                print(f"Microhard pair responses: {responses}")
            ret_msg = "Pairing is successful." if ret_status else "Pairing failed."
        elif self.action == ActionTypes.INFO.value:
            ret_msg = MicrohardService(
                action=self.action, verbose=self.verbose, monark_id=self.monark_id
            ).get_info(encryption_key=self.encryption_key)
            ret_status = bool(ret_msg)
        elif self.action == ActionTypes.IS_FACTORY.value:
            ret_status = MicrohardService(
                action=self.action, verbose=self.verbose, monark_id=self.monark_id
            ).is_default_microhard
            ret_msg = YES if ret_status else NO
        elif self.action == ActionTypes.UPDATE.value:
            _at_commands = []
            ret_status = True
            microhard_service = MicrohardService(
                action=self.action, verbose=self.verbose, monark_id=self.monark_id
            )

            if self.tx_power:
                _at_commands.append(f"AT+MWTXPOWER={self.tx_power}")
            if self.frequency:
                _at_commands.append(f"AT+MWFREQ={self.frequency}")
            if self.network_id:
                _at_commands.append(f"AT+MWNETWORKID={self.network_id}")

            if _at_commands:
                _at_commands.append("AT&W")
                ret_status, _ = microhard_service.send_commands(
                    password=self.encryption_key, at_commands=_at_commands
                )

            if ret_status:
                ret_msg = microhard_service.get_info(encryption_key=self.encryption_key)
            else:
                ret_msg = "Failed to update parameters."

        elif self.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            ret_status, _ = microhard_service.send_commands(
                password=self.encryption_key,
                at_commands=[
                    f"AT+MSPWD={self.new_encryption_key},{self.new_encryption_key}"
                ],
            )
            if ret_status:
                ret_msg = OK

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
