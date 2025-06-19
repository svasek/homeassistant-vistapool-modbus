# Changelog

## [1.7.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.0...v1.7.1) (2025-06-19)


### Bug Fixes

* **sensor:** 🐛 prevent stale sensor values when filtration is off ([cddd3d3](https://github.com/svasek/homeassistant-vistapool-modbus/commit/cddd3d3985d83a06d3e83ed061c20b550a1cf60e))

## [1.7.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.6.0...v1.7.0) (2025-06-19)


### Features

* **binary_sensor, sensor:** ✨ enhance sensor availability based on filtration state ([188ad35](https://github.com/svasek/homeassistant-vistapool-modbus/commit/188ad3559819c28057013fc2f9f342e27622e522))


### Bug Fixes

* **setup:** 🐛 skip setup if no data from Modbus ([c4ca493](https://github.com/svasek/homeassistant-vistapool-modbus/commit/c4ca49357673e71575b3857029fadaefe4fca581))

## [1.6.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.5.1...v1.6.0) (2025-06-19)


### Features

* **config_flow:** ✨ Added asynchronous host and port validation in the config flow ([de5f0fb](https://github.com/svasek/homeassistant-vistapool-modbus/commit/de5f0fbd6b253539f080799c6b9cb7142ef80083))


### Bug Fixes

* **binary_sensor, select, sensor:** 🐛 disable certain entities by default ([be7cca5](https://github.com/svasek/homeassistant-vistapool-modbus/commit/be7cca5895dc35bc98a0050a9ec16e5664d9dc90))

## [1.5.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.5.0...v1.5.1) (2025-06-18)


### Bug Fixes

* **modbus:** 🐛 ensure close method is callable before invoking ([6870501](https://github.com/svasek/homeassistant-vistapool-modbus/commit/6870501968fd301bccd8b4243412f08defe239d3))

## [1.5.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.4.0...v1.5.0) (2025-06-18)


### Features

* **light:** ✨ changed pool light from switch to light entity ([4666d21](https://github.com/svasek/homeassistant-vistapool-modbus/commit/4666d211a8a5e32f6b2b64e4879806e2c81cd0ed))
* **modbus:** ✨ persistent TCP client, reconnect and safe close ([cfac5c6](https://github.com/svasek/homeassistant-vistapool-modbus/commit/cfac5c660bc3caf0fc04e59e4639d5697350c7f4))


### Bug Fixes

* **coordinator:** 🐛 add support for enabling/disabling timers in coordinator ([abc6c2e](https://github.com/svasek/homeassistant-vistapool-modbus/commit/abc6c2ef3d1f5daac85e4d8802e78a8f02b66e81))
* **coordinator:** 🐛 handle Modbus communication errors gracefully ([d7972f2](https://github.com/svasek/homeassistant-vistapool-modbus/commit/d7972f2ad7ee50470df052aa1b498c15310c255b))
* **modbus:** 🐛 improve client closing logic for Modbus connection ([f075caf](https://github.com/svasek/homeassistant-vistapool-modbus/commit/f075cafc8c74bfc6985c52ef4da9a13a5c8fa16e))

## [1.4.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.3.0...v1.4.0) (2025-06-17)


### Features

* **options:** ✨ add timer resolution and update scan interval descriptions ([d83053d](https://github.com/svasek/homeassistant-vistapool-modbus/commit/d83053d499a6f3f5157ab5c9425dac298978dfa1))
* **relays:** ✨ Add timer functionality for AUX and Light relays ([#27](https://github.com/svasek/homeassistant-vistapool-modbus/issues/27)) ([89c312b](https://github.com/svasek/homeassistant-vistapool-modbus/commit/89c312b90c675a0418e3f219e92caefc2e912e5b))

## [1.3.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.5...v1.3.0) (2025-06-15)


### Features

* **options:** ✨ add advanced options for enabling 'Backwash' mode ([9993931](https://github.com/svasek/homeassistant-vistapool-modbus/commit/99939316b815c09539d93a304a93870ee2fddda5))
* **options:** ✨ enhance options flow with automatic integration reload ([02d1e21](https://github.com/svasek/homeassistant-vistapool-modbus/commit/02d1e215a825ff28c4094e16d14293e86a53639e))

## [1.2.5](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.4...v1.2.5) (2025-06-11)


### Bug Fixes

* **binary_sensor:** 🛠️ skip acid pump if relay is not assigned ([89e7529](https://github.com/svasek/homeassistant-vistapool-modbus/commit/89e752964c3fe193d6c3ed628a43730db540154d))

## [1.2.4](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.2.3...v1.2.4) (2025-06-06)


### Bug Fixes

* **timer:** 🐛 pad timer registers to ensure correct parsing ([4d12a1c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/4d12a1ceec68bd78a522a2d780dd6411dd9cba4e))

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
