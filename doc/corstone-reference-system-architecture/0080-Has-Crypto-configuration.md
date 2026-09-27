# Has-Crypto configuration

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/CryptoCell/Has-Crypto-configuration>

### Has-Crypto configuration

When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.

CryptoCell-312 provides the following:

- Cryptographic acceleration for the protection of data-in-transit (communication protocols) and data-at-rest.
- Protection of various assets belonging to the IC or device manufacturer, service operators providing services over the target device and also for the end user. These asset protection features include:

  - Image verification at boot or during runtime
  - Authenticated debug
  - True random number generation
  - Lifecycle management
  - Provisioning of assets

When CryptoCell-312 exists, the following is provided:

- A configuration interface for CryptoCell that is mapped at aliased address regions 0x4009\_0000 to 0x4009\_3FFF and 0x5009\_0000 to 0x5009\_3FFF. This interface provides access to programmer visible registers within CryptoCell-312 and parts of the Non-Volatile Memory (NVM) memory with word address of 0x00A0 to 0x1FFC, and CryptoCell-312 itself handles security checking of accesses to its registers on its own.
- Access to the same NVM memory at aliased system addresses 0x0E00\_0000 to 0x0E00\_1FFF and 0x1E00\_0000 to 0x1E00\_1FFF. This interface provides access to the NVM, with word address of 0x00A0 to 0x1FFC. Note the address offset of 0xA0 being applied to the system address when accessing the NVM memory.
- CryptoCell can access the system as a manager only to the following address space:

  - Manager Code Main Expansion Interface, at addresses 0x0100\_0000 to 0x0DFF\_FFFF, and 0x1100\_0000 to 0x1DFF\_FFFF.
  - All implemented VM areas 0x2100\_0000 to 0x21FF\_FFF, and 0x3100\_0000 to 0x31FF\_FFFF.
  - Manager Main Expansion Interface at the following address range:

    - 0x2800\_0000 to 0x2FFF\_FFFF.
    - 0x3800\_0000 to 0x3FFF\_FFFF.
    - 0x6000\_0000 to 0xDFFF\_FFFF.
- Persistent State storage to store key states that must be preserved.
- An NVM interface, which connects to the top level of CRSAS Ma1.

For more information on CryptoCell-312, see Arm® CryptoCell™-312 Technical Reference Manual.
