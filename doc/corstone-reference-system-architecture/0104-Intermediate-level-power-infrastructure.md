# Intermediate level power infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure>

### Intermediate level power infrastructure

The Intermediate Level power infrastructure makes some simplifications to reduce the complexity of the infrastructure at the cost of reducing the support provided to reduce always-on leakage power and power during HIBERNATE1 state.

The system at PILEVEL = 1 supports only one voltage domain:

VSYS
:   The system voltage domain.

    The previous VAON voltage domain is now merged into the system voltage domain and therefore VSYS is now also considered as an always ON voltage domain.

In addition, PD\_MGMT is merged into the PD\_AON domain.

- **[Power hierarchy](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Power-hierarchy?lang=en)**
   The system at PILEVEL = 1 supports several power domains:
- **[BR\_DEBUG power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-DEBUG-power-modes?lang=en)**
   The following figure shows the power modes that BR\_DEBUG supports.
- **[BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-SYS-power-modes?lang=en)**
   The following figure shows the power modes that BR\_SYS supports.
- **[BR\_CPU<n> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes?lang=en)**
   The following figure shows the power modes that BR\_CPU<n> supports.
- **[BR\_CRYPTO power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CRYPTO-power-modes?lang=en)**
   The following figure shows the power modes that BR\_CRYPTO supports.
- **[BR\_NPU<m> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-NPU-m--power-modes?lang=en)**
   The following figure shows the power modes that BR\_NPU<m>.
- **[Intermediate power dependency control](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Intermediate-power-dependency-control?lang=en)**
   The following table shows the PDCM table and it shows how the PD\_SYS and PD\_VMR<i> are affected by the power state of the other domains.
- **[Intermediate System level Power States](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Intermediate-System-level-Power-States?lang=en)**
   Through the relationship defined by Power dependency control matrix, and the CPU minimum power states, we can define several System Power States that the system supports.
