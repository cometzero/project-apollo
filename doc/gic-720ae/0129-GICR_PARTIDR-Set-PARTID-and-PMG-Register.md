# GICR_PARTIDR, Set PARTID and PMG Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register>

### GICR\_PARTIDR, Set PARTID and PMG Register

This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.

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

Figure 1. GICR\_PARTIDR bit assignments

![GICR_PARTIDR bit assignments](images/0129-GICR_PARTIDR-Set-PARTID-and-PMG-Register-img01.svg)



<table id="zcr1499093417801__tbl.gicr_PARTIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_PARTIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d95455e134" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d95455e137" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d95455e140" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PMG</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The performance monitoring group value that the Redistributor uses when it accesses memory. The GIC allocates 8 bits for PMG, but <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR_PARTIDR.">GICR_MPAMIDR</a>.PMGmax controls the usable width of this field, so some upper bits might be RES0.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PARTID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">The Partition ID value that the Redistributor uses when it accesses memory. The GIC allocates 16 bits for PARTID, but <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR_PARTIDR.">GICR_MPAMIDR</a>.PARTIDmax controls the usable width of this field, so some upper bits might be RES0.</td>
</tr>
</tbody>
</table>
