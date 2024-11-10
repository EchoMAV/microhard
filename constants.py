from typing import Final
from enum import Enum


BAUD_RATE: Final = 115200
SERIAL_PATH: Final = "/dev/ttyUSB0"
OK: Final = "OK"
DEFAULT_ID: Final = 0
MONARK_ID_FILE_PATH: Final = "~/monark_id.txt"
PAIR_STATUS_FILE_PATH: Final = "~/status.txt" # used so that the microhard service can check the status of the microhard (also serves as lockfile)
MICROHARD_USER: Final = "admin"
MICROHARD_DEFAULT_PASSWORD: Final = "admin"
MICROHARD_DEFAULT_IP: Final = "192.168.168.1"
MICROHARD_IP_PREFIX: Final = "172.20.1"

class SerialCommands(Enum):
    """ 
    Some of the command conventions are based on microhard's AT definition.
    """
    # Pairing will only be accepted if the IP address is factory reset to 192.168.168.1
    PAIR = "PAIR" # i.e. `PAIR={network_id},{encryption_key},{tx_power},{frequency},{monark_id}` # performs initial configuration of a reset microhard
    PAIR_STATUS = "PAIR_STATUS" # i.e. `PAIR_STATUS` # returns the status of the pairing as a string like '3/10'
    # Login command needed to authenticate the user before other commands are accepted
    LOGIN = "LOGIN" # i.e. `LOGIN=superstrongpassword123` # logs in with the encryption key to confirm the user
    # The below commands will only work if the user has confirmed a log in
    INFO = "INFO" # i.e. `INFO` # returns `{tx_power},{frequency},{monark_id}`
    CHANGE_MONARK_ID = "MONARK_ID" # i.e. `MONARK_ID=2` # results in the IP address of the microhard getting changed based on the number mapping
    # 1:1 commands that are sent to the microhard directly (login also required)
    CHANGE_TX_POWER = "AT+MWTXPOWER" # i.e. `AT+MWTXPOWER=33` # sets the transmit power of the drone microhard
    CHANGE_FREQUENCY = "AT+MWFREQ" # i.e. `AT+MWFREQ=2310` # sets the transmit power of the drone microhard
    CHANGE_NETWORK_ID = "AT+MWNETWORKID" # i.e. `AT+MWNETWORKID=MONARK-12345` # changes the encryption key
    CHANGE_ENCRYPTION_KEY = "AT+MSPWD" # i.e. `AT+MSPWD=superstrongpassword124,superstrongpassword124` # changes the encryption key