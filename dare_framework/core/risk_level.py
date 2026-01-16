from enum import Enum


class RiskLevel(Enum):
    READ_ONLY = "read_only"
    IDEMPOTENT_WRITE = "idempotent_write"
    NON_IDEMPOTENT_EFFECT = "non_idempotent_effect"
    COMPENSATABLE = "compensatable"