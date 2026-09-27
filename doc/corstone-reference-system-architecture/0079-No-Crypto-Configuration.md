# No-Crypto Configuration

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/CryptoCell/No-Crypto-Configuration>

### No-Crypto Configuration

When HASCRYPTO = 0, CryptoCell-312 does not exist in the system. Therefore, all associated interfaces and configuration that are associated with CryptoCell-312 do not need to exist.

In such a system, the root of trust can still be within the system, but if TBSA-M compliance is still required, the system integrator must ensure that the integrated system contains all the necessary resources that a root of trust requires.
