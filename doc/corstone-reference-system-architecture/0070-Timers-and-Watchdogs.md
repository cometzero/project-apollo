# Timers and Watchdogs

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Timers-and-Watchdogs>

### Timers and Watchdogs

CRSAS Ma1 supports two main classes of timers and watchdogs: Timestamp based Timers and SLOWCLK AON based timers.

- **[Timestamp-based timers](/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs/Timestamp-based-timers?lang=en)**
   The first class of timer and watchdogs are timestamp-based. They use the timestamp value provided on the System Timestamp Interface.
- **[SLOWCLK AON Timers](/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en)**
   The second class of timers and watchdogs are simple CMSDK based 32-bit timers that run on SLOWCLK. They reside in PD\_AON power domain and are reset by nWARMRESETAON. A single timer and a single Secure privileged Watchdog are provided and are expected to be used when the system is in HIBERNATION{0-1} when potentially only SLOWCLK is available and running and all other clocks are off.
