#!/usr/bin/env python3
from typing import Final
from enum import Enum

OK: Final = "OK"
YES: Final = "YES"
NO: Final = "NO"
FAILURE: Final = "FAILURE"
MONARK_ID_FILE_NAME: Final = "/usr/local/echopilot/monarkProxy/monark_id.txt"
MICROHARD_USER: Final = "admin"
MICROHARD_DEFAULT_PASSWORD: Final = "admin"
MICROHARD_DEFAULT_IP: Final = "192.168.168.1"
MICROHARD_IP_PREFIX: Final = "172.20.2"
MAX_MONARK_ID: Final = 255
ENCRYPTION_KEY: Final = "ENCRYPTION_KEY"
NEW_ENCRYPTION_KEY: Final = "NEW_ENCRYPTION_KEY"


class ActionTypes(Enum):
    """
    These are the types of command actions the GCS can perform.
    """

    PAIR = "pair"
    INFO = "info"
    UPDATE = "update"
    UPDATE_ENCRYPTION_KEY = "update_encryption_key"
    IS_FACTORY = "is_factory"
