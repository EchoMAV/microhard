#!/usr/bin/env python3
from typing import Any, List, Optional

from constants import ActionTypes
import os


class Validator:
    """
    This validation only checks that based on the provided action certain arguments are non default.
    The GCS and microhard should have a more robust validation system.
    """

    def __init__(self, args: Optional[Any] = None) -> None:
        self.args = args
        if self.args:
            if not self._validate_args():
                raise Exception("Invalid arguments")

    def _validate_args(self) -> bool:
        if not self.args:
            raise ValueError("No arguments provided")

        self.validate_action(str(self.args.action))

        if self.args.action != ActionTypes.RSSI.value:
            self.args.monark_id = 0
        self.validate_monark_id(int(self.args.monark_id))

        if self.args.action == ActionTypes.PAIR.value:
            return self.all_fields_truthy(
                ["network_id", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.action == ActionTypes.UPDATE.value:
            return self.all_fields_truthy(["monark_id"]) and self.one_field_truthy(
                ["network_id", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            return self.all_fields_truthy(["monark_id"])
        else:
            return bool(self.args.action)

    def validate_action(self, action: str) -> bool:
        supported_actions = [a.value for a in ActionTypes.__members__.values()]
        if not action in supported_actions:
            raise ValueError(f"{action} not in {supported_actions}")
        return True

    def validate_monark_id(self, monark_id: int) -> bool:
        if monark_id >= 0 and monark_id <= 255:
            return True
        raise ValueError(f"Monark ID must be between 1 and 255")

    def all_fields_truthy(self, field_names: List[str]) -> bool:
        if not all([bool(getattr(self.args, arg)) for arg in field_names]):
            raise ValueError(f"Missing fields: {field_names}")
        return True

    def one_field_truthy(self, field_names: List[str]) -> bool:
        if not any([bool(getattr(self.args, arg)) for arg in field_names]):
            raise ValueError(
                f"Missing ate least one field from the following: {field_names}"
            )
        return True
