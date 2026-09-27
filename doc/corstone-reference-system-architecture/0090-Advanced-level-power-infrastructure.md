# Advanced level power infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure>

### Advanced level power infrastructure

The Advanced level power infrastructure specifies a power control infrastructure that provides additional functionality to help an implementation achieve very low power at the lowest System Power State. This is achieved by providing more voltage and power domains.

The system at PILEVEL = 2 supports two voltage domains:

VAON
:   The always on voltage domain.

    This voltage domain is intended only to drive Always ON logic and therefore only includes the PD\_AON domain. As its name suggest, the domain must always be always ON.

    This domain is separated from the VSYS to allow always on logic to be implemented using a different target process technology to reduce always on power.

VSYS
:   The system voltage domain.

    This voltage domain implements all other power domains in the system. VSYS, if required, can be powered OFF in the lowest power state as long as all retention requirement of any host logic host within it during the lowest power state are met.

- **[Power hierarchy](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/Power-hierarchy?lang=en)**
   The system at PILEVEL = 2 supports the following power domains:
- **[BR\_MGMT power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-MGMT-power-modes?lang=en)**
   The following figure shows the power modes that BR\_MGMT supports.
- **[BR\_DEBUG power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-DEBUG-power-modes?lang=en)**
   On Cold reset, PD\_DEBUG automatically transitions to ON state and enters OFF state eventually, if the debug system is not required to stay ON. It is woken either through the PD\_DEBUG’s Power Control Wakeup Q-Channel Device interface or through a bus access targeting its shared debug domain.
- **[BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-SYS-power-modes?lang=en)**
   The following figure shows the power modes that BR\_SYS supports.
- **[BR\_CPU<n> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-CPU-n--power-modes?lang=en)**
   The following figure shows the power modes that each of the BR\_CPU<n> supports.
- **[BR\_CRYPTO power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-CRYPTO-power-modes?lang=en)**
   The following figure shows the power modes that BR\_CRYPTO supports.
- **[BR\_NPU<m> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-NPU-m--power-modes?lang=en)**
   The following figure shows the power modes supported by BR\_NPU<m>.
- **[Advanced level power dependency control](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/Advanced-level-power-dependency-control?lang=en)**
   The following table shows an example, with PDCMQCHWIDTH of 4, and four CPU cores, how each of the power domains are affected by the power state of the other domains.
- **[System Level Power States](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/System-Level-Power-States?lang=en)**
   Through the relationship defined by the Power dependency control matrix, the MIN\_PWR\_STATEs of each power domain, and the CPU minimum power states, we can define several System Power States that the system supports.
