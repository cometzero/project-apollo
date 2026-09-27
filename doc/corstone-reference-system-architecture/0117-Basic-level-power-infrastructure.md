# Basic level power infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure>

### Basic level power infrastructure

The Basic Level power infrastructure, when PILEVEL = 0, locks the CPU top-level power domain to the main system to reduce the complexity of the infrastructure to reduce the complexity of the infrastructure by locking the CPU top-level power domain to the main system. This reduces the number of power domains and hence the number of PPUs in the system.

Therefore, this simlification removes the ability to separately control the power state of the processor, the system, and volatile memories in the system. In addition, such a system can only support a single processor and therefore NUMCPU must be ‘0’ when PILEVEL = 0.

- **[Power hierarchy](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/Power-hierarchy?lang=en)**
   The system at PILEVEL = 0 supports only one voltage domain:
- **[BR\_DEBUG power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-DEBUG-power-modes?lang=en)**
   The following figure shows the power modes that BR\_DEBUG supports.
- **[BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-SYS-power-modes?lang=en)**
   The following figure shows the power modes that BR\_SYS supports. Because PD\_SYS is merged with PD\_CPU0 when PILEVEL = 0, BR\_SYS has a power mode transition diagram like BR\_CPU<n> when PILEVEL = 1.
- **[BR\_NPU<m> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-NPU-m--power-modes?lang=en)**
   The following figure shows the power modes that BR\_NPU<m>.
- **[Basic power dependency control](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/Basic-power-dependency-control?lang=en)**
   The following table shows the PDCM table and it shows how the PD\_SYS is affected by the power state of the other domains.
- **[Basic System Level Power States](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/Basic-System-Level-Power-States?lang=en)**
   Through the relationship defined by Power dependency control matrix, and the CPU minimum power states, we can define several System Power States that the system supports, and these are:
