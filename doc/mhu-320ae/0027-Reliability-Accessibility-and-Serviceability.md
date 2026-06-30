# Reliability, Accessibility, and Serviceability

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability>

### Reliability, Accessibility, and Serviceability

MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.

The configuration parameters to enable RAS features for RAMs related to a given channel type are:

- Doorbell channels: `RAS_DB_PRESENT`
- Fast channels: `RAS_FAST_PRESENT`
- FIFO channels: `RAS_FIFO_PRESENT`

The MHU makes all necessary information available to software through Arm RASv1.1 architecture-compliant register space. For more information about RASv1.1 architecture, see the RAS System Architecture chapter of the [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487).
