# CryptoCell

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/CryptoCell>

### CryptoCell

CRSAS Ma1 supports two possible cryptographic configurations:

- HASCRYPTO = 0: In this No-Crypto configuration, the CryptoCell-312 IP and its associated integration logic do not exist within the system.
- HASCRYPTO = 1: In this Has-Crypto configuration, the CryptoCell-312 IP and its associated integration logic exist within the system.

- **[No-Crypto Configuration](/documentation/102803/0000/Functional-Description/CryptoCell/No-Crypto-Configuration?lang=en)**
   When HASCRYPTO = 0, CryptoCell-312 does not exist in the system. Therefore, all associated interfaces and configuration that are associated with CryptoCell-312 do not need to exist.
- **[Has-Crypto configuration](/documentation/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en)**
   When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.
