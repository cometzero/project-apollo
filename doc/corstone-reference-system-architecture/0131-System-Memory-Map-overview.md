# System Memory Map overview

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Memory-Map-overview>

### System Memory Map overview

The High Level System Address Map table shows the high-level view of the memory map defined by CRSAS Ma1. This memory map is divided into Secure and Non-secure regions. The memory alternates between Secure and Non-secure regions on 256Mbyte regions, with only a few address areas exempted from security mapping because they are related to debug functionality.

To provide memory blocks and peripherals that can be mapped either as Secure or Non-secure using software, several address regions are aliased as shown in the table. Software can then choose to allocate each memory block or peripheral as Secure or Non-secure using protection controllers. The Implementation Defined Attribution Unit (IDAU) Region Values columns in the table specifies each area’s security along with its ID and each region’s Non-secure Callable (NSC) settings.

The following occur except when specifically stated:

- All accesses to unmapped regions of the memory result in bus-error response.
- When accessing unmapped address space within a mapped region taken by a peripheral, the access results in Read-As-Zero and Write-Ignored (RAZ/WI) except when specifically stated otherwise.
- Any accesses that result in security violations are either RAZ/WI or return a bus error response as defined by the SECRESPCFG register setting.

Some regions of memory map are reserved to maintain compatibility with past and future subsystems. Other areas are mapped to Expansion interfaces.

All accesses targeting populated Volatile Memory regions within 0x2100\_0000 to 0x21FF\_FFFF and 0x3100\_0000 to 0x31FF\_FFFF support exclusive access since they implement exclusive access monitoring, provided the accesses are from:

- The CPUs,
- Expansion managers through the Subordinate Main Expansion Interfaces and Subordinate Peripheral Expansion Interfaces.

Exclusive access is not supported for other regions implemented within the subsystem. For regions that reside in user expansion areas, exclusive access support is defined by the user expansion logic. If an exclusive access tries to access a region that does not support exclusive accesses, these accesses are not monitored for exclusive access and might still update their target memory locations regardless of their associated exclusive responses.

- **[High Level System Address Map](/documentation/102803/0000/Programmers-model/System-Memory-Map-overview/High-Level-System-Address-Map?lang=en)**
   Security values do not define privileged or unprivileged accessibility. These are defined by the PPC, or by the register blocks that is mapped to each area. See lower-level details of each area for details.
