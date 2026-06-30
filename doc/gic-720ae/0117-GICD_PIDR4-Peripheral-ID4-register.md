# GICD_PIDR4, Peripheral ID4 register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register>

### GICD\_PIDR4, Peripheral ID4 register

This register returns byte[4] of the peripheral ID. The GICD\_PIDR4 register is part of the set of Distributor peripheral identification registers.

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

Figure 1. GICD\_PIDR4 bit assignments

![GICD_PIDR4 bit assignments](images/0117-GICD_PIDR4-Peripheral-ID4-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_PIDR4 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d54535e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d54535e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d54535e136" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SIZE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns <span class="documents-g.number.hex">0x4</span>, which indicates that the Distributor occupies 64KB of memory, (2<sup>SIZE</sup> × 4KB).</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[3:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">DES_2</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns <span class="documents-g.number.hex">0x4</span>, which represents bits[10:7] of the JEDEC JEP106 identification code. Together, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" title="This register returns byte[1] of the peripheral ID. The GICD_PIDR1 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR1</a>.DES_0, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICD_PIDR2 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR2</a>.DES_1, and DES_2 identify the component designer.</td>
</tr>
</tbody>
</table>
