# VistaPool Modbus Integration for Home Assistant

- Easily connect your Sugar Valley (NeoPool, Hidrolife, Aquascenic, Bionet...) or compatible pool controller to Home Assistant via Modbus TCP.
- Full local control, real-time sensors, timers, relays, automation support, and more.

[![Release](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/release.yml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/release.yml)
[![Validate with Hassfest](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/hassfest.yml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/validate-hacs.yaml/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/validate-hacs.yaml)
[![CodeQL](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/svasek/homeassistant-vistapool-modbus/actions/workflows/github-code-scanning/codeql)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **This integration is available via [HACS](https://hacs.xyz/) and is recommended for most users.**

**Supported brands / devices:**  
Hidrolife • Aquascenic • Oxilife • Bionet • Hidroniser • UVScenic • Station • Brilix (Albixon) • Bayrol • Hay • Hayward • Aquarite • Kripsol KLX • Certikin • Poolstar • GrupAquadirect • Pentair • ProducPool • Pool Technologie

---

## What does this integration do?

- Provides **full local control** of supported pool controllers over Modbus TCP.
- Adds real-time sensors, numbers, switches, selects, and buttons for all available features.
- Allows timer/relay/aux configuration, automation and Home Assistant UI integration.
- Supports multiple pools or hubs, each as a separate integration.

---

## Hardware Connection

- **Gateway:** Any Modbus TCP gateway (e.g. [USR-DR164](https://www.pusr.com/products/Serial-to-Dual-Band-WiFi-Converter.html))
- **Connector:** Standard **2.54 mm** 5-pin PCB female connector
- **Settings:** 19200 baud, 1 stop bit, no parity
- **Protocol:** Modbus RTU
- **See the [Modbus Connection Guide](docs/modbus-connection-guide.md)** for more info and images.

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

- **The NeoPool device acts as a Modbus _server_ (slave), this integration is a Modbus _client_ (master).**
- **Only one Modbus client can be connected to a Modbus connector with the same label**. It is not possible to operate multiple clients on connectors that share the same name.
- **Modbus connectors with different labels represent independent physical interfaces.** Data traffic on one connector is **not visible** on others.
- The **DISPLAY** connector is present **twice** and is usually used by the built-in LCD.
  **Do not use it for this integration if the LCD is connected!**

---

## Features

- **Reliable single Modbus TCP connection per device/hub** (improves stability, avoids connection issues).
- **Multi-hub support**: Add multiple VistaPool devices, each with a custom prefix (used in entity IDs).
- **Sensors**:
  pH, Redox (ORP), Salt, Conductivity, Water Temperature, Ionization, Hydrolysis Intensity/Voltage, Device Time, Status/Alarm bits, Filtration speed _(if supported)_.
- **Numbers**:
  Setpoints for pH, Redox, Chlorine, Temperature, Hydrolysis production.
- **Switches**:
  Manual filtration, relays (_Light & AUX1–AUX4_, can be enabled in Options), automatic time sync to Home Assistant (default: disabled).
- **Selects**:
  Filtration mode (Manual, Auto, Heating, Smart, Intelligent), timers for automatic filtration, filtration speed _(if supported)_, boost control _(if Hydro/Electrolysis module is present)_.
- **Buttons**:
  Manual time sync, reset alarm/error states.

---

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=svasek&repository=homeassistant-vistapool-modbus&category=Integration)

### [HACS](https://hacs.xyz/) (recommended)

1. Open **HACS** in Home Assistant.
2. Go to **Integrations** and search for **VistaPool Modbus Integration** (no need to add a custom repository, this integration is included in the HACS default list).
3. Install **VistaPool Modbus Integration**.
4. Restart Home Assistant.

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/vistapool` folder to your `/config/custom_components` directory.
3. Restart Home Assistant.

## Setup and Configuration

After installing the integration via HACS and restarting Home Assistant:

### 1. Add Your Pool to Home Assistant

You can use the button below to start configuration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vistapool)

Or add manually:

- Go to **Settings → Devices & Services**.
- Click **Add Integration**.
- Search for and select **VistaPool Modbus Integration**.

### 2. Enter Connection Details

- **Name**: Custom identifier for your pool.  
  _This will be used as a prefix in all entity IDs, with spaces replaced by underscores and converted to lowercase_  
  _(e.g., entering “Pool West” becomes `pool_west`, and your entity will be `sensor.pool_west_measure_ph`)_.
- **Host**: IP address of your Modbus TCP gateway
- **Port**: _(default: 502)_
- **Slave ID**: _(default: 1)_
- **Scan interval**: _(default: 30s)_

### 3. Adjust Integration Options (Optional)

After initial setup, you can fine-tune the integration:

- **Scan interval** (default: 30s)
- **Timer resolution** (default: 15m)
- **Enable/disable relays** (Light and AUX1–AUX4 are default: disabled)
- **Enable/disable filtration timers** (filtration1, filtration2, filtration3)
- **Unlock advanced features** (see [below](#advanced-options-unlocking-backwash-mode))

Go to **Settings → Devices & Services → VistaPool Modbus Integration → Configure**  
to adjust options at any time.

---

### Advanced Options: Unlocking “Backwash” Mode

The “Backwash” filtration mode is hidden by default, as its remote use can be risky and is intended only for advanced users.

To enable it:

1. Go to **Settings → Devices & Services → VistaPool Modbus Integration → Configure**.
2. In the options dialog, find the field **Unlock advanced options**.
3. Enter the code: `<device_prefix><current_year>`

- Example: If your pool’s prefix is `vistapool` and the year is 2025, enter `vistapool2025`.
- The prefix is the same as in your entity IDs (e.g., `switch.vistapool_light`).

4. Submit the form. The advanced settings page will open, allowing you to enable “Backwash” mode.

> **⚠️ WARNING:**
> Enabling “Backwash” exposes this function in filtration mode selection.
> **Improper use may damage your filtration system! Only activate if you fully understand the risks.**

---

## Example Entities

Entities are lowercased and prefixed by your custom name, e.g. `sensor.pool1_filt_mode`:

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

- **Only enabled timers and relays (per Options) are shown in Home Assistant.**
- **Timer resolution:** Can be set (in minutes) in integration Options.
- **Entities cache last value** if there is a Modbus communication problem.
- **Backwash and advanced options:** See above for details.
- **Reload on options change:** Integration is reloaded automatically on option changes.
- **Filtration speed sensor/control:** Only available for variable-speed pump models.
- **Boost control (select):** Only if Hydro/Electrolysis module is present.
- **Reset Alarm button:** Allows clearing of error and alarm states from HA.

---

## Based On

- [Tasmota Neopool driver](https://github.com/arendst/Tasmota/blob/master/tasmota/tasmota_xsns_sensor/xsns_83_neopool.ino)

---

## Disclaimer

This integration is provided "AS IS" and without any warranty or guarantee of any kind.  
The author takes no responsibility for any damage, loss, or malfunction resulting from the use or misuse of this code. Use at your own risk.

## License

This project is licensed under the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/),
the same license used by [Home Assistant](https://www.home-assistant.io/developers/license/).

_This project is not affiliated with or endorsed by any pool controller manufacturer._
