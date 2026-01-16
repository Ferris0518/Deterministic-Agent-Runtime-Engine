from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_VALIDATORS
from dare_framework.core.validator.validator import IValidator


class ValidatorManager(BaseComponentManager[IValidator]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_VALIDATORS, IValidator, entry_points_loader, config_section="validators")
