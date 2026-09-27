# Trusted Base System Architecture for Armv8-M

Source: <https://developer.arm.com/documentation/102803/latest/Overview/Compliance/Trusted-Base-System-Architecture-for-Armv8-M>

### Trusted Base System Architecture for Armv8-M

The Arm® Platform Security Architecture, Trusted Base System Architecture for Arm®v6-M, Arm®v7-M and Arm®v8-M 2.0 (TBSA-M) is part of Arm Platform Security Architecture (PSA).

TBSA-M implements best practice security principles when designing systems around Armv8-M processing elements (PEs). These principles support the design and integration of the following features rooted in hardware:

- Root of Trust (RoT)
- A protected key store
- Isolation between Secure and Non-secure software components
- A Secure firmware update mechanism
- A lifecycle management mechanism, for Secure control of debug, test, and access to provisioned secrets
- A high-entropy random number generator, for reliable cryptography
- Cryptographic acceleration

CRSAS Ma1 specifies a system architecture that only partly fulfills the requirements specified within the TBSA-M. However, it specifies many features that help form the core of a system that complies.

For a system that integrates an CRSAS Ma1 based subsystem to comply with TBSA-M, the integrator, when expanding the system is required to continue to complying with TBSA-M requirements. For example:

- Suitable fuses are required to be added to CryptoCell. While CryptoCell handles error detection, you must ensure the fuses cannot be unprogrammed and they are reliable and confidential.
- When adding more managers and subordinates to the system, the memory space continues to obey Secure and Non-secure world partitioning.

Adherence to TBSA-M requirements helps to create a secure system, but it does not create a system that mitigates Denial of Service (DoS) attacks. As such, DoS is out of scope of CRSAS Ma1.
