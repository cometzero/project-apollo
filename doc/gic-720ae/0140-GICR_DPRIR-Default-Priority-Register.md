# GICR_DPRIR, Default Priority Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-DPRIR--Default-Priority-Register>

### GICR\_DPRIR, Default Priority Register

This register controls the default priority of errored interrupts.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, this register is banked for each view.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for SGIs and PPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en "The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_DPRIR bit assignments

![GICR_DPRIR bit assignments](images/0140-GICR_DPRIR-Default-Priority-Register-img01.svg)



<table id="fpn1489160399734__tbl.gicr_dprir">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_DPRIR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d99815e146" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d99815e149" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d99815e152" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:19]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">G1SPRI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The default priority that the GIC uses for errored Secure Group 1 interrupts. Lower priority values correspond to greater priority of the interrupt. Only Secure writes can update this field.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[18:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">G1NSPRI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The default priority that the GIC uses for errored Non-secure Group 1 interrupts. Lower priority values correspond to greater priority of the interrupt.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[10:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">G0PRI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The default priority that the GIC uses for errored Group 0 interrupts. Lower priority values correspond to greater priority of the interrupt. Only Secure writes can update this field.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[2:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
</tbody>
</table>



### Accessibility

Some fields are writable only by using a Secure access.
