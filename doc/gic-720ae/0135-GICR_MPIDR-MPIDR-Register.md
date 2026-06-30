# GICR_MPIDR, MPIDR Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register>

### GICR\_MPIDR, MPIDR Register

This register allows Secure software to write the affinity values of a Redistributor.

### Configurations

This register is available in configurations when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").RDC == 1.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for control and physical LPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en "The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.") for the address offset, type, and reset value of this register.

### Usage constraints

Software must program this register after it writes to the [GICD\_RDOFFRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") registers and before the GIC receives messages from any processors or any other register accesses. Otherwise the behavior is unpredictable.

Programming of GICR\_MPIDR must be unique for each Redistributor. If multi view is supported, that is [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then GICR\_MPIDR needs to be unique only within the view.

### Bit descriptions

Figure 1. GICR\_MPIDR bit assignments

![GICR_MPIDR bit assignments](images/0135-GICR_MPIDR-MPIDR-Register-img01.svg)



<table id="yxb1505904595145__tbl.GICR_MPIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_MPIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d87310e169" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d87310e172" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d87310e175" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the affinity level 3 value of this Redistributor.<p>The <code class="documents-parmname">max_affinity_width3</code> configuration parameter controls how many of the lower bits are implemented. This field ignores writes <span>for cross-chip configurations or </span>when <code class="documents-parmname">max_affinity_width3</code> is zero.</p> <p>Software can use <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.AffinityValue to read the affinity level 3 value.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the affinity level 2 value of this Redistributor.<p>The <code class="documents-parmname">max_affinity_width2</code> configuration parameter controls how many of the lower bits are implemented. This field ignores writes <span>for cross-chip configurations with chip affinity level 2 or </span>when <code class="documents-parmname">max_affinity_width2</code> is zero.</p> <p>Software can use <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.AffinityValue to read the affinity level 2 value.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the affinity level 1 value of this Redistributor.<p>The <code class="documents-parmname">max_affinity_width1</code> configuration parameter controls how many of the lower bits are implemented. This field ignores writes when <code class="documents-parmname">max_affinity_width1</code> is zero.</p> <p>Software can use <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.AffinityValue to read the affinity level 1 value.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Affinity0</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the affinity level 0 value of this Redistributor.<p>The <code class="documents-parmname">max_affinity_width0</code> configuration parameter controls how many of the lower bits are implemented. This field ignores writes when <code class="documents-parmname">max_affinity_width0</code> is zero.</p> <p>Software can use <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.AffinityValue to read the affinity level 0 value.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_MPIDR is accessible only by Secure accesses.

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then GICR\_MPIDR is accessible only for view 0.
