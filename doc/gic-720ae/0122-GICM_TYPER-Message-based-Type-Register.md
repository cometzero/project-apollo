# GICM_TYPER, Message-based Type Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register>

### GICM\_TYPER, Message-based Type Register

This register returns information about the number of SPIs that are assigned to the frame.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [Distributor registers (GICM) for message-based SPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary?lang=en "The functions for the GIC-720AE message-based SPIs are controlled through the Distributor registers identified with the prefix GICM.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICM\_TYPER bit assignments

![GICM_TYPER bit assignments](images/0122-GICM_TYPER-Message-based-Type-Register-img01.svg)



<table id="rqb1505904595701__tbl.GICM_TYPER_bit_assignments">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICM_TYPER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d34733e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d34733e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d34733e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 1 to indicate that the register reports information about the capabilities of the frame.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CLR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 1 to indicate that the GICM_CLRSPI registers are present.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the GICM_CLRSPI_SR and GICM_SETSPI_SR registers are present:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             GICM_CLRSPI_SR and GICM_SETSPI_SR registers are not present because

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a>.DS == 1.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             GICM_CLRSPI_SR and GICM_SETSPI_SR registers are present.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">INTID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The INTID of the lowest or first SPI that is assigned to the frame.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[10:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NumSPIS</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the number of SPIs that are assigned to the frame.<p>If the software is written for GICv2m, then we recommend setting <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" title="This register controls how interrupts are handled.">GICT_ERR&lt;n&gt;CTLR</a>.DIS_SPI_OOR to <span class="documents-g.number.bin">0b10</span> or <span class="documents-g.number.bin">0b01</span>. These values ensure that errors are not generated if software attempts to use the unimplemented SPI block with INTIDs 992-1023.</p> </td>
</tr>
</tbody>
</table>
