# RAS extension support

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support>

### RAS extension support

The DynamIQ Shared Unit-120AE (DSU-120AE) supports the Reliability, Availability, Serviceability (RAS) Extension, including all extensions up to Arm®v9.0-A. You can optionally enable Error Correcting Code (ECC) support for the L3 cache RAMs and snoop filter RAMs at build time configuration.

The DSU-120AE supports:

- Cache protection with ECC on the L3 cache RAMs and snoop filter RAM
- Poison attribute on bus transfers
- Error Data Record registers
- Fault Handling Interrupts (FHIs)
- Error Recovery Interrupts (ERIs)
- Critical Error Interrupts (CRIs)
- Error injection

Node 0 observed by the cores includes the L3 memory system for the DSU-120AE. For other nodes observed by the core or complex, see your core Technical Reference Manual (TRM).

For more information on the architectural RAS Extension and the definition of a node, see the [Arm® Reliability, Availability, and Serviceability (RAS) System Architecture for A-profile architecture](https://developer.arm.com/documentation/IHI0100/aa/?lang=en).
