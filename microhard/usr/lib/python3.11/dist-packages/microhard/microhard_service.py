#!/usr/bin/env python3
from typing import List, Tuple
import time
from constants import (
    MICROHARD_DEFAULT_IP,
    MICROHARD_DEFAULT_PASSWORD,
    MICROHARD_IP_PREFIX,
    MICROHARD_USER,
)
import paramiko
import subprocess
from functools import cached_property
import os


class MicrohardService:
    def __init__(self, action: str, monark_id: int, verbose: bool = False) -> None:
        # Set up the SSH client
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.monark_id = int(monark_id)
        self.action = action
        self.verbose = verbose

    @cached_property
    def paired_microhard_ip(self) -> str:
        """
        The intended provisioned microhard radio IP after pairing
        """
        return f"{MICROHARD_IP_PREFIX}.{self.monark_id}"

    @cached_property
    def active_microhard_ip(self) -> str:
        """
        The current microhard radio IP (i.e. default or provisioned)
        """
        if self.is_default_microhard:
            ip = MICROHARD_DEFAULT_IP
        else:
            ip = self.paired_microhard_ip

        if self.verbose:
            print(f"Active MONARK IP: {ip}")

        return ip

    @cached_property
    def is_default_microhard(self) -> bool:
        """
        Return True if 192.168.168.1 can be pinged
        """
        try:
            # Ping the IP address and check for response within 200 ms
            output = subprocess.run(
                ["ping", "-c", "1", "-W", "200", MICROHARD_DEFAULT_IP],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=0.75,
            )
            # Check if the ping was successful
            return output.returncode == 0
        except Exception as e:
            if self.verbose:
                print(f"Error: {e}")
        return False

    def pair_monark(
        self,
        network_id: str,
        encryption_key: str,
        tx_power: int,
        frequency: int,
    ) -> Tuple[bool, List[str]]:
        at_commands = [
            f"AT+MWRADIO=1",  # turn on radio
            f"AT+MWVMODE=1",  # slave mode
            f"AT+MWTXPOWER={tx_power}",
            f"AT+MWNETWORKID={network_id}",
            f"AT+MWFREQ={frequency}",
            f"AT+MWDISTANCE=8047",  # 5 miles
            f"AT+MWVENCRYPT=2,{encryption_key}",
            f"AT+MSPWD={encryption_key},{encryption_key}",
            f"AT+MNLAN=LAN,EDIT,0,{self.paired_microhard_ip},255.255.0.0,0",  # the target paired IP
            f"AT+MNLANDHCP=LAN,0",  # disable DHCP server
            "AT&W",  # save and write
        ]

        _password = (
            MICROHARD_DEFAULT_PASSWORD if self.is_default_microhard else encryption_key
        )

        is_success, responses = self.send_commands(
            ip_address=self.active_microhard_ip,  # send to active microhard IP
            password=_password,
            at_commands=at_commands,
        )

        return is_success, responses

    def get_info(self, encryption_key: str) -> dict:
        """
        Returns tx_power, frequency, and monark_id in json format.
        If any of the AT commands fail then it will return error.
        """
        at_commands = [
            f"AT+MWTXPOWER",
            f"AT+MWFREQ",
        ]
        is_success, responses = self.send_commands(
            ip_address=self.active_microhard_ip,
            password=encryption_key,
            at_commands=at_commands,
        )
        if not is_success:
            return {}

        # format response to json
        _tx_power = responses[0].split("MWTXPOWER: ")[1].strip()
        _tx_power = _tx_power.split("dBm")[0].strip()
        _frequency = responses[1].split("MWFREQ: ")[1].strip()
        _frequency = _frequency.split("MHz")[0].strip()
        return {
            "tx_power": _tx_power,
            "frequency": _frequency,
            "monark_id": self.monark_id,
        }

    def send_commands(
        self, password: str, at_commands: List[str], ip_address: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Runs at_commands one by one on the microhard radio at admin@{ip_address} using the given password.
        Returns a tuple of (success, responses) where success is a boolean and responses is a list of strings.
        """
        try:
            if not ip_address:
                ip_address = self.active_microhard_ip

            # Connect to the Microhard radio
            try:
                if os.path.exists("/home/echopilot/.ssh/known_hosts"):
                    os.remove("/home/echopilot/.ssh/known_hosts")
                self.client.connect(
                    ip_address, username=MICROHARD_USER, password=password
                )
                if self.verbose:
                    print(f"Connected to {ip_address}")
            except Exception as e:
                if self.verbose:
                    print(f"Unable to Connect to Radio: {e}")
                return False, [str(e)]

            # Start an interactive shell session
            shell = self.client.invoke_shell()
            time.sleep(2)  # Give some time for the shell to open

            responses = []

            # Send AT commands
            i = 0
            should_continue = True
            for command in at_commands:
                if should_continue == False:
                    break
                i += 1
                _status = f"{i}/{len(at_commands)}"

                if self.verbose:
                    print(f"Running command {_status}")

                shell.send(command + "\n")
                time.sleep(0.1)

                # We wait for "OK" to be returned before sending the next command (up to limit)
                end_time = time.time() + 15
                response = ""
                while time.time() < end_time:
                    if shell.recv_ready():
                        part = shell.recv(1024).decode()
                        response += part
                        # Check if the output contains a prompt or specific end marker
                        if "\nOK\r" in part:
                            break
                        elif "ERROR" in part:
                            should_continue = False
                            print(f"Error occurred: {part}")
                            break
                    else:
                        time.sleep(0.1)

                responses.append(response)

            shell.close()
            self.client.close()
            if self.verbose:
                print("Session closed.")
            return should_continue, responses  # should_continue correlates to success

        except Exception as e:
            print(f"An error occurred: {e}")
            return False, []
