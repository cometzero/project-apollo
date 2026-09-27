# System Counter overview

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-Counter-overview>

### System Counter overview

This section provides an overview of the System Counter.

The System Counter has the following features:

- Binary encoded, unsigned, 64‑bit up‑counter, starts counting from 0, with the optional ability to start counting from a different preload value.
- Generates a 64‑bit time value that compatible components across the SoC can share.
- Internal 24‑bit fractional value to allow fine count resolution control.
- Ability to scale counter clock frequency, therefore allowing operation at lower frequency during low‑power mode.
- Hardware can handle dynamic clock switching between different frequencies. Software is required only for initialization.
- Support of software enabled halt‑on‑debug from external CoreSight Cross Trigger Interface (CTI).
