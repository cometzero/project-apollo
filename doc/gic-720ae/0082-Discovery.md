# Discovery

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages/Discovery>

### Discovery

We recommend that the operating system is provided with pointers to the start of the Distributor, every ITS, and the first Redistributor page on each chip.

To verify that the pages relate to GIC registers, software can check these pointers against the discovery registers, which start at offset 0xFFD0 for each GIC page. These registers allow discovery of the architecture version and, for GIC-720AE, whether the page contains the Distributor, ITS, or Redistributor registers. For example, to discover the page type, software can:

1. Read from 0xFFE0 to determine the PIDR0.PART\_0 value.
2. Read from 0xFFE4 to determine the PIDR1.PART\_1 value.
3. Concatenate PART\_1 (4 bits) and PART\_0 (8 bits), to discover the 12-bit part number, PART\_1||PART\_0. A value of:
   - 0x492 indicates that this page contains Distributor registers.
   - 0x493 indicates that this page contains Redistributor registers.
   - 0x494 indicates that this page contains ITS registers.

When this information is known, software can obtain additional information from registers that are specific to each page.

For Redistributors, we recommend that you examine [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.") to determine:

- Whether the implementation has 2 or 4 pages for each Redistributor, which depends on the features implemented. It can be inferred that GIC-720AE has 4 pages for each Redistributor because the [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.").VLPIS bit indicates that it supports virtual LPIs.
- Whether it is the last Redistributor in the series of pages. However, if [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then it applies only for view 0 because [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.").Last == 1 for views 1, 2, and 3.
- Which core the Redistributor is for, based on affinity values.

This information allows you to iteratively search through all Redistributors in a discovery process.

The [GITS\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en "This register returns information about the features that this ITS supports.") register in the GIC-720AE indicates that you must program the ITS with unique ProcessorNumbers, instead of physical target addresses. The [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.") contains the unique ProcessorNumber that you must use to reference a Redistributor when programming the ITS.

> ### Note
>
> In a multichip configuration, the ProcessorNumber upper bits are derived from the
> chip\_id tie-off signal. Therefore, the
> chip\_id signal value must be set before the GIC exits from reset.

For more information, see the [Learn the architecture - Generic Interrupt Controller v3 and v4, Overview](https://developer.arm.com/documentation/198123/latest).
