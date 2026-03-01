# Changelog

## [1.14.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.13.2...v1.14.0) (2026-03-01)


### Features

* **binary_sensor:** ✨ add Pool Cover sensor ([#65](https://github.com/svasek/homeassistant-vistapool-modbus/issues/65)) ([915e3ca](https://github.com/svasek/homeassistant-vistapool-modbus/commit/915e3caade00bbfc23e5bb88af0eb18297491e51)), closes [#58](https://github.com/svasek/homeassistant-vistapool-modbus/issues/58)


### Bug Fixes

* 🐛 code review fixes for HA 2026.2 compatibility ([#69](https://github.com/svasek/homeassistant-vistapool-modbus/issues/69)) ([2491d0f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/2491d0f861befdd16b10474d874479cbcb23b14d))
* 🐛 correct hydrolysis intensity unit determination logic ([#64](https://github.com/svasek/homeassistant-vistapool-modbus/issues/64)) ([61ba9de](https://github.com/svasek/homeassistant-vistapool-modbus/commit/61ba9de23f0686b0ee5084c2f968f42376014df9))
* **sensor:** 🔧 update icons for filtration modes ([006ceca](https://github.com/svasek/homeassistant-vistapool-modbus/commit/006ceca98d563ae1a9ae67ea2640d57d65b7bde8))

## [1.13.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.13.1...v1.13.2) (2026-02-05)


### Bug Fixes

* 🐛 remove redundant entity_id assignment in component classes ([1778567](https://github.com/svasek/homeassistant-vistapool-modbus/commit/177856729ee9f74ac9a242c63195051b95a0762c)), closes [#61](https://github.com/svasek/homeassistant-vistapool-modbus/issues/61)

## [1.13.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.13.0...v1.13.1) (2026-02-05)


### Bug Fixes

* **sensor defs:** 🔧 set unit for pH measurement ([#60](https://github.com/svasek/homeassistant-vistapool-modbus/issues/60)) ([6d21ec8](https://github.com/svasek/homeassistant-vistapool-modbus/commit/6d21ec84cb8cb2776e3f526822782b75a0a4d2b8)), closes [#59](https://github.com/svasek/homeassistant-vistapool-modbus/issues/59)

## [1.13.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.12.1...v1.13.0) (2025-10-21)


### Features

* **sensor:** ✨ add intelligent mode intervals sensor ([fa98d8c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/fa98d8c55c783faa92eaa8a82e648015580f87b0))
* **sensor:** ✨ add intelligent mode next interval sensor ([b73e8c3](https://github.com/svasek/homeassistant-vistapool-modbus/commit/b73e8c3416a91b5f503ba09112a2ef60f6b3a839))


### Bug Fixes

* **coordinator:** 🔧 handle simultaneous setpoint changes and initial sync ([79fbbfd](https://github.com/svasek/homeassistant-vistapool-modbus/commit/79fbbfda04baefc9930c7dab279c4c61bc6fecec))
* **sensor:** 🔧 skip temperature sensor when not detected ([b0cb16a](https://github.com/svasek/homeassistant-vistapool-modbus/commit/b0cb16adb8efbc1d459ea858ff3d24d824901644))

## [1.12.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.12.0...v1.12.1) (2025-10-20)


### Bug Fixes

* **translations:** 🔧 correct phrasing in Czech and Spanish translations ([6ec1871](https://github.com/svasek/homeassistant-vistapool-modbus/commit/6ec18711532200f69c45e52c8d87334557d181f4))

## [1.12.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.11.0...v1.12.0) (2025-10-17)


### Features

* ✨ add climate mode switch functionality ([98c2c9c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/98c2c9ce00086d628a35b143bce20b8896463487))
* ✨ add heating and intelligent setpoint synchronization ([937d414](https://github.com/svasek/homeassistant-vistapool-modbus/commit/937d414555518311dc2425836c776aa0d771df29))
* ✨ add intelligent minimum filtration time support ([6709354](https://github.com/svasek/homeassistant-vistapool-modbus/commit/67093548bb52ab75bc95d56e5534453611c6f878))
* ✨ add smart temperature and antifreeze features ([ea923e3](https://github.com/svasek/homeassistant-vistapool-modbus/commit/ea923e3c5cbb3338cefcd0d3b6cf137fe91ef7ed)), closes [#50](https://github.com/svasek/homeassistant-vistapool-modbus/issues/50)

## [1.11.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.10.1...v1.11.0) (2025-09-04)


### Features

* **modbus:** ✨ add compatibility helpers for pymodbus addressing ([bc3cfc4](https://github.com/svasek/homeassistant-vistapool-modbus/commit/bc3cfc48dbb99ff32d22ec91044bf69f320950cf))


### Bug Fixes

* **modbus:** 🐛 improve error handling by raising ModbusException ([ecc7ab0](https://github.com/svasek/homeassistant-vistapool-modbus/commit/ecc7ab0151cb9130ad3c5a4b5d103bb4028ff6b2))

## [1.10.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.10.0...v1.10.1) (2025-08-15)


### Bug Fixes

* **modbus:** 🐛 correct register indices for power module data retrieval ([d93b969](https://github.com/svasek/homeassistant-vistapool-modbus/commit/d93b969620664758913afefb5f3ce6b75171917d))
* **modbus:** 🐛 validate AUX relay index before writing state ([e28d708](https://github.com/svasek/homeassistant-vistapool-modbus/commit/e28d7087110693ea7ec7f8511bbf5d0e6a7568f8))

## [1.10.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.9.0...v1.10.0) (2025-08-10)


### Features

* **select:** ✨ Add pH pump activation delay feature ([a613494](https://github.com/svasek/homeassistant-vistapool-modbus/commit/a613494a0e82e8896945e3db17200e502902bdcd))


### Bug Fixes

* 🐛 correct typos, redundancies and formating ([471bb18](https://github.com/svasek/homeassistant-vistapool-modbus/commit/471bb1867ff5f5b550d777242dad360414d7556f))
* **coordinator:** 🐛 ensure config_entry is passed to DataUpdateCoordinator ([a461cf1](https://github.com/svasek/homeassistant-vistapool-modbus/commit/a461cf18e0d87a9dac2f35c3845b64d7dcc29645))
* **number:** 🐛 optimize value retrieval using coordinator cache ([46c05de](https://github.com/svasek/homeassistant-vistapool-modbus/commit/46c05de1c3f9139ebf618e6ce736c3bc4488e327))

## [1.9.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.8.4...v1.9.0) (2025-07-20)


### Features

* **coordinator:** ✨ improve update interval handling and error management ([04b8c49](https://github.com/svasek/homeassistant-vistapool-modbus/commit/04b8c4943308bee1685ef44fd0c1a65c9e904f00))
* **modbus:** ✨ add diagnostics tracking and error handling metrics ([7c1dfc6](https://github.com/svasek/homeassistant-vistapool-modbus/commit/7c1dfc61e14a56f15f78bbe8759c405e938c4f03))

## [1.8.4](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.8.3...v1.8.4) (2025-07-19)


### Bug Fixes

* **modbus:** 🩹 ensure consistent return values in async_write_register ([bfbe8d1](https://github.com/svasek/homeassistant-vistapool-modbus/commit/bfbe8d1919540c9eedb1e123565dc4c0f612322c))
* **number:** 🩹 improve logging during entity addition ([08fb3ad](https://github.com/svasek/homeassistant-vistapool-modbus/commit/08fb3ad8afa61521af9344ef5592ee269b515ca6))
* **sensor:** 🩹 streamline filtration speed checks and icon mapping ([a1be07f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/a1be07f96f6358a3c2ca91e3b851852fedef2d3a))

## [1.8.3](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.8.2...v1.8.3) (2025-07-18)


### Bug Fixes

* **binary_sensor:** 🩹 improve device status handling for binary sensors ([dcd4e36](https://github.com/svasek/homeassistant-vistapool-modbus/commit/dcd4e36a4ecde59ca4bf4947696e258445343c4f))
* **diagnostics:** 🩹 handle missing coordinator in diagnostics retrieval ([f2c5fab](https://github.com/svasek/homeassistant-vistapool-modbus/commit/f2c5fab5ad8a39be47e7199b979156f44b2c9253))
* **modbus:** 🩹 improve connection handling and diagnostics ([9fffdb9](https://github.com/svasek/homeassistant-vistapool-modbus/commit/9fffdb9c22b1f0f9ccb7a7a7f0e358a14321d544))

## [1.8.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.8.1...v1.8.2) (2025-07-09)


### Bug Fixes

* **light, number, select, switch:** 🐛 handle missing Modbus client ([5e42b0c](https://github.com/svasek/homeassistant-vistapool-modbus/commit/5e42b0cf3ec5e705d940f4e0b23f50a9f151f44a))

## [1.8.1](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.8.0...v1.8.1) (2025-06-30)


### Bug Fixes

* **entity:** 🐛 update suggested_object_id to use device_slug ([b7c0cd4](https://github.com/svasek/homeassistant-vistapool-modbus/commit/b7c0cd474e7d7ef5567129339afcfe6fa0781607))

## [1.8.0](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.5...v1.8.0) (2025-06-30)


### Features

* **config,options:** ✨ add new options for enabling filtration timers in the configuration ([75a46cb](https://github.com/svasek/homeassistant-vistapool-modbus/commit/75a46cbd824689a9dffbb615c43e667e8e3ee073))

## [1.7.5](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.4...v1.7.5) (2025-06-23)


### Bug Fixes

* **binary_sensor:** 🐛 update default enabled state for sensors ([7d81822](https://github.com/svasek/homeassistant-vistapool-modbus/commit/7d818226fd1fa9800aaa9b903788fb0af64f432e))

## [1.7.4](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.3...v1.7.4) (2025-06-20)


### Bug Fixes

* **modbus:** 🩹 improve client closure handling for unstable Modbus connections ([81f33cf](https://github.com/svasek/homeassistant-vistapool-modbus/commit/81f33cf3d21487b2b59890729684798fb51def3e))
* **sensor:** 🐛 update pH level unit to None for consistency ([3ca6b0b](https://github.com/svasek/homeassistant-vistapool-modbus/commit/3ca6b0b81eb31cdb24c57bd176021024a475e1c6))

## [1.7.3](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.2...v1.7.3) (2025-06-20)


### Bug Fixes

* **sensor:** 🩹 add option to measure values when filtration is off ([51fc55f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/51fc55f3aacb43bc068cb32497eaf7530f2cf7eb))

## [1.7.2](https://github.com/svasek/homeassistant-vistapool-modbus/compare/v1.7.1...v1.7.2) (2025-06-19)


### Bug Fixes

* **sensor:** 🩹 enhance sensor definitions with device and state classes ([c55a15f](https://github.com/svasek/homeassistant-vistapool-modbus/commit/c55a15f93d9ca228c76fa640df2f07f1bc0bd6d5))

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
