from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, NAME
from .modbus import modbus_regs_to_hex_string


class VistaPoolEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id

    # Generate a unique object ID for the entity to use in Home Assistant
    # This remove the prefix "mbf_" and "par_" from the key and replaces spaces, dashes, and dots with underscores
    @staticmethod
    def slugify(name):
        return name.lower().replace("mbf_", "", 1).replace("par_", "", 1).replace(" ", "_").replace("-", "_").replace(".", "_").replace(":", "_").replace(",", "_").replace("(", "_").replace(")", "_").replace("[", "_").replace("]", "_").replace("{", "_").replace("}", "_").replace("'", "_").replace('"', "_").replace("&", "_").replace("%", "_").replace("$", "_").replace("#", "_")
    
    @property
    def translation_key(self):
        return getattr(self, "_attr_translation_key", None)
    
    @property
    def device_info(self) -> dict:
        serial_number = modbus_regs_to_hex_string(self.coordinator.data.get("MBF_POWER_MODULE_NODEID"))
        info = {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": getattr(self.coordinator, "device_name", NAME),
            "model": "NeoPool compatible",
            "manufacturer": "Sugar Valley",
            "hw_version": f"Detected Modules: [{self.decode_modules(self.coordinator.data.get("MBF_PAR_MODEL"))}]",
            "sw_version": f"v{self.coordinator.firmware} (v{self.coordinator.parse_version(self.coordinator.data.get('MBF_PAR_VERSION'))})",
            "serial_number": serial_number,
        }
        return info

    @staticmethod
    def decode_modules(model_bitmask):
        """Decode MBF_PAR_MODEL bitmask into a human-readable string."""
        if model_bitmask is None:
            return "Unknown"
        modules = []
        if model_bitmask & 0x0001:
            modules.append("Ionization")
        if model_bitmask & 0x0002:
            modules.append("Hydro/Electrolysis")
        if model_bitmask & 0x0004:
            modules.append("UV Lamp")
        if model_bitmask & 0x0008:
            modules.append("Salinity")
        return ", ".join(modules) if modules else "None"
