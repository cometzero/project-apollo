# GICD_PIDR1, Peripheral ID1 register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register>

### GICD\_PIDR1, Peripheral ID1 register

This register returns byte[1] of the peripheral ID. The GICD\_PIDR1 register is part of the set of Distributor peripheral identification registers.

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

Figure 1. GICD\_PIDR1 bit assignments

![GICD_PIDR1 bit assignments](images/0120-GICD_PIDR1-Peripheral-ID1-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_PIDR1 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d59047e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59047e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d59047e136" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DES_0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns <span class="documents-g.number.hex">0xB</span>, which represents bits[3:0] of the JEDEC JEP106 identification code. Together, DES_0, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICD_PIDR2 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR2</a>.DES_1, and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" title="This register returns byte[4] of the peripheral ID. The GICD_PIDR4 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR4</a>.DES_2 identify the component designer.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[3:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PART_1</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns <span class="documents-g.number.hex">0x4</span>, which represents bits[11:8] of the 12-bit part number of the Distributor. Together, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" title="This register returns byte[0] of the peripheral ID. The GICD_PIDR0 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR0</a>.PART_0 and PART_1 field values indicate the part number of the Distributor.</td>
</tr>
</tbody>
</table>
