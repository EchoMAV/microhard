import subprocess
import os
from time import sleep
from typing import Tuple
from constants import SD_CARD_LOCATION, SD_CARD_MOUNTED_LOCATION, UPDATE_FILE_NAME
import RPi.GPIO as GPIO


class SDCardService:
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(6, GPIO.OUT)  # Drives buzzer

    def is_sd_card_present() -> Tuple[bool, bool]:
        try:
            # Run the command and capture the output
            result = subprocess.run(
                ["sudo", "fdisk", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2,
            )
            # TODO return whether is is mounted as well
            if SD_CARD_LOCATION in result.stdout:
                return True
            return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def mount_sd_card(self, is_read_only: bool = True) -> bool:
        try:
            # Run the command and capture the output
            os.makedirs(SD_CARD_MOUNTED_LOCATION, exist_ok=True)
            command = ["sudo", "mount", SD_CARD_LOCATION, SD_CARD_MOUNTED_LOCATION]
            if is_read_only:
                command = [
                    "sudo",
                    "mount",
                    "-o",
                    "ro",
                    SD_CARD_LOCATION,
                    SD_CARD_MOUNTED_LOCATION,
                ]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return True
            return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def unmount_sd_card(self) -> bool:
        try:
            # Run the command and capture the output
            os.makedirs(SD_CARD_MOUNTED_LOCATION, exist_ok=True)
            command = ["sudo", "umount", SD_CARD_MOUNTED_LOCATION]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return True
            return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def is_update_file_present(self):
        return os.listdir(SD_CARD_MOUNTED_LOCATION) == [UPDATE_FILE_NAME]

    def _play_mounted_buzz(self):
        for _ in range(1, 3):
            GPIO.output(6, GPIO.HIGH)  # Set GPIO 6 high
            sleep(0.1)  # Wait for 100ms
            GPIO.output(6, GPIO.LOW)  # Set GPIO 6 low
            sleep(0.1)  # Wait for 100ms

    def run(self) -> None:
        while True:
            is_present, is_mounted = self.is_sd_card_present()
            if is_present and not is_mounted:
                if self.mount_sd_card(is_read_only=False):
                    print("SD card is mounted.")
                    self._play_mounted_buzz()
                    if self.is_update_file_present():
                        print("Update file is present.")
                        # TODO Kick off process to update the system - wait for it to finish
                    else:
                        print("Update file is not present.")
                else:
                    raise Exception("SD card could not be mounted.")
            sleep(3)
