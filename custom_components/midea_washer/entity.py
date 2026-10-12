from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WASHER_TYPES
from .coordinator import MideaWasherCoordinator


class MideaWasherEntity(CoordinatorEntity[MideaWasherCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        device_type = int(entry.data["device_type"])
        device_id = entry.data["device_id"]
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": f"{WASHER_TYPES.get(device_type, 'Washer')} {entry.data['host']}",
            "manufacturer": "Midea",
            "model": entry.data.get("model") or WASHER_TYPES.get(device_type, "Washer"),
        }

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        return bool(self.coordinator.data.get("available", True))
