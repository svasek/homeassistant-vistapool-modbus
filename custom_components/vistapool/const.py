import json
import logging
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.number import NumberDeviceClass
from pathlib import Path

'''
Load the manifest file
This file contains metadata about the integration such as name, version, domain, etc.
The manifest file is loaded to get the integration name and version
The integration name and version are used to identify the integration
and to display information about the integration in Home Assistant
'''
manifest_path = Path(__file__).parent / "manifest.json"
with open(manifest_path, encoding="utf-8") as f:
    MANIFEST = json.load(f)

INTEGRATION_NAME = MANIFEST.get("name")
INTEGRATION_VERSION = MANIFEST.get("version")

DOMAIN = MANIFEST.get("domain").lower().replace("-", "_").replace(" ", "_").replace(".", "_") or "vistapool"
NAME = MANIFEST.get("name") or"VistaPool Integration"
VERSION = MANIFEST.get("version") or None

LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 8899
DEFAULT_SLAVE_ID = 1


SENSOR_DEFINITIONS = {
    "MBF_ION_CURRENT": {
        "name": "Ionization Level",
        "unit": "%",
        "device_class": None,
        "state_class": None,
        "icon": "mdi:atom",
    },
    "MBF_HIDRO_CURRENT": {
        "name": "Hydrolysis Intensity",
        "unit": "%",
        "device_class": None,
        "state_class": None,
    },
    "MBF_MEASURE_PH": {
        "name": "pH Level",
        "unit": "pH",
        "device_class": None,
        "state_class": None,
        "icon": "mdi:ph",
    },
    "MBF_MEASURE_RX": {
        "name": "Redox Potential",
        "unit": "mV",
        "device_class": None,
        "state_class": None,
        "icon": "mdi:gradient-vertical",
    },
    "MBF_MEASURE_CL": {
        "name": "Salt Level",
        "unit": "ppm",
        "device_class": None,
        "state_class": None,
        "icon": "mdi:shaker-outline",
    },
    "MBF_MEASURE_CONDUCTIVITY": {
        "name": "Conductivity Level",
        "unit": "%",
        "device_class": None,
        "state_class": None,
    },
    "MBF_MEASURE_TEMPERATURE": {
        "name": "Water Temperature",
        "unit": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": None,
    },
    "MBF_HIDRO_VOLTAGE": {
        "name": "Hydrolysis Voltage",
        "unit": "V",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "MBF_PAR_FILT_MODE": {
        "name": "Filtration Mode",
        "unit": None,
        "device_class": SensorDeviceClass.ENUM,
        "state_class": None,
    },
    "MBF_PH_STATUS_ALARM": {
        "name": "pH Alarm",
        "unit": None,
        "device_class": SensorDeviceClass.ENUM,
        "state_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Filtration current speed": {
        "name": "Filtration Current Speed",
        "device_class": "motor_speed",
        "state_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "MBF_DEVICE_TIME": {
        "name": "Device Time",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "state_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO_POLARITY": {
        "name": "Hydrolysis Polarity",
        "unit": None,
        "device_class": SensorDeviceClass.ENUM,
        "state_class": None,
        "icon": "mdi:plus-minus-variant",
    },
}

BINARY_SENSOR_DEFINITIONS = {
    # Relay states
    "pH Acid Pump": {
        "name": "pH Regulating",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Filtration Pump": {
        "name": "Filtration Running",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "Pool Light": {
        "name": "Pool Light",
        "device_class": BinarySensorDeviceClass.LIGHT,
        "icon_on": "mdi:lightbulb-on",
        "icon_off": "mdi:lightbulb-outline",
    },
    "AUX1": {
        "name": "Auxiliary Relay 1",
        "device_class": BinarySensorDeviceClass.POWER,
    },
    "AUX2": {
        "name": "Auxiliary Relay 2",
        "device_class": BinarySensorDeviceClass.POWER,
    },
    "AUX3": {
        "name": "Auxiliary Relay 3",
        "device_class": BinarySensorDeviceClass.POWER,
    },
    "AUX4": {
        "name": "Auxiliary Relay 4",
        "device_class": BinarySensorDeviceClass.POWER,
    },
    # "Filtration low speed": {
    #     "name": "Filtration Low Speed",
    #     "device_class": None,
    # },
    # "Filtration mid speed": {
    #     "name": "Filtration Mid Speed",
    #     "device_class": None,
    # },
    # "Filtration high speed": {
    #     "name": "Filtration High Speed",
    #     "device_class": None,
    # },

    # pH/Redox/CL/CD status bits from decode_ph_rx_cl_cd_status_bits
    # pH
    "pH module control status": {
        "name": "pH Control Module Status",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "pH acid pump active": {
        "name": "pH Acid Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "pH pump active": {
        "name": "pH Base Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "pH control module": {
        "name": "pH Control Module",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "pH measurement active": {
        "name": "pH Measurement",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:scale",
        "icon_off": "mdi:scale-off",
    },
    "pH measurement module detected": {
        "name": "pH Measurement Module Detected",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Redox
    "Redox pump active": {
        "name": "Redox Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "Redox control module": {
        "name": "Redox Control Module",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Redox measurement active": {
        "name": "Redox Measurement",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:scale",
        "icon_off": "mdi:scale-off",
    },
    "Redox measurement module detected": {
        "name": "Redox Measurement Module Detected",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Chlorine
    "Chlorine flow sensor problem": {
        "name": "Chlorine Flow Sensor",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Chlorine pump active": {
        "name": "Chlorine Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "Chlorine control module": {
        "name": "Chlorine Control Module",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Chlorine measurement active": {
        "name": "Chlorine Measurement",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:scale",
        "icon_off": "mdi:scale-off",
    },
    "Chlorine measurement module detected": {
        "name": "Chlorine Measurement Module Detected",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Conductivity
    "Conductivity pump active": {
        "name": "Conductivity Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
    },
    "Conductivity control module": {
        "name": "Conductivity Control Module",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "Conductivity measurement active": {
        "name": "Conductivity Measurement",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:scale",
        "icon_off": "mdi:scale-off",
    },
    "Conductivity measurement module detected": {
        "name": "Conductivity Measurement Module Detected",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },

    # Ion status bits
    "ION On Target": {
        "name": "Ionizer On Target",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "ION Low Flow": {
        "name": "Ionizer Low Flow",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # "ION Reserved": {
    #     "name": "Ionizer Reserved",
    #     "device_class": None,
    #     "entity_category": EntityCategory.DIAGNOSTIC,
    # },
    "ION Program time exceeded": {
        "name": "Ionizer Program Time Exceeded",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "ION in dead time": {
        "name": "Ionizer In Dead Time",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "ION in Pol1": {
        "name": "Ionizer Polarity 1",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "ION in Pol2": {
        "name": "Ionizer Polarity 2",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    
    # Hydrolysis status bits
    "HIDRO On Target": {
        "name": "Hydrolysis On Target",
        "device_class": None, 
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Low Flow": {
        "name": "Hydrolysis Low Flow",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # "HIDRO Reserved": {
    #     "name": "Hydrolysis Reserved",
    #     "device_class": None,
    #     "entity_category": EntityCategory.DIAGNOSTIC,
    # },
    "HIDRO Cell Flow FL1": {
        "name": "Hydrolysis Cell Flow FL1",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Cover input active": {
        "name": "Hydrolysis Cover Input Active",
        "device_class": BinarySensorDeviceClass.OPENING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Module active": {
        "name": "Hydrolysis Module Active",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Module regulated": {
        "name": "Hydrolysis Module Regulated",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Activated by the RX module": {
        "name": "Hydrolysis Activated by Redox Module",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Chlorine shock mode": {
        "name": "Hydrolysis Chlorine Shock Mode",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Chlorine flow indicator FL2": {
        "name": "Hydrolysis Chlorine Flow Indicator FL2",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO Activated by the CL module": {
        "name": "Hydrolysis Activated by Chlorine Module",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    "HIDRO in dead time": {
        "name": "Hydrolysis In Dead Time",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Replaced by HIDRO Polarity sensor
    # "HIDRO in Pol1": {
    #     "name": "Hydrolysis Polarity 1",
    #     "device_class": None,
    #     "entity_category": EntityCategory.DIAGNOSTIC,
    # },
    # "HIDRO in Pol2": {
    #     "name": "Hydrolysis Polarity 2",
    #     "device_class": None,
    #     "entity_category": EntityCategory.DIAGNOSTIC,
    # },
}

NUMBER_DEFINITIONS = [
    {
        "name": "Hydrolisis target production level",
        "unit": "%",
        "min": 0.0,
        "max": 100.0,
        "step": 1.0,
        "register": 0x0502,  # MBF_PAR_HIDRO
        "key": "MBF_PAR_HIDRO",
        "scale": 10.0,
        "device_class": None,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:air-humidifier",
    },
    {
        "name": "pH Max Limit",
        "unit": "pH",
        "min": 5.0,
        "max": 9.0,
        "step": 0.1,
        "register": 0x0504,  # MBF_PAR_PH1
        "key": "MBF_PAR_PH1",
        "scale": 100.0,
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
        # "icon": "mdi:ph"
    },
    {
        "name": "pH Min Limit",
        "unit": "pH",
        "min": 5.0,
        "max": 9.0,
        "step": 0.1,
        "register": 0x0505,  # MBF_PAR_PH2
        "key": "MBF_PAR_PH2",
        "scale": 100.0,
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
        # "icon": "mdi:ph",
    },
    {
        "name": "Redox Setpoint",
        "unit": "mV",
        "min": 0.0,
        "max": 1000.0,
        "step": 10.0,
        "register": 0x0508,  # MBF_PAR_RX1
        "key": "MBF_PAR_RX1",
        "scale": 1.0,
        "device_class": NumberDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:gradient-vertical"
    },
    {
        "name": "Chlorine Setpoint",
        "unit": "ppm",
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
        "register": 0x050A,  # MBF_PAR_CL1
        "key": "MBF_PAR_CL1",
        "scale": 100.0,
        "device_class": None,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:test-tube"
    },
    {
        "name": "Temperature Setpoint",
        "unit": "°C",
        "min": 10.0,
        "max": 40.0,
        "step": 1.0,
        "register": 0x0416,  # MBF_PAR_HEATING_TEMP
        "key": "MBF_PAR_HEATING_TEMP",
        "scale": 1.0,
        "device_class": NumberDeviceClass.TEMPERATURE,
        "entity_category": EntityCategory.CONFIG,
    },
]

BUTTON_DEFINITIONS = {
    "SYNC_TIME": {
        "name": "Synchronize Device Time",
        "icon": "mdi:clock-check-outline",
        "entity_category": EntityCategory.CONFIG,
    },
}

SELECT_DEFINITIONS = {
    "MBF_PAR_FILT_MODE": {
        "name": "Filtration Mode",
        "icon": "mdi:water-sync",
        "options_map": {
            0: "manual",
            1: "auto",
            2: "heating",
            3: "smart",
            4: "intelligent",
            13: "backwash",
        },
        "register": 0x0411,  # FILTRATION_MODE_REGISTER
    },
}

SWITCH_DEFINITIONS = {
    "MBF_PAR_FILT_MANUAL_STATE": {
        "name": "Manual Filtration",
        "icon": "mdi:pump",
        "entity_category": None,
        "switch_type": "manual_filtration",
    },
    # "AUX1": {
    #     "name": "Auxiliary Relay 1",
    #     "icon": "mdi:power-socket-eu",
    #     "switch_type": "aux",
    #     "relay_index": 1,
    #     "option": "use_aux1",
    # },
    # "AUX2": {
    #     "name": "Auxiliary Relay 2",
    #     "icon": "mdi:power-socket-eu",
    #     "switch_type": "aux",
    #     "relay_index": 2,
    #     "option": "use_aux2",
    # },
    # "AUX3": {
    #     "name": "Auxiliary Relay 3",
    #     "icon": "mdi:power-socket-eu",
    #     "switch_type": "aux",
    #     "relay_index": 3,
    #     "option": "use_aux3",
    # },
    # "AUX4": {
    #     "name": "Auxiliary Relay 4",
    #     "icon": "mdi:power-socket-eu",
    #     "switch_type": "aux",
    #     "relay_index": 4,
    #     "option": "use_aux4",
    # },
}