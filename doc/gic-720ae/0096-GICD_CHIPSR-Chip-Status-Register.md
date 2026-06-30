# GICD_CHIPSR, Chip Status Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register>

### GICD\_CHIPSR, Chip Status Register

This register returns the status of the chip in a multichip configuration. A single copy of this register exists on each chip in a multichip configuration.

### Configurations

This register is available in all multichip configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_CHIPSR bit assignments

![GICD_CHIPSR bit assignments](images/0096-GICD_CHIPSR-Chip-Status-Register-img01.svg)



<table id="col1468500451720__tbl.gicd_chipsr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_CHIPSR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d90863e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d90863e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d90863e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0                                           </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Ongoing SPI-related cross-chip traffic.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             No traffic.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Ongoing SGI-related traffic or not all cores are asleep.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             No traffic.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Ongoing LPI-related traffic.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             No traffic.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CC_busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Ongoing cross-chip traffic.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             No traffic.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RTS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Routing table status:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             Disconnected.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             Updating.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             Consistent.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             Reserved.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GTO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Gating transaction ongoing:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No accesses.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Accesses ongoing.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GTS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Gating status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Not gated.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Gated

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_CHIPSR is accessible only by Secure reads.
