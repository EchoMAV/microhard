#!/usr/bin/env python3
from typing import Final
from enum import Enum

OK: Final = "OK"
YES: Final = "YES"
NO: Final = "NO"
FAILURE: Final = "FAILURE"
MONARK_ID_FILE_NAME: Final = "/home/monark/monark_id.txt"
CHECKSUM_FILE_NAME: Final = "/home/monark/.checksum"
NAMESPACE_URI = "http://pix4d.com/camera/1.0/"
MICROHARD_USER: Final = "admin"
MICROHARD_DEFAULT_IP: Final = "192.168.168.1"
MICROHARD_IP_PREFIX: Final = "172.20.2"
MAX_MONARK_ID: Final = 255
NEWEK: Final = "NEWEK"
RSSI_DELAY: Final = 5


class ActionTypes(Enum):
    """
    These are the types of command actions the GCS can perform.
    """

    PAIR = "pair"
    INFO = "info"
    UPDATE = "update"
    UPDATE_ENCRYPTION_KEY = "update_encryption_key"
    IS_FACTORY = "is_factory"
    RSSI = "rssi"
