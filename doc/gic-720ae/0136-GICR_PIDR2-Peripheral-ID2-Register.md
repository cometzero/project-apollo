# GICR_PIDR2, Peripheral ID2 Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PIDR2--Peripheral-ID2-Register>

### GICR\_PIDR2, Peripheral ID2 Register

This register returns byte[2] of the peripheral ID. The GICR\_PIDR2 register is part of the set of Redistributor peripheral identification registers.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for control and physical LPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en "The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_PIDR2 bit assignments

![GICR_PIDR2 bit assignments](images/0136-GICR_PIDR2-Peripheral-ID2-Register-img01.svg)



<table id="aba1434365495970__table.1">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_PIDR2 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d84658e132" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d84658e135" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d84658e138" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ArchRev</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Identifies the version of the GIC architecture with which the Redistributor complies:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x3</span>
</dt>
<dd>
             GICv3

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x4</span>
</dt>
<dd>
             GICv4

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">JEDEC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates that a JEDEC-assigned JEP106 identity code is used.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[2:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">DES_1</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Bits[6:4] of the JEP106 identity code. Bits[3:0] of the JEP106 identity code are assigned to GICR_PIDR1[7:4].</td>
</tr>
</tbody>
</table>
