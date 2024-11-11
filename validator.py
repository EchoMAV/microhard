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
            return False
        if not (self.validate_action(str(self.args.gcs_ip))):
            return False

        if self.args.gcs_ip.action == ActionTypes.PAIR.value:
            return self.all_fields_truthy(
                ["network_id", "encryption_key", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.gcs_ip.action == ActionTypes.UPDATE_PARAM.value:
            return self.all_fields_truthy(["encryption_key"]) and self.one_field_truthy(
                ["network_id", "tx_power", "frequency", "monark_id"]
            )
        elif self.args.gcs_ip.action in [
            ActionTypes.LOGIN.value,
            ActionTypes.INFO.value,
        ]:
            return self.all_fields_truthy(["encryption_key"])
        elif self.args.gcs_ip.action == ActionTypes.UPDATE_ENCRYPTION_KEY.value:
            return self.all_fields_truthy(["encryption_key", "new_encryption_key"])

        return True

    def validate_action(self, action: str) -> bool:
        return action in ActionTypes.__members__.values()

    def all_fields_truthy(self, field_names: List[str]) -> bool:
        return all([bool(getattr(self.args, arg)) for arg in field_names])

    def one_field_truthy(self, field_names: List[str]) -> bool:
        return any([bool(getattr(self.args, arg)) for arg in field_names])
