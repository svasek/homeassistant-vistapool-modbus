# VistaPool Modbus Integration for Home Assistant

[![Release](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/release.yml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/release.yml)
[![Validate with Hassfest](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/hassfest.yml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/validate-hacs.yaml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/validate-hacs.yaml)
[![CodeQL](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/github-code-scanning/codeql)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Custom integration for connecting Sugar Valley pool controllers and salt chlorinators to Home Assistant via Modbus TCP.

**Supported brands:**  
Hidrolife • Aquascenic • Oxilife • Bionet • Hidroniser • UVScenic • Station • Brilix (Albixon) • Bayrol • Hay • Hayward • Aquarite • Kripsol KLX • Certikin • Poolstar • GrupAquadirect • Pentair • ProducPool • Pool Technologie

---

## Hardware Connection

- **Gateway:** Any Modbus TCP gateway (e.g. [USR-DR164](https://www.pusr.com/products/Serial-to-Dual-Band-WiFi-Converter.html))
- **Connector:** Standard **2.54 mm** 5-pin PCB female connector
- **Settings:** 19200 baud, 1 stop bit, no parity
- **Protocol:** Modbus RTU
- **For more information, check out our [Modbus Connection Guide](docs/modbus-connection-guide.md)**, which includes images.

### Plug Connector

- **RS485 port**: Use the `WIFI` or `EXTERNAL` connector (do **not** use `DISPLAY`, unless the internal LCD is disconnected).
- **Pinout** (top to bottom):
  ```
       ___
    1 |*  |– +12V (from internal power supply)
    2 |*  |– NC (not connected)
    3 |*  |– Modbus A+
    4 |*  |– Modbus B-
    5 |*__|– GND
  ```
- **Settings**: 19200 baud, 1 stop bit, no parity
- **Protocol**: Modbus RTU

The NeoPool device acts as a Modbus **server** (formerly known as a _slave_), while this integration functions as a Modbus **client** (formerly known as a _master_).  
Only **one** Modbus client can be connected to a Modbus connector with the same label. It is not possible to operate multiple clients on connectors that share the same name.

Modbus connectors with **different labels** represent completely independent physical Modbus interfaces. Data traffic on one connector is **not visible** on the others.

There is one exception: the **DISPLAY** connector, which is present **twice** and is typically occupied by the built-in LCD.  
Since only one Modbus client can communicate with a Modbus server at a time, the DISPLAY connector is **not suitable** for this integration if the internal LCD is connected to either of the two DISPLAY ports.

---

## Features

- **Multi-hub support**: Add multiple VistaPool devices to Home Assistant, each with a custom name (used as a prefix in entity IDs).
- **Sensors**:  
  pH, Redox (ORP), Salt, Conductivity, Water Temperature, Ionization, Hydrolysis Intensity/Voltage, Device Time, Status/Alarm bits
  - **Filtration speed** _(only if the model has a variable-speed filtration pump)_
- **Number entities**:  
  Setpoints for pH, Redox, Chlorine, Temperature, and Hydrolysis production
- **Switches**:  
  Manual filtration, auxiliary relays (_Light & AUX1–AUX4_, enable in options), automatic time synchronization to Home Assistant _(default: disabled)_
- **Select entities**:  
  Filtration mode (_Manual, Auto, Heating, Smart, Intelligent_), timers for automatic filtration
  - **Filtration speed control** _(select entity; only if the model has a variable-speed pump)_
  - **Boost control** _(only if the Hydro/Electrolysis module is detected)_
- **Buttons**:  
  Manual sync of device time to Home Assistant time
  - **Reset Alarm** _(clears error/alarm states)_

---

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=svasek&repository=homeassistant-vistapool-modbus&category=Integration)

### [HACS](https://hacs.xyz/) (recommended)

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS (you can use the button above).
2. Install **VistaPool Modbus Integration**.
3. Restart Home Assistant.

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/vistapool` folder to your `/config/custom_components` directory.
3. Restart Home Assistant.

### Add Your Pool to Home Assistant

Now you just need to add your pool. You can click the button below:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vistapool)

Or you can add it manually:

- Navigate to **Devices & Services**.
- Click **Add Integration**.
- Search for and select **VistaPool Modbus Integration**.

---

## Configuration

1. In Home Assistant, go to **Settings → Devices & Services → Add Integration → VistaPool**.
2. Enter the connection details:
   - **Name**: Custom identifier for your pool (used as a prefix in entity IDs, e.g., `pool_west`)
   - **Host**: IP address of your Modbus TCP gateway
   - **Port**: _(default: 502)_
   - **Slave ID**: _(default: 1)_
   - **Scan interval**: _(default: 30s)_

### Options (after setup)

- **Adjust scan interval**
- **Enable/disable Relays** Light and AUX1–4 _(default: disabled)_

### Advanced Options: Unlocking “Backwash” Mode

The “Backwash” filtration mode is hidden in the integration UI by default, as its remote use can be risky and is intended only for advanced users.

If you want to make the “Backwash” option available in Home Assistant (for automations or remote control), you must **explicitly unlock it using a secret code in the integration’s options**:

1. Go to **Settings → Devices & Services → VistaPool Modbus Integration → Configure**.
2. In the options dialog, find the field **Unlock advanced options**.
3. Enter the code: `<device_prefix><current_year>`
   - Example: If your pool’s prefix is `Vistapool` and the year is 2025, enter `vistapool2025`.
   - The prefix is the same as used in your entity IDs (e.g. `switch.vistapool_light`).
4. Submit the form.  
   The advanced settings page will open, allowing you to enable “Backwash” mode.

> **⚠️ Warning:**  
> Enabling “Backwash” mode exposes the backwash function in the filtration mode select.  
> **Improper use may damage your filtration system! Only activate if you fully understand the risks.**

---

## Example Entities

Entities are prefixed by the custom name (e.g. `sensor.pool1_filt_mode`):

- **Sensors**:  
  `sensor.<name>_measure_ph`, `sensor.<name>_measure_temperature`, `sensor.<name>_filt_mode`,  
  `sensor.<name>_filtration_speed` _(if supported)_
- **Numbers**:  
  `number.<name>_hidro`, `number.<name>_ph1`,
  `number.<name>_heating_temp` _(if supported)_
- **Switches**:  
  `switch.<name>_filt_manual_state`, `switch.<name>_time_auto_sync`,
  `switch.<name>_light`, `switch.<name>_aux1`-`switch.<name>_aux4` _(if enabled)_
- **Selects**:  
  `select.<name>_filt_mode`, `select.<name>_filtration1_start`, `select.<name>_filtration1_stop`,
  `select.<name>_filtration_speed` _(if supported)_,  
  `select.<name>_cell_boost` _(if supported)_
- **Buttons**:  
  `button.<name>_sync_time`, `button.<name>_escape`

---

## Special Notes

- **Filtration speed sensor and control**:  
  Only available for variable-speed pump models.
- **Boost control (select)**:  
  Only available for models with the Hydro/Electrolysis module detected.
- **Reset Alarm button**:  
  Allows remote clearing of error and alarm states from Home Assistant.
- **Auxiliary relays (Light & AUX1–AUX4)**:  
  Only available if enabled in integration options.

---

## Based On

- [Tasmota Neopool driver](https://github.com/arendst/Tasmota/blob/master/tasmota/tasmota_xsns_sensor/xsns_83_neopool.ino)

---

## License

This project is licensed under the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/),  
the same license used by [Home Assistant](https://www.home-assistant.io/developers/license/).
