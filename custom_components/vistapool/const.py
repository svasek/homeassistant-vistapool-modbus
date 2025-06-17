import json
import logging
from pathlib import Path
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.number import NumberDeviceClass

"""
Load the manifest file
This file contains metadata about the integration such as name, version, domain, etc.
The manifest file is loaded to get the integration name and version
The integration name and version are used to identify the integration
and to display information about the integration in Home Assistant
"""
PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "button", "select"]

manifest_path = Path(__file__).parent / "manifest.json"
with open(manifest_path, encoding="utf-8") as f:
    MANIFEST = json.load(f)

INTEGRATION_NAME = MANIFEST.get("name")
INTEGRATION_VERSION = MANIFEST.get("version")

DOMAIN = (
    MANIFEST.get("domain").lower().replace("-", "_").replace(" ", "_").replace(".", "_")
    or "vistapool"
)
NAME = MANIFEST.get("name") or "VistaPool Integration"
VERSION = MANIFEST.get("version") or None

LOGGER = logging.getLogger(__name__)

DEFAULT_TIMER_RESOLUTION = 15  # in minutes
DEFAULT_SCAN_INTERVAL = 30  # in seconds
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

PERIOD_MAP = {
    "1_day": 86400,
    "2_days": 2 * 86400,
    "3_days": 3 * 86400,
    "4_days": 4 * 86400,
    "5_days": 5 * 86400,
    "1_week": 7 * 86400,
    "2_weeks": 14 * 86400,
    "3_weeks": 21 * 86400,
    "4_weeks": 28 * 86400,
}


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
        "icon": "mdi:water-sync",
    },
    "MBF_PH_STATUS_ALARM": {
        "name": "pH Alarm",
        "unit": None,
        "device_class": SensorDeviceClass.ENUM,
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
    "FILTRATION_SPEED": {
        "name": "Filtration Current Speed",
        "unit": None,
        "device_class": SensorDeviceClass.ENUM,
        "state_class": None,
        "icon": "mdi:fan",
    },
}

BINARY_SENSOR_DEFINITIONS = {
    "Device Time Out Of Sync": {
        "name": "Device Time Out Of Sync",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:clock-alert",
        "icon_off": "mdi:clock-check-outline",
    },
    # Relay states
    "pH Acid Pump": {
        "name": "pH Regulating",
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
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
        "option": "use_light",
    },
    "AUX1": {
        "name": "Auxiliary Relay 1",
        "device_class": BinarySensorDeviceClass.POWER,
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "option": "use_aux1",
    },
    "AUX2": {
        "name": "Auxiliary Relay 2",
        "device_class": BinarySensorDeviceClass.POWER,
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "option": "use_aux2",
    },
    "AUX3": {
        "name": "Auxiliary Relay 3",
        "device_class": BinarySensorDeviceClass.POWER,
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "option": "use_aux3",
    },
    "AUX4": {
        "name": "Auxiliary Relay 4",
        "device_class": BinarySensorDeviceClass.POWER,
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "option": "use_aux4",
    },
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
    },
    "pH pump active": {
        "name": "pH Base Pump",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "entity_category": EntityCategory.DIAGNOSTIC,
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
}

NUMBER_DEFINITIONS = {
    "MBF_PAR_HIDRO": {
        "name": "Hydrolisis target production level",
        "unit": "%",
        "min": 0.0,
        "max": 100.0,
        "step": 1.0,
        "register": 0x0502,  # MBF_PAR_HIDRO
        "scale": 10.0,
        "device_class": None,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:air-humidifier",
    },
    "MBF_PAR_PH1": {
        "name": "pH Max Limit",
        "unit": "pH",
        "min": 5.0,
        "max": 9.0,
        "step": 0.1,
        "register": 0x0504,  # MBF_PAR_PH1
        "scale": 100.0,
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
    },
    "MBF_PAR_PH2": {
        "name": "pH Min Limit",
        "unit": "pH",
        "min": 5.0,
        "max": 9.0,
        "step": 0.1,
        "register": 0x0505,  # MBF_PAR_PH2
        "scale": 100.0,
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
    },
    "MBF_PAR_RX1": {
        "name": "Redox Setpoint",
        "unit": "mV",
        "min": 0.0,
        "max": 1000.0,
        "step": 10.0,
        "register": 0x0508,  # MBF_PAR_RX1
        "scale": 1.0,
        "device_class": NumberDeviceClass.VOLTAGE,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:gradient-vertical",
    },
    "MBF_PAR_CL1": {
        "name": "Chlorine Setpoint",
        "unit": "ppm",
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
        "register": 0x050A,  # MBF_PAR_CL1
        "scale": 100.0,
        "device_class": None,
        "entity_category": EntityCategory.CONFIG,
        "icon": "mdi:test-tube",
    },
    "MBF_PAR_HEATING_TEMP": {
        "name": "Temperature Setpoint",
        "unit": "°C",
        "min": 10.0,
        "max": 40.0,
        "step": 1.0,
        "register": 0x0416,  # MBF_PAR_HEATING_TEMP
        "scale": 1.0,
        "device_class": NumberDeviceClass.TEMPERATURE,
        "entity_category": EntityCategory.CONFIG,
    },
}

BUTTON_DEFINITIONS = {
    "SYNC_TIME": {
        "name": "Synchronize Device Time",
        "icon": "mdi:clock-check-outline",
        "entity_category": EntityCategory.CONFIG,
    },
    "MBF_ESCAPE": {
        "name": "Clear Errors",
        "icon": "mdi:reload-alert",
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
            # 13: "backwash",
        },
        "register": 0x0411,  # FILTRATION_MODE_REGISTER
    },
    "MBF_PAR_FILTRATION_SPEED": {
        "name": "Filtration Speed",
        "icon": "mdi:fan-speed-3",
        "options_map": {0: "low", 1: "mid", 2: "high"},
        "register": 0x050F,
        "mask": 0x0070,
        "shift": 4,
    },
    "MBF_CELL_BOOST": {
        "name": "Boost Mode",
        "icon": "mdi:flash-outline",
        "options_map": {
            0: "inactive",
            1: "active",
            2: "active_redox",
        },
        "register": 0x020C,
    },
    "filtration1_start": {
        "name": "Filtration Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "filtration1_stop": {
        "name": "Filtration Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "filtration2_start": {
        "name": "Filtration Timer 2 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "filtration2_stop": {
        "name": "Filtration Timer 2 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "filtration3_start": {
        "name": "Filtration Timer 3 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "filtration3_stop": {
        "name": "Filtration Timer 3 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
    },
    "relay_aux1_start": {
        "name": "Relay AUX1 Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux1_stop": {
        "name": "Relay AUX1 Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux1_period": {
        "name": "Relay AUX1 Timer 1 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux1b_start": {
        "name": "Relay AUX1 Timer 2 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux1b_stop": {
        "name": "Relay AUX1 Timer 2 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux1b_period": {
        "name": "Relay AUX1 Timer 2 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux1",
    },
    "relay_aux2_start": {
        "name": "Relay AUX2 Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux2_stop": {
        "name": "Relay AUX2 Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux2_period": {
        "name": "Relay AUX2 Timer 1 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux2b_start": {
        "name": "Relay AUX2 Timer 2 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux2b_stop": {
        "name": "Relay AUX2 Timer 2 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux2b_period": {
        "name": "Relay AUX2 Timer 2 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux2",
    },
    "relay_aux3_start": {
        "name": "Relay AUX3 Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux3_stop": {
        "name": "Relay AUX3 Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux3_period": {
        "name": "Relay AUX3 Timer 1 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux3b_start": {
        "name": "Relay AUX3 Timer 2 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux3b_stop": {
        "name": "Relay AUX3 Timer 2 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux3b_period": {
        "name": "Relay AUX3 Timer 2 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux3",
    },
    "relay_aux4_start": {
        "name": "Relay AUX4 Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux4",
    },
    "relay_aux4_stop": {
        "name": "Relay AUX4 Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux4",
    },
    "relay_aux4_period": {
        "name": "Relay AUX4 Timer 1 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux4",
    },
    "relay_aux4b_start": {
        "name": "Relay AUX4 Timer 2 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux4",
    },
    "relay_aux4b_stop": {
        "name": "Relay AUX4 Timer 2 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_aux4",
    },
    "relay_aux4b_period": {
        "name": "Relay AUX4 Timer 2 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_aux4",
    },
    "relay_light_start": {
        "name": "Relay Light Timer 1 Start",
        "icon": "mdi:clock-start",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_light",
    },
    "relay_light_stop": {
        "name": "Relay Light Timer 1 Stop",
        "icon": "mdi:clock-end",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_time",
        "register": None,
        "option": "use_light",
    },
    "relay_light_period": {
        "name": "Relay Light Timer 1 Repeat",
        "icon": "mdi:repeat-variant",
        "entity_category": EntityCategory.CONFIG,
        "select_type": "timer_period",
        "register": None,
        "option": "use_light",
    },
    "relay_aux1_mode": {
        "name": "AUX1 Mode",
        "icon": "mdi:speedometer-medium",
        "options_map": {
            # 0: "disabled",
            1: "auto",
            # 2: "auto_linked",
            3: "on",
            4: "off",
        },
        "register": 0x04AC,
        "register_offset": 0,
        "select_type": "relay_mode",
        "option": "use_aux1",
    },
    "relay_aux2_mode": {
        "name": "AUX2 Mode",
        "icon": "mdi:speedometer-medium",
        "options_map": {
            # 0: "disabled",
            1: "auto",
            # 2: "auto_linked",
            3: "on",
            4: "off",
        },
        "register": 0x04BB,
        "register_offset": 0,
        "select_type": "relay_mode",
        "option": "use_aux2",
    },
    "relay_aux3_mode": {
        "name": "AUX3 Mode",
        "icon": "mdi:speedometer-medium",
        "options_map": {
            # 0: "disabled",
            1: "auto",
            # 2: "auto_linked",
            3: "on",
            4: "off",
        },
        "register": 0x04CA,
        "register_offset": 0,
        "select_type": "relay_mode",
        "option": "use_aux3",
    },
    "relay_aux4_mode": {
        "name": "AUX4 Mode",
        "icon": "mdi:speedometer-medium",
        "options_map": {
            # 0: "disabled",
            1: "auto",
            # 2: "auto_linked",
            3: "on",
            4: "off",
        },
        "register": 0x04D9,
        "register_offset": 0,
        "select_type": "relay_mode",
        "option": "use_aux4",
    },
    "relay_light_mode": {
        "name": "Light Mode",
        "icon": "mdi:speedometer-medium",
        "options_map": {
            # 0: "disabled",
            1: "auto",
            # 2: "auto_linked",
            3: "on",
            4: "off",
        },
        "register": 0x0470,
        "register_offset": 0,
        "select_type": "relay_mode",
        "option": "use_light",
    },
}

SWITCH_DEFINITIONS = {
    "TIME_AUTO_SYNC": {
        "name": "Automatic Time Sync",
        "icon": "mdi:home-clock-outline",
        "entity_category": EntityCategory.CONFIG,
        "switch_type": "auto_time_sync",
    },
    "MBF_PAR_FILT_MANUAL_STATE": {
        "name": "Manual Filtration",
        "icon": "mdi:pump",
        "entity_category": None,
        "switch_type": "manual_filtration",
    },
    "light": {
        "name": "Pool Light",
        "icon_on": "mdi:lightbulb-on",
        "icon_off": "mdi:lightbulb-off",
        "switch_type": "relay_timer",
        "timer_block_addr": 0x0470,
        "function_addr": 0x047B,
        "function_code": 2,  # LIGHTING
        "option": "use_light",
    },
    "aux1": {
        "name": "Auxiliary Relay 1",
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "switch_type": "relay_timer",
        "timer_block_addr": 0x04AC,
        "function_addr": 0x04B7,
        "function_code": 0x0800,  # AUX1 relay code
        "option": "use_aux1",
    },
    "aux2": {
        "name": "Auxiliary Relay 2",
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "switch_type": "relay_timer",
        "timer_block_addr": 0x04BB,
        "function_addr": 0x04C6,
        "function_code": 0x1000,  # AUX2 relay code
        "option": "use_aux2",
    },
    "aux3": {
        "name": "Auxiliary Relay 3",
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "switch_type": "relay_timer",
        "timer_block_addr": 0x04CA,
        "function_addr": 0x04D5,
        "function_code": 0x2000,  # AUX3 relay code
        "option": "use_aux3",
    },
    "aux4": {
        "name": "Auxiliary Relay 4",
        "icon_on": "mdi:electric-switch-closed",
        "icon_off": "mdi:electric-switch",
        "switch_type": "relay_timer",
        "timer_block_addr": 0x04D9,
        "function_addr": 0x04E4,
        "function_code": 0x4000,  # AUX4 relay code
        "option": "use_aux4",
    },
}
