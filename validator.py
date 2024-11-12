from typing import Any, List, Optional

from constants import ActionTypes


class Validator:
    """
    This validation only checks that based on the provided action certain arguments are non default.
    The GCS and microhard should have a more robust validation system.
    """

    def __init__(self, args: Optional[Any] = None) -> None:
        self.args = args
        if self.args:
            self._validate_args()

    def _validate_args(self) -> bool:
        if not self.args:
            raise ValueError("No arguments provided")

        self.validate_action(str(self.args.action))
        self.validate_encryption_key(
            str(self.args.encryption_key), str(self.args.new_encryption_key)
        )

        if self.args.action == ActionTypes.PAIR.value:
            return self.all_fields_truthy(
                ["network_id", "encryption_key", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.action == ActionTypes.UPDATE_PARAM.value:
            return self.all_fields_truthy(["encryption_key"]) and self.one_field_truthy(
                ["network_id", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            return self.all_fields_truthy(["encryption_key", "new_encryption_key"])
        else:
            return bool(self.args.action)

    def validate_action(self, action: str) -> bool:
        supported_actions = [a.value for a in ActionTypes.__members__.values()]
        if not action in supported_actions:
            raise ValueError(f"{action} not in {supported_actions}")
        return True

    def validate_encryption_key(
        self, encryption_key: str, new_encryption_key: str
    ) -> bool:
        if encryption_key and not len(encryption_key) >= 8:
            raise ValueError(f"Encryption key must be at least 8 characters long")
        if new_encryption_key and not len(new_encryption_key) >= 8:
            raise ValueError(f"New encryption key must be at least 8 characters long")
        return True

    def all_fields_truthy(self, field_names: List[str]) -> bool:
        return all([bool(getattr(self.args, arg)) for arg in field_names])

    def one_field_truthy(self, field_names: List[str]) -> bool:
        return any([bool(getattr(self.args, arg)) for arg in field_names])
