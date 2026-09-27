# System timer components

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components>

### System timer components

The system timer components are:

- The System Counter generates a timestamp value that can be shared across the System on Chip (SoC).
- The System Timer can raise an interrupt when a period has elapsed.
- System Watchdog provides a mechanism to detect errant system behavior causing reset of the system if a period elapses without intervention.

The components are software‑programmable using APB interfaces.

- **[System Counter overview](/documentation/102803/0000/System-timer-components/System-Counter-overview?lang=en)**
   This section provides an overview of the System Counter.
- **[Counter operation flows](/documentation/102803/0000/System-timer-components/Counter-operation-flows?lang=en)**
   This section describes pseudo‑sequences for some of the commonly used Counter programming flows.
- **[System counter Programmers model](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model?lang=en)**
   This section describes programmers model for the System Counter. Registers in the System Counter provide the following functions:
- **[System Timer overview](/documentation/102803/0000/System-timer-components/System-Timer-overview?lang=en)**
   This section provides an overview of the System Timer.
- **[System timer programmers model](/documentation/102803/0000/System-timer-components/System-timer-programmers-model?lang=en)**
   The registers of the System Timer are grouped into a single 4KB block that is called the CNTBase frame. The base address of the CNTBase frame is not defined here and is IMPLEMENTATION DEFINED.
- **[System Watchdog overview](/documentation/102803/0000/System-timer-components/System-Watchdog-overview?lang=en)**
   The following figure shows a block diagram of the System Watchdog.
