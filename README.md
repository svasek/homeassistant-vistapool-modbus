# VistaPool Modbus Integration for Home Assistant

Custom integration to connect VistaPool/Sugar Valley pool controllers and salt chlorinators to Home Assistant via Modbus TCP.

**Supported brands:**  
Hidrolife • Aquascenic • Oxilife • Bionet • Hidroniser • UVScenic • Station • Brilix (Albixon) • Bayrol • Hay

---

## Hardware Connection

- **Gateway:** Any modbus TCP gateway (I use [USR-DR164](https://www.pusr.com/products/Serial-to-Dual-Band-WiFi-Converter.html) for example)
- **Connector:** Use standard **2.54mm** 5-Pin PCB female connector
- **Settings:** 19200 Baud, 1 Stop bit, No parity
- **Protocol:** Modbus RTU

### Plug connector

- **RS485 port**: Use the WIFI or EXTERNAL connector (not DISPLAY, unless LCD is disconnected).
- **Pins** (top to bottom):
    ```
         ___
      1 |*  |- +12V (from internal power supply)
      2 |*  |- NC (not connected)
      3 |*  |- Modbus A+
      4 |*  |- Modbus B-
      5 |*__|- Modbus GND
    ```
- **Settings**: 19200 Baud, 1 Stop bit, No parity
- **Protocol**: Modbus RTU


The NeoPool device acts as a Modbus **server** (formerly known as a *slave*), while this integration functions as a Modbus **client** (formerly known as a *master*).  
Only **one** Modbus client can be connected to a Modbus connector of the same name. It is not possible to operate multiple clients on connectors that share the same name.

Modbus connectors with **different labels** represent completely independent physical Modbus interfaces. Data traffic on one connector is **not visible** on the others.

There is one exception: the **DISPLAY** connector, which is present **twice** and is typically occupied by the built-in LCD.  
Since only one Modbus client can communicate with a Modbus server at a time, the DISPLAY connector is **not suitable** for this integration if the built-in LCD is connected to either of the two DISPLAY ports.

---

## Features

- **Multi-hub**: Add multiple VistaPool devices to HA, each with a custom name (used as prefix in entity IDs).
- **Sensors**: pH, Redox (ORP), Salt, Conductivity, Water Temperature, Ionization, Hydrolysis Intensity/Voltage, Device Time, Status/Alarm bits, Filtration speed
- **Numbers**: Setpoints for pH, Redox, Chlorine, Temperature, Hydrolysis production
- **Switches**: Manual filtration, Auxiliary relays (AUX1–AUX4, enable in options)
- **Select**: Filtration mode (Manual, Auto, Heating, Smart, Intelligent, Backwash; Backwash can only be activated at the device)
- **Buttons**: Sync device time to HA time

---

## Installation

### HACS (recommended)
1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS.
2. Install “VistaPool Integration”.
3. Restart Home Assistant.

### Manual
1. Download or clone this repository.
2. Copy the `custom_components/vistapool` folder to `/config/custom_components`.
3. Restart Home Assistant.

---

## Configuration

1. In HA, go to **Settings → Devices & Services → Add Integration → VistaPool**.
2. Enter connection details:
    - **Name**: Custom identifier for your pool (used in entity IDs, e.g. `pool_west`)
    - **Host**: IP address of your Modbus TCP gateway
    - **Port**: (default: 8899)
    - **Slave ID**: (default: 1)
    - **Scan interval**: (default: 30s)

### Options (after setup)

- **Adjust scan interval**
- ~~Enable/disable AUX relays 1–4~~

---

## Example Entities

Entities are prefixed by the custom name (e.g. `sensor.bazen_jih_par_filt_mode`):

- **Sensors**: `sensor.<name>_measure_ph`, `sensor.<name>_device_time`
- **Numbers**: `number.<name>_par_heating_temp`
- **Switches**: `switch.<name>_aux1`, `switch.<name>_mbf_par_filt_manual_state`
- **Select**: `select.<name>_mbf_par_filt_mode`
- **Buttons**: `button.<name>_sync_time`

---

## Special Notes

- **Filtration mode "Backwash"**: Can only be enabled via device display, not via HA.
- **Multi-hub**: Each device uses its unique name as prefix in all entity_ids.
- **Time sync**: Use the Sync Time button to set device RTC to Home Assistant time.

---

## To Do

- Add even more sensor coverage (flow, error states, power info)
- Add timers as settings option
- Add relays controlls

---

## Based On

- [Tasmota Neopool XSNS_83 driver](https://github.com/arendst/Tasmota/blob/master/tasmota/tasmota_xsns_sensor/xsns_83_neopool.ino)

---

## License

Apache License version 2.0
