from typing import List, Tuple
import paramiko
import os
import time
from constants import (
    DEFAULT_ID,
    MICROHARD_DEFAULT_IP,
    MICROHARD_DEFAULT_PASSWORD,
    MICROHARD_IP_PREFIX,
    MICROHARD_USER,
    MONARK_ID_FILE_PATH,
    PAIR_STATUS_FILE_PATH,
)
import fcntl


class MicrohardService:
    def __init__(self):
        # Set up the SSH client
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.monark_id = DEFAULT_ID

        # The MONARK ID determines which IP address to use for the microhard
        if os.path.exists(MONARK_ID_FILE_PATH):
            with open(MONARK_ID_FILE_PATH, "r") as file:
                self.monark_id = int(file.readline().strip())

    @property
    def monark_ip(self) -> str:
        if self.monark_id == DEFAULT_ID:
            return MICROHARD_DEFAULT_IP
        return f"{MICROHARD_IP_PREFIX}.{self.monark_id}0"

    def _save_monark_id(self, monark_id: int):
        if monark_id > 10:
            raise ValueError("Invalid MONARK ID. Must be between 1 and 10.")
        self.monark_id = monark_id
        with open(MONARK_ID_FILE_PATH, "w") as file:
            file.write(str(self.monark_id))

    def pair_monark(
        self,
        network_id: str,
        encryption_key: str,
        tx_power: int,
        frequency: int,
        monark_id: int,
    ) -> Tuple[bool, List[str]]:
        print(f"Pairing Monark...")

        # create the pairing lock file
        with open(PAIR_STATUS_FILE_PATH, "w") as _:
            pass

        at_commands = [
            f"AT+MWRADIO=1",  # turn on radio
            f"AT+MWVMODE=0",  # slave mode
            f"AT+MWTXPOWER={tx_power}",
            f"AT+MWNETWORKID={network_id}",
            f"AT+MWVENCRYPT=2,{encryption_key}",
            f"AT+MSPWD={encryption_key},{encryption_key}",
            f"AT+MWFREQ={frequency}",
            f"AT+MNLAN=LAN,EDIT,0,{self.monark_ip},255.255.0.0,0",
            f"AT+MNLANDHCP=LAN,0",  # disable DHCP server
            "AT&W",  # save and write
        ]
        is_success, responses = self.send_commands(
            ip_address=MICROHARD_DEFAULT_IP,
            password=MICROHARD_DEFAULT_PASSWORD,
            at_commands=at_commands,
        )

        os.remove(PAIR_STATUS_FILE_PATH)

        if is_success:
            self._save_monark_id(monark_id)

        return is_success, responses

    def login(self, encryption_key: str) -> Tuple[bool, List[str]]:
        return self.send_commands(
            ip_address=self.monark_ip, password=encryption_key, at_commands=["AT"]
        )

    def get_info(self, encryption_key: str) -> str:
        """
        Returns "{tx_power},{frequency},{monark_id}"
        If any of the AT commands fail then it will return "No MONARK found."
        """
        at_commands = [
            f"AT+MWTXPOWER",
            f"AT+MWFREQ",
        ]
        is_success, responses = self.send_commands(
            ip_address=self.monark_ip, password=encryption_key, at_commands=at_commands
        )
        if not is_success:
            return "No MONARK found."

        return f"{responses[0].strip()},{responses[1].strip()},{self.monark_id}"

    def change_monark_id(
        self, encryption_key: str, new_monark_id: int
    ) -> Tuple[bool, List[str]]:
        """
        Based on the incoming monark_id, the IP address of the microhard will be changed.
        """
        original_monark_id = self.monark_id
        self._save_monark_id(new_monark_id)

        at_command = f"AT+MNLAN=LAN,EDIT,0,{self.monark_ip},255.255.0.0,0"
        is_success, responses = self.send_commands(
            ip_address=self.monark_ip, password=encryption_key, at_commands=[at_command]
        )

        if not is_success:
            self._save_monark_id(original_monark_id)

        return is_success, responses

    def send_commands(
        self, password: str, at_commands: List[str], ip_address: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Runs at_commands one by one on the microhard radio at admin@{ip_address} using the given password.
        Returns a tuple of (success, responses) where success is a boolean and responses is a list of strings.
        """
        try:
            if not ip_address:
                ip_address = self.monark_ip

            # Connect to the Microhard radio
            self.client.connect(ip_address, username=MICROHARD_USER, password=password)
            print(f"Connected to {ip_address}")

            # Start an interactive shell session
            shell = self.client.invoke_shell()
            time.sleep(2)  # Give some time for the shell to open

            responses = []

            # Send AT commands
            i = 0
            for command in at_commands:
                i += 1
                _status = f"{i}/{len(at_commands)}"
                print(f"Running command {_status}")
                with open(PAIR_STATUS_FILE_PATH, "w") as file:
                    # Acquire an exclusive lock
                    fcntl.flock(file, fcntl.LOCK_EX)
                    try:
                        file.write(_status + "\n")
                    finally:
                        # Release the lock
                        fcntl.flock(file, fcntl.LOCK_UN)

                shell.send(command + "\n")
                time.sleep(0.1)

                # We wait for "OK" to be returned before sending the next command (up to limit)
                end_time = time.time() + 10
                response = ""
                has_failure = False
                while time.time() < end_time:
                    if shell.recv_ready():
                        part = shell.recv(1024).decode()
                        response += part
                        # Check if the output contains a prompt or specific end marker
                        if "OK" in part:
                            break
                        elif (
                            "ERROR" in part
                        ):  # TODO will ERROR work -> what about if no auth?
                            has_failure = True
                            break
                    else:
                        time.sleep(0.1)

                responses.append(response)

            shell.close()
            self.client.close()
            print("Session closed.")
            return not has_failure, responses

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, []
