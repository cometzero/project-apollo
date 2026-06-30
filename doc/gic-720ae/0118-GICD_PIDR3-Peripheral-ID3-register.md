# GICD_PIDR3, Peripheral ID3 register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR3--Peripheral-ID3-register>

### GICD\_PIDR3, Peripheral ID3 register

This register returns byte[3] of the peripheral ID. The GICD\_PIDR3 register is part of the set of Distributor peripheral identification registers.

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

Figure 1. GICD\_PIDR3 bit assignments

![GICD_PIDR3 bit assignments](images/0118-GICD_PIDR3-Peripheral-ID3-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_PIDR3 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d94439e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d94439e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d94439e136" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">REVAND</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates minor errata fixes specific to the revision of the component being used, for example metal fixes after implementation. <span class="documents-g.number.hex">0x0</span> indicates that there are no errata fixes to this component.<p><span class="documents-g.number.hex">0x0</span>.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[3:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CMOD</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Customer modified. Indicates whether the customer has modified the behavior of the component. Usually, this field is <span class="documents-g.number.hex">0x0</span>. Customers change this value when they make authorized modifications to this component.<p><span class="documents-g.number.hex">0x0</span>.</p> </td>
</tr>
</tbody>
</table>
