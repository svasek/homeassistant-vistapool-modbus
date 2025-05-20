import logging
import asyncio
from pymodbus.client import AsyncModbusTcpClient

from .status_mask import (
    decode_notification_mask,
    decode_relay_state,
    decode_ph_rx_cl_cd_status_bits,
    decode_ion_status_bits,
    decode_hidro_status_bits,
)

_LOGGER = logging.getLogger(__name__)

AUX_BITMASKS = {
    1: 0x0008,  # AUX1
    2: 0x0010,  # AUX2
    3: 0x0020,  # AUX3
    4: 0x0040,  # AUX4
}

class VistaPoolModbusClient:
    def __init__(self, config):
        self._host = config["host"]
        self._port = config.get("port", 8899)
        self._unit = config.get("slave", 1)

    async def async_read_all(self):
        result = {}

        '''WARNING: Device limit for reading registers is 31 at one request !!!'''
        
        def get_safe(regs, idx):
            try:
                return regs[idx]
            except IndexError:
                _LOGGER.warning(f"Register at index {idx} is missing in {regs}")
                return None
        

            
        try:
            async with AsyncModbusTcpClient(self._host, port=self._port) as client:
                if not client.connected:
                    _LOGGER.error("Modbus client connection failed to %s:%s", self._host, self._port)
                    return {}

                '''
                Request MODBUS page of registers starting from 0x0000
                Manages general configuration of the box. This page is reserved for internal purposes
                '''
                try:
                    rr00_count = 15
                    rr00 = await client.read_holding_registers(address=0x0000, count=rr00_count, slave=self._unit)
                except Exception as e:
                    _LOGGER.error("Read error 0x0000: %s", e)
                    return {}
                if rr00.isError():
                    _LOGGER.error("Modbus read error from 0x0000: %s", rr00)
                else:
                    reg00 = rr00.registers
                    _LOGGER.debug("Raw rr00: %s", reg00)
                    if len(reg00) < rr00_count:
                        _LOGGER.warning("Expected at least %d registers from 0x0300, got %d", rr00_count, len(reg00))
                        return result
                    # Example: [1, 3, 1280, 32768, 88, 47, 16707, 20497, 8248, 12592, 0, 0, 0, 22069, 0]
                    result.update({
                        "MBF_POWER_MODULE_VERSION": get_safe(reg00, 2),		# 0x0002         ! Power module version (MSB=Major, LSB=Minor)
                        "MBF_POWER_MODULE_NODEID": reg00[4:10],             # 0x0004         ! Power module Node ID (6 register 0x0004 - 0x0009)
                        "MBF_POWER_MODULE_REGISTER": get_safe(reg00, 11),   # 0x000C         ! Writing an address in this register causes the power module register address to be read out into MBF_POWER_MODULE_DATA, see MBF_POWER_MODULE_REG_*
                        "MBF_POWER_MODULE_DATA": get_safe(reg00, 12),		# 0x000D         ! power module data as requested in MBF_POWER_MODULE_REGISTER
                        "MBF_PH_STATUS_ALARM": get_safe(reg00, 14), 		# 0x000F           PH alarm. The possible alarm values are depending on the regulation model
                        # Prepared for future use:
                        # "MBF_VOLT_24_36": get_safe(reg00, 0),		        # 0x0022*        ! Current 24-36V line in mV
                        # "MBF_VOLT_12": get_safe(reg00, 0),		        # 0x0023*        ! Current 12V line in mV
                        # "MBF_VOLT_5": get_safe(reg00, 0),		            # 0x006A*        ! 5V line in mV / 0,62069
                        # "MBF_AMP_4_20_MICRO": get_safe(reg00, 0),		    # 0x0072*        ! 2-40mA line in µA * 10 (1=0,01mA)
                    })
                    
                
                '''
                Request MEASURE page of registers starting from 0x0100
                Contains the different measurement information including hydrolysis current, pH level, redox level, etc.
                For measurements registers, we have to use function 0x04 (Read Input Registers).
                '''
                try:
                    rr01_count = 18
                    rr01 = await client.read_input_registers(address=0x0100, count=rr01_count, slave=self._unit)
                except Exception as e:
                    _LOGGER.error("Read error 0x0100: %s", e)
                    return {}
                if rr01.isError():
                    _LOGGER.error("Modbus read error from 0x0100: %s", rr01)
                else:
                    reg01 = rr01.registers
                    _LOGGER.debug("Raw rr01: %s", reg01)
                    if len(reg01) < rr01_count:
                        _LOGGER.warning("Expected at least %d registers from 0x0100, got %d", rr01_count, len(reg01))
                        return result
                    # Example: [0, 0, 820, 709, 0, 0, 140, 50560, 49536, 1280, 1280, 0, 8192, 16928, 0, 0, 9, 0]
                    result.update({
                        "MBF_ION_CURRENT": get_safe(reg01, 0),                # 0x0100        Ionization level measured
                        "MBF_HIDRO_CURRENT": get_safe(reg01, 1) / 10.0,       # 0x0101        Hydrolysis intensity level
                        "MBF_MEASURE_PH": get_safe(reg01, 2) / 100.0,         # 0x0102 ph     pH level measured in 1/100 (700 = 7.00)
                        "MBF_MEASURE_RX": get_safe(reg01, 3),                 # 0x0103 mV     Redox level measured in mV
                        "MBF_MEASURE_CL": get_safe(reg01, 4) / 100.0,         # 0x0104 ppm    Chlorine level measured in 1/100 ppm (100 = 1.00 ppm)
                        "MBF_MEASURE_CONDUCTIVITY": get_safe(reg01, 5),       # 0x0105 %      Conductivity level measured in %
                        "MBF_MEASURE_TEMPERATURE": get_safe(reg01, 6) / 10.0, # 0x0106 °C     Temperature sensor measured in 1/10° C (100 = 10.0°C)
                        "MBF_PH_STATUS": get_safe(reg01, 7),                  # 0x0107 mask   Status of the pH-module
                        "MBF_RX_STATUS": get_safe(reg01, 8),                  # 0x0108 mask   Status of the Rx-module
                        "MBF_CL_STATUS": get_safe(reg01, 9),                  # 0x0109 mask   Status of the Chlorine-module
                        "MBF_CD_STATUS": get_safe(reg01, 10),                 # 0x010A mask   Status of the Conductivity-module
                        "MBF_ION_STATUS": get_safe(reg01, 12),                # 0x010C mask   Status of the Ionization-module
                        "MBF_HIDRO_STATUS": get_safe(reg01, 13),              # 0x010D mask   Status of the Hydrolysis-module
                        "MBF_RELAY_STATE": get_safe(reg01, 14),               # 0x010E mask   Status of each configurable relay
                        "MBF_HIDRO_SWITCH_VALUE": get_safe(reg01, 15),        # 0x010F        INTERNAL - contains the opening of the hydrolysis PWM.
                        "MBF_NOTIFICATION": get_safe(reg01, 16),              # 0x0110 mask   Bit field that informs whether a property page has changed since the last time it was queried. (see MBMSK_NOTIF_*). This register makes it possible to refresh the content of the registers maintained by a modbus master in an optimized way, without the need to reread all registers periodically, but only those on a page that has been changed.
                        "MBF_HIDRO_VOLTAGE": get_safe(reg01, 17),             # 0x0111        The voltage applied to the hydrolysis cell. This register, together with that of MBF_HIDRO_CURRENT allows extrapolation of water salinity.
                    })
                
                
                # After loading reg01, update result with all decodings:
                result.update({
                    **decode_ph_rx_cl_cd_status_bits(get_safe(reg01, 7), "pH"),
                    **decode_ph_rx_cl_cd_status_bits(get_safe(reg01, 8), "Redox"),
                    **decode_ph_rx_cl_cd_status_bits(get_safe(reg01, 9), "Chlorine"),
                    **decode_ph_rx_cl_cd_status_bits(get_safe(reg01, 10), "Conductivity"),
                    **decode_ion_status_bits(get_safe(reg01, 12)),
                    **decode_hidro_status_bits(get_safe(reg01, 13)),
                    **decode_relay_state(get_safe(reg01, 14)),
                    **decode_notification_mask(get_safe(reg01, 16)),
                })
                

                '''
                Request FACTORY page of registers starting from 0x0300
                Contains factory data such as calibration parameters for the different power units.
                For configuration registers, we have to use function 0x03 (Read Holding Registers)
                '''
                await asyncio.sleep(0.05)
                try:
                    rr03_count = 13
                    rr03 = await client.read_holding_registers(address=0x0300, count=rr03_count, slave=self._unit)
                except Exception as e:
                    _LOGGER.error("Read error 0x0300: %s", e)
                    return {}
                if rr03.isError():
                    _LOGGER.error("Modbus read error from 0x0300: %s", rr03)
                else:
                    reg03 = rr03.registers
                    _LOGGER.debug("Raw rr03: %s", reg03)
                    if len(reg03) < rr03_count:
                        _LOGGER.warning("Expected at least %d registers from 0x0300, got %d", rr03_count, len(reg03))
                        return result
                    # [2055, 10, 0, 0, 0, 0, 1000, 50, 0, 14687, 2600, 2, 1297]
                    result.update({
                        "MBF_PAR_VERSION": get_safe(reg03, 0),                # 0x0300*        Software version of the PowerBox
                        "MBF_PAR_MODEL": get_safe(reg03, 1),                  # 0x0301* mask   System model options
                        "MBF_PAR_SERNUM": get_safe(reg03, 2),                 # 0x0302*        Serial number of the PowerBox
                        "MBF_PAR_ION_NOM":  get_safe(reg03, 3),		          # 0x0303*        Ionization maximum production level (DO NOT WRITE!)
                        "MBF_PAR_HIDRO_NOM":  get_safe(reg03, 6) / 10.0,      # 0x0306*        Hydrolysis maximum production level. (DO NOT WRITE!) If the hydrolysis is set to work in percent mode, this value will be 100. If the hydrolysis module is set to work in g/h production, this module will contain the maximum amount of production in g/h units. (DO NOT WRITE!)
                        "MBF_PAR_SAL_AMPS":  get_safe(reg03, 10),	          # 0x030A         Current command in regulation for which we are going to measure voltage
                        "MBF_PAR_SAL_CELLK":  get_safe(reg03, 11),		      # 0x030B         Specifies the relationship between the resistance obtained in the measurement process and its equivalence in g / l (grams per liter)
                        "MBF_PAR_SAL_TCOMP":  get_safe(reg03, 12),		      # 0x030C         Specifies the deviation in temperature from the conductivity.
                    })

                '''
                Request INSTALLER page of registers starting from 0x0400 
                Contains a set of configuration registers related to the equipment installation,
                such as the relays used for each function, the amount of time that each pump must operate, etc.
                For configuration registers, we have to use function 0x03 (Read Holding Registers)
                '''
                
                # Read configuration registers (0x0408–0x04E0) in blocks of *31* due to device limits
                register_ranges = [
                    (0x0408, 31),  # 0x0408–0x0426
                    (0x0427, 3),  # 0x0427–0x0445
                    # Prepared for future use:
                    # (0x0446, 31),  # 0x0446–0x0464
                    # (0x0465, 31),  # 0x0465–0x0483
                    # (0x0484, 31),  # 0x0484–0x04A2
                    # (0x04A3, 31),  # 0x04A3–0x04C1
                    # (0x04C2, 31),  # 0x04C2–0x04E0
                ]
                
                reg04 = []
                for address, count in register_ranges:
                    await asyncio.sleep(0.05)
                    try:
                        rr04 = await client.read_holding_registers(address=address, count=count, slave=self._unit)
                    except Exception as e:
                        _LOGGER.error(f"Read error 0x{address:04X}: {e}")
                        return {}
                    if rr04.isError():
                        _LOGGER.error(f"Modbus read error from 0x{address:04X}: {rr04}")
                        return {}
                    reg04.extend(rr04.registers)
                    _LOGGER.debug(f"Raw rr04 from 0x{address:04X}: {rr04.registers}")
                
                # Example: [1, 0, 0, 0, 0, 1, 3, 1, 2, 0, 0, 0, 25, 0, 25, 10, 0, 0, 28, 480, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]    
                result.update({
                    "MBF_PAR_TIME_LOW": get_safe(reg04, 0),                    # 0x0408*        System timestamp as unix timestamp (32 bit value - low word).
                    "MBF_PAR_TIME_HIGH": get_safe(reg04, 1),                   # 0x0409*        System timestamp as unix timestamp (32 bit value - high word).
                    "MBF_PAR_PH_ACID_RELAY_GPIO": get_safe(reg04, 2),          # 0x040A*        Relay number assigned to the acid pump function (only with pH module).
                    "MBF_PAR_PH_BASE_RELAY_GPIO": get_safe(reg04, 3),          # 0x040B*        Relay number assigned to the base pump function (only with pH module).
                    "MBF_PAR_RX_RELAY_GPIO": get_safe(reg04, 4),               # 0x040C*        Relay number assigned to the Redox level regulation function. If the value is 0, there is no relay assigned, and therefore there is no pump function (ON / OFF should not be displayed)
                    "MBF_PAR_CL_RELAY_GPIO": get_safe(reg04, 5),               # 0x040D*        Relay number assigned to the chlorine pump function (only with free chlorine measuring modules).
                    "MBF_PAR_CD_RELAY_GPIO": get_safe(reg04, 6),               # 0x040E*        Relay number assigned to the conductivity (brine) pump function (only with conductivity measurement modules).
                    "MBF_PAR_TEMPERATURE_ACTIVE": get_safe(reg04, 7),          # 0x040F*        Indicates whether the equipment has a temperature measurement or not.
                    "MBF_PAR_LIGHTING_GPIO": get_safe(reg04, 8),               # 0x0410*        Relay number assigned to the lighting function. 0: inactive.
                    "MBF_PAR_FILT_MODE": get_safe(reg04, 9),                   # 0x0411*        Filtration mode (see MBV_PAR_FILT_*)
                    "MBF_PAR_FILT_GPIO": get_safe(reg04, 10),                  # 0x0412*        Relay selected to perform the filtering function (by default it is relay 2). When this value is at zero, there is no relay assigned and therefore it is understood that the equipment does not control the filtration. In this case, the filter option does not appear in the user menu.
                    "MBF_PAR_FILT_MANUAL_STATE": get_safe(reg04, 11),          # 0x0413         Filtration status in manual mode (on = 1; off = 0)
                    "MBF_PAR_HEATING_MODE": get_safe(reg04, 12),               # 0x0414         Heating mode: 0 = the equipment is not heated. 1 = the equipment is heating.
                    "MBF_PAR_HEATING_GPIO": get_safe(reg04, 13),               # 0x0415         Relay number assigned to perform the heating function (by default it is relay 7). When this value is at zero, there is no relay assigned and therefore it is understood that the equipment does not control the heating. In this case, the filter modes associated with heating will not be displayed.
                    "MBF_PAR_HEATING_TEMP": get_safe(reg04, 14),               # 0x0416         Heating mode: Heating setpoint temperature
                    "MBF_PAR_CLIMA_ONOFF": get_safe(reg04, 15),                # 0x0417         Activation of the climate mode (0 = inactive, 1 = active).
                    "MBF_PAR_SMART_TEMP_HIGH": get_safe(reg04, 16),            # 0x0418         Smart mode: Upper temperature
                    "MBF_PAR_SMART_TEMP_LOW": get_safe(reg04, 17),             # 0x0419         Smart mode: Lower temperature
                    "MBF_PAR_SMART_ANTI_FREEZE": get_safe(reg04, 18),          # 0x041A         Smart mode: Antifreeze mode activated (1) or not (0).
                    "MBF_PAR_SMART_INTERVAL_REDUCTION": get_safe(reg04, 19),   # 0x041B         Smart mode: This register is read-only and reports to the outside what percentage (0 to 100%) is being applied to the nominal filtration time. 100% means that the total programmed time is being filtered.
                    "MBF_PAR_INTELLIGENT_TEMP": get_safe(reg04, 20),           # 0x041C         Intelligent mode: Setpoint temperature
                    "MBF_PAR_INTELLIGENT_FILT_MIN_TIME": get_safe(reg04, 21),  # 0x041D         Intelligent mode: Minimum filtration time in minutes
                    "MBF_PAR_INTELLIGENT_BONUS_TIME": get_safe(reg04, 22),     # 0x041E         Intelligent mode: Bonus time for the current set of intervals
                    "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL": get_safe(reg04, 23), # 0x041F       Intelligent mode: Time to next filtration interval. When it reaches 0 an interval is started and the number of seconds is reloaded for the next interval (2x3600)
                    "MBF_PAR_INTELLIGENT_INTERVALS": get_safe(reg04, 24),      # 0x0420         Intelligent mode: Number of started intervals. When it reaches 12 it is reset to 0 and the bonus time is reloaded with the value of MBF_PAR_INTELLIGENT_FILT_MIN_TIME
                    "MBF_PAR_FILTRATION_STATE": get_safe(reg04, 25),           # 0x0421         Filtration state: 0 is off and 1 is on. The filtration state is regulated according to the MBF_PAR_FILT_MANUAL_STATE register if the filtration mode held in register MBF_PAR_FILT_MODE is set to FILT_MODE_MANUAL (0).
                    "MBF_PAR_HEATING_DELAY_TIME": get_safe(reg04, 26),         # 0x0422         Timer in seconds that counts up when the heating is to be enabled. Once this counter reaches 60 seconds, the heating is then enabled. This counter is for internal use only.
                    "MBF_PAR_FILTERING_TIME_LOW": get_safe(reg04, 27),         # 0x0423         Internal timer for the intelligent filtering mode (32-bit value - low word). It counts the filtering time done during a given day. This register is only for internal use and should not be modified by the user.
                    "MBF_PAR_FILTERING_TIME_HIGH": get_safe(reg04, 28),        # 0x0424         Internal timer for the intelligent filtering mode (32-bit value - high word)
                    "MBF_PAR_INTELLIGENT_INTERVAL_TIME_LOW": get_safe(reg04, 29), # 0x0425      Internal timer that counts the filtration interval assigned to the the intelligent mode (32-bit value - low word). This register is only for internal use and should not be modified by the user.
                    "MBF_PAR_INTELLIGENT_INTERVAL_TIME_HIGH": get_safe(reg04, 30), # 0x0426     Internal timer that counts the filtration interval assigned to the the intelligent mode (32-bit value - high word)
                    "MBF_PAR_UV_MODE": get_safe(reg04, 31),                    # 0x0427         UV mode active or not - see MBV_PAR_UV_MODE*. To enable UV support for a given device, add the mask MBMSK_MODEL_UV to the MBF_PAR_MODEL register.
                    "MBF_PAR_UV_HIDE_WARN": get_safe(reg04, 32),                # 0x0428  mask  Suppression for warning messages in the UV mode (see MBMSK_UV_HIDE_WARN_*)
                    "MBF_PAR_UV_RELAY_GPIO": get_safe(reg04, 33),               # 0x0429        Relay number assigned to the UV function.
                })
                
                ''' 
                Request INSTALLER page of registers starting from 0x0500
                Contains user configuration registers, such as the production level
                for the ionization and the hydrolysis, or the set points for the pH, redox, or chlorine regulation loops.
                For configuration registers, we have to use function 0x03 (Read Holding Registers)
                '''
                await asyncio.sleep(0.05)
                try:
                    rr05_count = 9
                    rr05 = await client.read_holding_registers(address=0x0502, count=rr05_count, slave=self._unit)
                except Exception as e:
                    _LOGGER.error("Read error 0x0504: %s", e)
                    return {}
                if rr05.isError():
                    _LOGGER.error("Modbus read error from 0x0504: %s", rr05)
                else:
                    reg05 = rr05.registers
                    _LOGGER.debug("Raw rr05: %s", reg05)
                    if len(reg05) < rr05_count:
                        _LOGGER.warning("Expected at least %d registers from 0x0504, got %d", rr05_count, len(reg05))
                        return result
                    # Example: [650, 0, 750, 700, 0, 0, 700, 0, 100]
                    result.update({
                        "MBF_PAR_HIDRO": get_safe(reg05, 0) / 10.0,       # 0x0502        Hydrolisis target production level. When the hydrolysis production is to be set in percent values, this value will contain the percent of production. If the hydrolysis module is set to work in g/h production, this module will contain the desired amount of production in g/h units. The value adjusted in this register must not exceed the value set in the MBF_PAR_HIDRO_NOM factory register.
                        "MBF_PAR_PH1": get_safe(reg05, 2) / 100.0,        # 0x0504        Higher limit of the pH regulation system. The value set in this register is multiplied by 100. This means that if we want to set a value of 7.5, the numerical content that we must write in this register is 750. This register must be always higher than MBF_PAR_PH2.
                        "MBF_PAR_PH2": get_safe(reg05, 3) / 100.0,        # 0x0505        Lower limit of the pH regulation system. The value set in this register is multiplied by 100. This means that if we want to set a value of 7.0, the numerical content that we must write in this register is 700. This register must be always lower than MBF_PAR_PH1.
                        "MBF_PAR_RX1": get_safe(reg05, 6),                # 0x0508        Set point for the redox regulation system. This value must be in the range of 0 to 1000.
                        "MBF_PAR_CL1": get_safe(reg05, 8) / 100.0,        # 0x050A        Set point for the chlorine regulation system. The value stored in this register is multiplied by 100. This mean that if we want to set a value of 1.5 ppm, we will have to write a numerical value of 150. This value stored in this register must be in the range of 0 to 1000.
                    })


                ''' 
                Request MISC page of registers starting from 0x0600
                Contains the configuration parameters for the screen controllers (language, colours, sound, etc).
                For configuration registers, we have to use function 0x03 (Read Holding Registers)
                '''
                await asyncio.sleep(0.05)
                try:
                    rr06_count = 13
                    rr06 = await client.read_holding_registers(address=0x0600, count=rr06_count, slave=self._unit)
                except Exception as e:
                    _LOGGER.error("Read error 0x0600: %s", e)
                    return {}
                if rr06.isError():
                    _LOGGER.error("Modbus read error from 0x0600: %s", rr05)
                else:
                    reg06 = rr06.registers
                    _LOGGER.debug("Raw rr06: %s", reg06)
                    if len(reg06) < rr06_count:
                        _LOGGER.warning("Expected at least %d registers from 0x0600, got %d", rr06_count, len(reg06))
                        return result
                    # Example: [9, 6, 25604, 5, 0, 2240, 545, 1281, 0, 0, 0, 0, 0, 0]
                    result.update({
                        "MBF_PAR_UICFG_MACHINE": get_safe(reg06, 0),                # 0x0600        Machine type (see MBV_PAR_MACH_* and  kNeoPoolMachineNames[])
                        "MBF_PAR_UICFG_LANGUAGE": get_safe(reg06, 1),               # 0x0601        Selected language (see MBV_PAR_LANG_*)
                        "MBF_PAR_UICFG_BACKLIGHT": get_safe(reg06, 2),              # 0x0602        Display backlight function (see MBV_PAR_BACKLIGHT_*)
                        "MBF_PAR_UICFG_SOUND": get_safe(reg06, 3),                  # 0x0603 mask   Audible alerts (see MBMSK_PAR_SOUND_*)
                        "MBF_PAR_UICFG_PASSWORD": get_safe(reg06, 4),               # 0x0604        System password encoded in BCD
                        "MBF_PAR_UICFG_VISUAL_OPTIONS": get_safe(reg06, 5),         # 0x0605 mask   Stores the different display options for the user interface menus (bitmask). Some bits allow you to hide options that are normally visible (bits 0 to 3) while other bits allow you to show options that are normally hidden (bits 9 to 15)
                        "MBF_PAR_UICFG_VISUAL_OPTIONS_EXT": get_safe(reg06, 6),     # 0x0606 mask   This register stores additional display options for the user interface menus (see MBMSK_VOE_*)
                        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": get_safe(reg06, 7),      # 0x0607 mask   This register is an expansion of register MBF_PAR_UICFG_MACHINE and MBF_PAR_UICFG_VISUAL_OPTIONS. If MBF_PAR_UICFG_MACHINE is MBV_PAR_MACH_GENERIC then the lower part (8 bits LSB) is used to store the type of color selected. Colors and styles correspond to those listed in MBF_PAR_UICFG_MACHINE (see MBV_PAR_MACH_*). The upper part (8-bit MSB) contains extra bits MBMSK_VS_FORCE_UNITS_GRH, MBMSK_VS_FORCE_UNITS_PERCENTAGE and MBMSK_ELECTROLISIS
                        "MBF_PAR_UICFG_MACH_NAME_BOLD": get_safe(reg06, 8),         # 0x0608         Machine name bold part title displayed during startup if MBF_PAR_UICFG_MACHINE is MBV_PAR_MACH_GENERIC. Note: Only lowercase letters (a-z) can be used. 4 register (0x608 to 0x60B) ASCIIZ string with up to 8 characters
                        "MBF_PAR_UICFG_MACH_NAME_LIGHT": get_safe(reg06, 12),       # 0x060C         Machine name normal intensity part title displayed during startup if MBF_PAR_UICFG_MACHINE is MBV_PAR_MACH_GENERIC. Note: Only lowercase letters (a-z) can be used. 4 register (0x060C to 0x060F) ASCIIZ string with up to 8 characters
                        # Prepared for future use:
                        # "MBF_PAR_UICFG_MACH_NAME_AUX1": modbus_regs_to_ascii(reg06[16:21]), # 0x0610         Aux1 relay name: 5 register ASCIIZ string with up to 10 characters
                        # "MBF_PAR_UICFG_MACH_NAME_AUX2": modbus_regs_to_ascii(reg06[21:26]), # 0x0615         Aux2 relay name: 5 register ASCIIZ string with up to 10 characters
                        # "MBF_PAR_UICFG_MACH_NAME_AUX3": modbus_regs_to_ascii(reg06[26:31]), # 0x061A         Aux3 relay name: 5 register ASCIIZ string with up to 10 characters
                        # "MBF_PAR_UICFG_MACH_NAME_AUX4": modbus_regs_to_ascii(reg06[31:36]), # 0x061F         Aux4 relay name: 5 register ASCIIZ string with up to 10 characters
                    })
                

        except Exception as e:
            _LOGGER.error("Modbus TCP read error: %s", e)
        # _LOGGER.debug("All Results: %s", result)
        return result

    async def async_write_register(self, address: int, value, apply: bool = False):
        """
        Write one or more Modbus registers using function 0x10 (Write Multiple Registers).

        If apply=True, the configuration is saved to EEPROM (0x02F0)
        and executed (0x02F5) after the write.
        """
        try:
            async with AsyncModbusTcpClient(self._host, port=self._port) as client:
                if not client.connected:
                    _LOGGER.error("Modbus client connection failed to %s:%s", self._host, self._port)
                    return

                # Ensure value is always a list, even for a single register
                if not isinstance(value, list):
                    value = [value]

                result = await client.write_registers(address=address, values=value, slave=self._unit)
                if result.isError():
                    _LOGGER.error("Write failed at 0x%04X: %s", address, result)
                    return
                _LOGGER.debug("Wrote register(s) at 0x%04X: %s", address, value)

                # Confirm the write
                await asyncio.sleep(0.05)
                # Read back the register to confirm the write
                confirm = await client.read_holding_registers(address=address, count=len(value), slave=self._unit)
                if confirm.isError():
                    _LOGGER.error("Read failed at 0x%04X: %s", address, confirm)
                    return
                
                # If apply is True, save the configuration to EEPROM and execute
                if apply:
                    await asyncio.sleep(0.1)
                    result = await client.write_registers(address=0x02F0, values=[1], slave=self._unit)
                    
                    if result.isError():
                        _LOGGER.error("EEPROM save failed (0x02F0): %s", result)
                        return
                    _LOGGER.debug("EEPROM save triggered (0x02F0)")

                    await asyncio.sleep(0.1)
                    result = await client.write_registers(address=0x02F5, values=[1], slave=self._unit)
                    if result.isError():
                        _LOGGER.error("EXEC failed (0x02F5): %s", result)
                        return
                    _LOGGER.debug("Config EXEC triggered (0x02F5)")
                    await asyncio.sleep(0.1)

        except Exception as e:
            _LOGGER.error("Modbus TCP write exception: %s", e)


    ''' Manual controller for AUX relays (1-4) '''
    async def async_write_aux_relay(self, relay_index, on):
        aux_bit = AUX_BITMASKS[relay_index]
        try:
            async with AsyncModbusTcpClient(self._host, port=self._port) as client:
                if not client.connected:
                    _LOGGER.error("Modbus client connection failed to %s:%s", self._host, self._port)
                    return
                # Read current relay state
                current_result = await client.read_input_registers(address=0x010E, count=1, slave=self._unit)
                if current_result.isError():
                    _LOGGER.error("Modbus read error from %s: %s", 0x010E, current_result)
                    return
                current = current_result.registers[0]
                # Set or clear the aux bit
                if on:
                    value = current | aux_bit
                else:
                    value = current & ~aux_bit
                await client.write_registers(address=0x0289, values=[1], slave=self._unit)
                # await client.write_registers(address=0x010E, values=[value], slave=self._unit)
                _LOGGER.debug("Wrote relay state at 0x010E: 0x%04X", value)
                await client.write_registers(address=0x0289, values=[0], slave=self._unit)
                await client.write_registers(address=0x02F5, values=[1], slave=self._unit)
        except Exception as e:
            _LOGGER.error("Modbus TCP AUX relay write exception: %s", e)

def modbus_regs_to_ascii(regs):
    """Convert list of uint16 Modbus registers to ASCII string (ASCIIZ, max 10 chars)."""
    chars = []
    for reg in regs:
        # High byte (1st char)
        high = (reg >> 8) & 0xFF
        # Low byte (2nd char)
        low = reg & 0xFF
        if high != 0:
            chars.append(chr(high))
        else:
            break
        if low != 0:
            chars.append(chr(low))
        else:
            break
    return ''.join(chars)

def modbus_regs_to_hex_string(regs):
    """Return Modbus registers as hex string, e.g. '0058 002F 4143 5011 0238 3130'."""
    if not regs or not isinstance(regs, list):
        return ""
    return " ".join(f"{reg:04X}" for reg in regs)