"""
Mask decoders for VistaPool / NeoPool integration, based on xsns_83_neopool.ino

WARNING: DO NOT change names of this keys, they are used in the code !!!
"""


def decode_notification_mask(value: int) -> dict:
    if value is None:
        return {}
    return {
        "NOTIF_IO": bool(value & 0x0001),
        "NOTIF_MEAS": bool(value & 0x0002),
        "NOTIF_STATUS": bool(value & 0x0004),
        "NOTIF_CONF": bool(value & 0x0008),
        "NOTIF_WARN": bool(value & 0x0010),
        "NOTIF_INFO": bool(value & 0x0020),
        "NOTIF_DATE": bool(value & 0x0040),
        "NOTIF_PAGE": bool(value & 0x0080),
    }


"""
TODO: Check against GPIO configuration
    MBF_PAR_LIGHTING_GPIO for relay number assigned to the lighting function (0: inactive).
    MBF_PAR_FILT_GPIO for relay number assigned to the filtration function (0: inactive).    
    MBF_PAR_PH_ACID_RELAY_GPIO for relay number assigned to the acid pump (0: inactive).
    MBF_PAR_HEATING_GPIO for relay number assigned to the heating function (0: inactive).
    MBF_PAR_UV_RELAY_GPIO for relay number assigned to the UV lamp (0: inactive).
    
    There should be also name for each relay available in the settings.
    Each relay name has 5 register ASCIIZ string with up to 10 characters.
    (MBF_PAR_UICFG_MACH_NAME_AUX1, MBF_PAR_UICFG_MACH_NAME_AUX2, MBF_PAR_UICFG_MACH_NAME_AUX3, MBF_PAR_UICFG_MACH_NAME_AUX4)
"""


def decode_relay_state(value: int) -> dict:
    """Decode the relay state bits."""
    # Relay state bits are 16 bits, where each bit represents a relay state
    # Bit 0: pH Acid Pump
    # Bit 1: Filtration Pump
    # Bit 2: Pool Light
    # Bit 3: AUX1
    # Bit 4: AUX2
    # Bit 5: AUX3
    # Bit 6: AUX4
    # Bit 8: Filtration low speed
    # Bit 9: Filtration mid speed
    # Bit 10: Filtration high speed
    # Bits 8-10: Filtration current speed (0: off, 1: low, 2: mid, 3: high)
    if value is None:
        return {}
    return {
        "pH Acid Pump": bool(value & 0x0001),
        "Filtration Pump": bool(value & 0x0002),
        "Pool Light": bool(value & 0x0004),
        "AUX1": bool(value & 0x0008),
        "AUX2": bool(value & 0x0010),
        "AUX3": bool(value & 0x0020),
        "AUX4": bool(value & 0x0040),
        "Filtration low speed": bool(value & 0x0100),
        "Filtration mid speed": bool(value & 0x0200),
        "Filtration high speed": bool(value & 0x0400),
        "Filtration current speed": (value & 0x0700) >> 8,
    }


def decode_ph_rx_cl_cd_status_bits(status: int, unit: str) -> dict:
    """Decode the status bits for pH, Redox, Chlorine, and Conductivity sensors."""
    # Status bits are 16 bits, where each bit represents a status flag
    # Bit 0: Flow sensor problem
    # Bit 10: Module control status
    # Bit 11: Acid pump active
    # Bit 12: Pump active
    # Bit 13: Control module
    # Bit 14: Measurement active
    # Bit 15: Measurement module detected
    if status is None:
        return {}
    return {
        f"{unit} flow sensor problem": bool(status & 0x0008),
        f"{unit} module control status": bool(status & 0x0400),
        f"{unit} acid pump active": bool(status & 0x0800),
        f"{unit} pump active": bool(status & 0x1000),
        f"{unit} control module": bool(status & 0x2000),
        f"{unit} measurement active": bool(status & 0x4000),
        f"{unit} measurement module detected": bool(status & 0x8000),
    }


def decode_ion_status_bits(status: int) -> dict:
    """Decode the status bits for ION sensor."""
    # Status bits are 16 bits, where each bit represents a status flag
    # Bit 0: ION On Target
    # Bit 1: ION Low Flow
    # Bit 2: ION Reserved
    # Bit 3: ION Program time exceeded
    # Bit 12: ION in dead time
    # Bit 13: ION in Pol1
    # Bit 14: ION in Pol2
    # Bit 15: ION measurement module detected
    # Note: ION measurement module is always detected if ION sensor is present
    if status is None:
        return {}
    return {
        "ION On Target": bool(status & 0x0001),
        "ION Low Flow": bool(status & 0x0002),
        "ION Reserved": bool(status & 0x0004),
        "ION Program time exceeded": bool(status & 0x0008),
        "ION in dead time": bool(status & 0x1000),
        "ION in Pol1": bool(status & 0x2000),
        "ION in Pol2": bool(status & 0x4000),
    }


def decode_hidro_status_bits(status: int) -> dict:
    """Decode the status bits for HIDRO sensor."""
    # Status bits are 16 bits, where each bit represents a status flag
    # Bit 0: HIDRO On Target
    # Bit 1: HIDRO Low Flow
    # Bit 2: HIDRO Reserved
    # Bit 3: HIDRO Cell Flow FL1 (if present)
    # Bit 4: HIDRO Cover input active
    # Bit 5: HIDRO Module active
    # Bit 6: HIDRO Module regulated
    # Bit 7: HIDRO Activated by the RX module
    # Bit 8: HIDRO Chlorine shock mode
    # Bit 9: HIDRO Chlorine flow indicator FL2 (if present)
    # Bit 10: HIDRO Activated by the CL module
    # Bit 12: HIDRO in dead time
    # Bit 13: HIDRO in Pol1
    # Bit 14: HIDRO in Pol2
    # Bit 15: HIDRO measurement module detected
    # Note: HIDRO measurement module is always detected if HIDRO sensor is present
    if status is None:
        return {}
    return {
        "HIDRO On Target": bool(status & 0x0001),
        "HIDRO Low Flow": bool(status & 0x0002),
        "HIDRO Reserved": bool(status & 0x0004),
        "HIDRO Cell Flow FL1": bool(status & 0x0008),  # if present
        "HIDRO Cover input active": bool(status & 0x0010),
        "HIDRO Module active": bool(status & 0x0020),
        "HIDRO Module regulated": bool(status & 0x0040),
        "HIDRO Activated by the RX module": bool(status & 0x0080),
        "HIDRO Chlorine shock mode": bool(status & 0x0100),
        "HIDRO Chlorine flow indicator FL2": bool(status & 0x0200),  # if present
        "HIDRO Activated by the CL module": bool(status & 0x0400),
        "HIDRO in dead time": bool(status & 0x1000),
        "HIDRO in Pol1": bool(status & 0x2000),
        "HIDRO in Pol2": bool(status & 0x4000),
    }
