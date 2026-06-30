# Removing cores from a preconfigured GIC

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC>

### Removing cores from a preconfigured GIC

The GIC can be configured to either enable Secure software or a tie-off signal to remove cores from a GIC configuration. This feature enables you to use a single GIC configuration in multiple products that contain a different number of cores.

The `prog_mpidr` configuration parameter controls whether software or hardware can remove cores from a GIC configuration.

### Software control, when `prog_mpidr` `== prog`

This `prog_mpidr` setting enables Secure software to remove cores during the boot up of a system. If [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.").DS == 1, then Non-secure software can remove cores. If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then only view 0 has access to perform the necessary changes. The software flow is:

1. Software checks if [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").RDC == 1. When set to 1, it confirms that software can remove cores from the configuration.
2. Software writes to [GICD\_RDOFFR`n`](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") and sets a bit to 1 to remove that core from the configuration. `n` has a value of 0-7 and each value represents 64 cores. For example, to remove:
   - The 1st core, set GICD\_RDOFFR0[0] to 1.
   - The 22nd core, set GICD\_RDOFFR0[21] to 1.
   - The 72nd core, set GICD\_RDOFFR1[7] to 1.

   When cores are removed, the affinity values of the remaining cores automatically change, so software must then program [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor."). See [Requirement to program GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en#dsb1505904597662__example.program_gicr_mpidr_example). Software must ensure writes to [GICD\_RDOFF<n>](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") have completed before issuing subsequent accesses to the GIC. This can be achieved with a DSB.
3. Software writes to each [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor.") to set the affinity values for the cores on that Redistributor. The address map for these Redistributors is now a single contiguous block of Redistributor address space.
4. Software can then start normal operation.
   > ### Note
   >
   > Software must program the
   > [GICD\_RDOFFR`n`](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") and
   > [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor.") registers before any other GIC registers are accessed (other than reads to
   > [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.") and read-only ID registers) and before the GIC receives messages from any cores. Otherwise the behavior is unpredictable.

### Example 1. Requirement to program GICR\_MPIDR

When software uses [GICD\_RDOFFR`n`](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") to remove a core, the following core in the sequence then effectively inherits the affinity settings of the removed core. The following example shows the importance of the subsequent programming of the [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor.") registers.

In this example, there are 4 Redistributors with the following affinity values:

Redistributor 0
:   0.0.0.0, physical PE 0

Redistributor 1
:   0.1.0.0, physical PE 1

Redistributor 2
:   0.2.0.0, physical PE 2

Redistributor 3
:   0.2.1.0, physical PE 3

If software writes 0x2 to [GICD\_RDOFFR0](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC."), it removes PE 1 and its Redistributor, and the affinity values for the remaining Redistributors are:

Redistributor 0
:   0.0.0.0, physical PE 0

Redistributor 1
:   0.1.0.0, physical PE 2

Redistributor 2
:   0.2.0.0, physical PE 3

The original Redistributor 2 and Redistributor 3 are now in separate clusters, but previously they were in the same cluster. Therefore, to retain the intended heirarchy, software must also program the [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor.") registers.

### Hardware control, when `prog_mpidr` `== strap`

This `prog_mpidr` setting enables hardware to remove cores as the GIC exits reset. With this option, the software is unaware that the GIC is supporting fewer cores than the configuration allows.

This option provides the following extra tie-off signals:

gicd\_pe\_off[max\_pe\_on\_chip − 1:0]
:   Set a bit to 1, to remove the corresponding core. The behavior is unpredictable when all bits are set to 1.

affinity0[(max\_pe\_on\_chip × max\_affinity\_width0) − 1:0]
:   Sets the affinity 0 value for each core.

affinity1[(max\_pe\_on\_chip × max\_affinity\_width1) − 1:0]
:   Sets the affinity 1 value for each core.

affinity2[(max\_pe\_on\_chip × max\_affinity\_width2) − 1:0]
:   Sets the affinity 2 value for each core.

affinity3[(max\_pe\_on\_chip × max\_affinity\_width3) − 1:0]
:   Sets the affinity 3 value for each core.

> ### Note
>
> These tie-off signals must be set before the GIC is taken out of reset and must remain stable, otherwise the behavior is unpredictable. If the width of the signal is zero, then it is not present on the GIC instance.

The bit order in these tie-off signals is the order that the Redistributor pages appear in the default GIC address map, as defined by the order of GCI blocks and buses within them. These values are set by the `ppi_ref` and `bus` parameters in the configuration file, that is, there is a fixed relationship between the tie-off signal and a physical processor.

### Example 2. Example of removing cores from a 4-core configuration

This 4-core example has affinity 0, 1, and 2 with a width of 2 bits:

Core 0
:   MPIDR 0.0.0.0

Core 1
:   MPIDR 0.0.0.1

Core 2
:   MPIDR 0.0.1.0

Core 3
:   MPIDR 0.0.1.1

The following table shows the tie-off signal values when core 1 is removed and also when core 0 and core 2 are removed.



<table id="dsb1505904597662__table_w2740ab1b7b9b9_w2741ab1b7b9_w2742ab1b7_w2743ab1">
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d98995e498" rowspan="1">Signal</th>
<th class="documents-nocellnorowborder" colspan="1" id="d98995e501" rowspan="1">No cores removed</th>
<th class="documents-nocellnorowborder" colspan="1" id="d98995e504" rowspan="1">Core 1 removed</th>
<th class="documents-cell-norowborder" colspan="1" id="d98995e507" rowspan="1">Core 0 and 2 removed<p>Core 1 in each cluster moved to 0</p> </th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">gicd_pe_off</span></span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b0000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b0010</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b0101</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">affinity0</span></span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b01_00_01_00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b01_00_xx_00</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b00_xx_00_xx</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">affinity1</span></span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b01_01_00_00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b01_01_xx_00</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b01_xx_00_xx</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">affinity2</span></span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b00_00_00_00</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b00_00_xx_00</span></td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><span class="documents-g.number.bin">0b00_xx_00_xx</span></td>
</tr>
</tbody>
</table>



When cores are removed by setting bits of the gicd\_pe\_off signal, the GICD updates other software-visible features so that software cannot detect the reduced core count. These updates include:

- Moving [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.").Last to the last Redistributor.
- Moving the GICDA register page to the page above the last Redistributor.

### Limitations

The removal of cores from a configuration, by software or hardware, has the following limitations:

GICR\_CFGID0.PPI\_number
:   This field reflects a tie-off on the
    GIC Cluster Interface (GCI). The system integrator must change the tie-off as required. The tie-off has no function other than implementation-defined discovery, so the tie-offs could all be tied to the same value.

FMU
:   The removal of cores does not change the
    protection mechanism mappings in the FMU. Therefore, the firmware that accesses the APB interface must know the full structure of the GIC configuration, especially if all cores on a particular
    GCI or CPUIF protection block are removed.

MBIST
:   The GIC does not alter the MBIST interface, so the system integrator must add any protection that is required.

Removed cores
:   If cores are removed, then the behavior is unpredictable if the GIC receives GIC Stream messages from a removed core.

[GICR<n>\_ERRINSR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ERRINSR--Error-Insertion-Register?lang=en "This register can inject errors into the PPI RAM. You can use this register to test your error recovery software.")
:   These registers are used for inserting errors, so that software can check the ECC operation on the RAMs in the
    GCI block.

    However, if cores are removed then these registers are not updated. Therefore, when some, but not all, cores are removed from a cluster interface, the GIC reports errors only in the RAS records of the available cores. This behavior provides a mechanism for software to determine which cores are removed.
