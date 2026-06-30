# GICR_TYPER, Redistributor Type Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register>

### GICR\_TYPER, Redistributor Type Register

This register returns information about the features that this Redistributor supports.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [Redistributor registers for control and physical LPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en "The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_TYPER bit assignments

![GICR_TYPER bit assignments](images/0126-GICR_TYPER-Redistributor-Type-Register-img01.svg)

In the following table, the View column is applicable only for GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1.



<table id="kug1489160994724__tbl.gicr_typer_bit_assignments_with_view">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_TYPER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d28415e146" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d28415e149" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d28415e152" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d28415e155" rowspan="1">View</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">AffinityValue</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity level values for this Redistributor:

          <dl>
<dt class="documents-dlterm">
             Bits[63:56], Aff3

           </dt>
<dd>
             The affinity level 3 value.

           </dd>
<dt class="documents-dlterm">
             Bits[55:48], Aff2

           </dt>
<dd>
             The affinity level 2 value.

           </dd>
<dt class="documents-dlterm">
             Bits[47:40], Aff1

           </dt>
<dd>
             The affinity level 1 value.

           </dd>
<dt class="documents-dlterm">
             Bits[39:32], Aff0

           </dt>
<dd>
             The affinity level 0 value.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:27]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPInum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indicates the maximum PPI INTID that <span class="documents-keyword">GIC-720AE</span> supports:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00000</span>
</dt>
<dd>
             Maximum PPI INTID is 31.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00001</span>
</dt>
<dd>
             Maximum PPI INTID is 1087.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[26]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indicates whether this Redistributor supports direct injection of SGIs:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             This Redistributor does not support direct injection of SGIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             This Redistributor supports direct injection of SGIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[25:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CommonLPIAff</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             Single chip configuration.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             If chip set by Aff3.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             If chip set by Aff2.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             Reserved.

           </dd>
</dl> <p>Redistributors that belong to the same CommonLPIAff group must point at the same copy of the vPE Configuration table.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ProcessorNumber</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns the core number and chip number that uniquely identifies this core in the system.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RVPEID</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The GICR_VPENDBASER register does not record the index into the vPE Configuration table. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The GICR_VPENDBASER register records the index into the vPE Configuration table. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPAM</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indicates whether <span class="documents-keyword">GIC-720AE</span> supports Memory Partitioning and Monitoring (MPAM):

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             MPAM is not supported.

            <span> This value occurs when <code class="documents-parmname">lpi_support</code> == 0.</span>
</dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             MPAM is supported. This value occurs when

            <code class="documents-parmname">lpi_support</code> == 1.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DPGS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns 1, to indicate that the <span class="documents-keyword">GIC-720AE</span> supports Disable Processor Group Selections. See <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a>.DPG1S, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a>.DPG1NS, and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a>.DPG0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Last</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Last Redistributor:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             This Redistributor is not the last Redistributor on the chip.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             This Redistributor is the last Redistributor on the chip. When

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.VIEW == 1, for views 1, 2, or 3 this bit always returns 1.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DirectLPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns 0, to indicate that:

          <ul>
<li>The GICR_INVLPIR, GICR_INVALLR, and GICR_SYNCR registers are implemented.</li>
<li>The GICR_SETLPIR and GICR_CLRLPIR are not implemented.</li>
</ul> <p>The GICR_INVLPIR and GICR_INVALLR are present in all configurations of the GIC that support LPIs.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Dirty</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No vLPI support. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The Redistributor sets the state of GICR_VPENDBASER.Dirty after GICR_VPROPBASER.Valid is set to 1. After every residency change, software must poll for GICR_VPENDBASER.Dirty == 0. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VLPIS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indicates whether the Redistributor supports virtual LPIs:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The Redistributor does not support virtual LPIs or the direct injection of virtual LPIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The Redistributor supports virtual LPIs and the direct injection of virtual LPIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> <p>See the <a href="https://developer.arm.com/documentation/107627/latest" target="_blank"><span><cite>Learn the architecture - Generic Interrupt Controller v3 and v4, Virtualization</cite></span></a>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PLPIS</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Indicates whether the Redistributor supports physical LPIs:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The Redistributor does not support physical LPIs. This value occurs when

            <code class="documents-parmname">lpi_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The Redistributor supports physical LPIs. This value occurs when

            <code class="documents-parmname">lpi_support</code> == 1.

           </dd>
</dl> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">PE view 0, 1</td>
</tr>
</tbody>
</table>
