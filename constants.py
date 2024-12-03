from typing import Final
from enum import Enum

OK: Final = "OK"
FAILURE: Final = "FAILURE"
DEFAULT_ID: Final = 0
MONARK_ID_FILE_PATH: Final = "monark_id.txt"  # TODO change this later during deploy
PAIR_STATUS_FILE_PATH: Final = "/tmp/pair_status.txt"  # used so that the microhard service can check the status of the microhard (also serves as lockfile)
MICROHARD_USER: Final = "admin"
MICROHARD_DEFAULT_PASSWORD: Final = "admin"
MICROHARD_DEFAULT_IP: Final = "192.168.168.1"
MICROHARD_IP_PREFIX: Final = "172.20.2"
MAX_MONARK_ID: Final = 255


class ActionTypes(Enum):
    """
    These are the types of command actions the GCS can perform.
    """

    PAIR = "pair"
    PAIR_STATUS = "pair_status"
    INFO = "info"
    UPDATE = "update"
    UPDATE_ENCRYPTION_KEY = "update_encryption_key"
    IS_FACTORY = "is_factory"
