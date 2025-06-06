# Changelog

## [1.0.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.3...v1.0.2) (2025-06-06)


### Features

* ✨ Refactor VistaPool integration to streamline entity initialization ([f4727b4](https://github.com/svasek/homeassistant-vistapool-modbus/commit/f4727b49146ae56ba7c3c3c6b98b08366e2777fb))
* **binary_sensor, button, coordinator, sensor, switch:** ✨ Add automatic time synchronization feature ([83cff1d](https://github.com/svasek/homeassistant-vistapool-modbus/commit/83cff1d7ff8fa621a75fea1ca6f1a481af9b500f))
* **boost:** ✨ add boost mode functionality and translations ([62617d5](https://github.com/svasek/homeassistant-vistapool-modbus/commit/62617d59997b21ec607b57b57f4285c3a60771c3))
* **button:** ✨ add "Clear Errors" button functionality and translations ([b07dfe9](https://github.com/svasek/homeassistant-vistapool-modbus/commit/b07dfe9ea9f6e65291c8257c13d524a32199af11))
* **entity, helpers, modbus, number, select:** ✨ Add VistaPool integration enhancements ([c0d8de0](https://github.com/svasek/homeassistant-vistapool-modbus/commit/c0d8de09a8b60c99496ff3303a0505c84a33ac21))
* **filtration:** ✨ add filtration speed functionality controll for devices which support it ([5aed83c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/5aed83c9322b07da889eb83a06f09cadbc5683e8))
* **select:** ✨ Added options filtering based on heating mode and temperature sensor status ([61311ae](https://github.com/svasek/homeassistant-vistapool-modbus/commit/61311ae2bc44ad92c75fbc73c1ab421aaca6ccce))
* **sensor:** ✨ add filtration speed sensor and update translations ([cf5b51f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/cf5b51f1f1e34182b21e2debb9b14c9b3f45883f))
* **switch:** ✨ Add relay controll functionality for light and auxiliary relays ([aa3ad8d](https://github.com/svasek/homeassistant-vistapool-modbus/commit/aa3ad8dcb895bc0d11689bbe9457f1a5c47620fd))
* **translations:** ✨ Add AI generated translations ([0a7fe41](https://github.com/svasek/homeassistant-vistapool-modbus/commit/0a7fe41838b64620c8f137f73a4fb4a08f535120))


### Bug Fixes

* **const:** 🐛 Update DEFAULT_PORT to match standard configuration ([9c514c7](https://github.com/svasek/homeassistant-vistapool-modbus/commit/9c514c70bc999026d49dcf4be862b2cbbc206d1c))
* **manifest:** 🐛 Fixed documentation and issue tracker URLs ([7f23704](https://github.com/svasek/homeassistant-vistapool-modbus/commit/7f237046b293dc5054b310ef845430289ed352da))
* **manifest:** 🐛 Fixed integration version ([ebab4c1](https://github.com/svasek/homeassistant-vistapool-modbus/commit/ebab4c10e40d22db028f2e12ba198184be73512c))
* **manifest:** 🐛 Update version to 0.3.0 ([44a45cf](https://github.com/svasek/homeassistant-vistapool-modbus/commit/44a45cfbcb01af10a38b4290a173d59ae1ee7fcc))
* **modbus:** 🐛 add connection error handling for Modbus client ([e429430](https://github.com/svasek/homeassistant-vistapool-modbus/commit/e4294303703ef031e7a966967a97d357fd7b5c8f))
* **modbus:** 🐛 Corrected error logging for Modbus read operation ([505a2b2](https://github.com/svasek/homeassistant-vistapool-modbus/commit/505a2b2c501969518192d877c8c3a5d89878e017))
* **modbus:** 🐛 Fixed InvalidStateError ([102ebf9](https://github.com/svasek/homeassistant-vistapool-modbus/commit/102ebf9f95e4a478e184f35127955f39779fab7e))
* **number, select, switch:** 🐛 Improve state update handling ([a7ea717](https://github.com/svasek/homeassistant-vistapool-modbus/commit/a7ea717f9ebaeee910a9096e04f265767c502c79))
* **number:** 🐛 Update initialization to handle optional parameters ([f70f312](https://github.com/svasek/homeassistant-vistapool-modbus/commit/f70f312d0002d28938930fe44d8c842099f59b65))
* **select:** ✨ show/hide boost mode select based on model support ([9cca2ef](https://github.com/svasek/homeassistant-vistapool-modbus/commit/9cca2efc646a96d635f659b70fa9471ae243125f))
* **select:** 🐛 added turning off manual filtration before switch mode from manual ([db663ba](https://github.com/svasek/homeassistant-vistapool-modbus/commit/db663ba354fdb5bd7e2d0616090d069898935625))
* **sensor:** 🐛 Fix conditional check for ION current and model detection ([1d614ce](https://github.com/svasek/homeassistant-vistapool-modbus/commit/1d614ce42003f7c54f516d7f17f3667ef9c020e8))
* **sensor:** 🐛 Fixed typo return value for pol1 in VistaPoolSensor ([57f72d3](https://github.com/svasek/homeassistant-vistapool-modbus/commit/57f72d3258ac967db9447d2010be827f35a4b283))

## [1.2.3](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.2...v1.2.3) (2025-06-06)


### Bug Fixes

* **modbus:** 🐛 add connection error handling for Modbus client ([e429430](https://github.com/svasek/homeassistant-vistapool-modbus/commit/e4294303703ef031e7a966967a97d357fd7b5c8f))

## [1.2.3](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.2...v1.2.3) (2025-06-03)


### Bug Fixes

* **modbus:** 🐛 add connection error handling for Modbus client ([e429430](https://github.com/svasek/homeassistant-vistapool-modbus/commit/e4294303703ef031e7a966967a97d357fd7b5c8f))

## [1.2.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.1...v1.2.2) (2025-05-30)


### Bug Fixes

* **manifest:** 🐛 Fixed integration version ([ebab4c1](https://github.com/svasek/homeassistant-vistapool-modbus/commit/ebab4c10e40d22db028f2e12ba198184be73512c))

## [1.2.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.0...v1.2.1) (2025-05-29)


### Bug Fixes

* **select:** ✨ show/hide boost mode select based on model support ([9cca2ef](https://github.com/svasek/homeassistant-vistapool-modbus/commit/9cca2efc646a96d635f659b70fa9471ae243125f))

## [1.2.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.1.0...v1.2.0) (2025-05-29)


### Features

* **filtration:** ✨ add filtration speed functionality controll for devices which support it ([5aed83c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/5aed83c9322b07da889eb83a06f09cadbc5683e8))

## [1.1.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.0.3...v1.1.0) (2025-05-28)


### Features

* **boost:** ✨ add boost mode functionality and translations ([62617d5](https://github.com/svasek/homeassistant-vistapool-modbus/commit/62617d59997b21ec607b57b57f4285c3a60771c3))
* **button:** ✨ add "Clear Errors" button functionality and translations ([b07dfe9](https://github.com/svasek/homeassistant-vistapool-modbus/commit/b07dfe9ea9f6e65291c8257c13d524a32199af11))
* **sensor:** ✨ add filtration speed sensor and update translations ([cf5b51f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/cf5b51f1f1e34182b21e2debb9b14c9b3f45883f))

## [1.0.3](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.0.2...v1.0.3) (2025-05-26)


### Bug Fixes

* **modbus:** 🐛 Fixed InvalidStateError ([102ebf9](https://github.com/svasek/homeassistant-vistapool-modbus/commit/102ebf9f95e4a478e184f35127955f39779fab7e))

## [1.0.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.0.1...v1.0.2) (2025-05-25)


### Bug Fixes

* **manifest:** 🐛 Fixed documentation and issue tracker URLs ([7f23704](https://github.com/svasek/homeassistant-vistapool-modbus/commit/7f237046b293dc5054b310ef845430289ed352da))
