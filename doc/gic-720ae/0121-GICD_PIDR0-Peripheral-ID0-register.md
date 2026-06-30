# GICD_PIDR0, Peripheral ID0 register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register>

### GICD\_PIDR0, Peripheral ID0 register

This register returns byte[0] of the peripheral ID. The GICD\_PIDR0 register is part of the set of Distributor peripheral identification registers.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_PIDR0 bit assignments

![GICD_PIDR0 bit assignments](images/0121-GICD_PIDR0-Peripheral-ID0-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_PIDR0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d51206e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d51206e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d51206e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PART_0</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns <span class="documents-g.number.hex">0x92</span>, which represents bits[7:0] of the 12-bit part number of the Distributor. Together, PART_0 and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" title="This register returns byte[1] of the peripheral ID. The GICD_PIDR1 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR1</a>.PART_1 field values indicate the part number of the Distributor.</td>
</tr>
</tbody>
</table>
