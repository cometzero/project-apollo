# GITS_PARTIDR, PART ID Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register>

### GITS\_PARTIDR, PART ID Register

This register sets the Partition ID and PMG values that the ITS uses during memory accesses.

### Configurations

This register is available in all configurations that have one or more ITS blocks.

### Attributes

Width
:   32-bit

Functional group
:   See
    [ITS control register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en "The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GITS\_PARTIDR bit assignments

![GICR_PARTIDR bit assignments](images/0155-GITS_PARTIDR-PART-ID-Register-img01.svg)



<table id="frx1493722825190__tbl.gits_PARTIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_PARTIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d14866e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d14866e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d14866e142" rowspan="1">Description</th>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The performance monitoring group value that the ITS uses when it accesses memory. The GIC allocates 8 bits for PMG, but <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GITS_PARTIDR.">GITS_MPAMIDR</a>.PMGmax controls the usable width of this field, so some upper bits might be RES0.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PARTID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">The Partition ID value that the ITS uses when it accesses memory. The GIC allocates 16 bits for PARTID, but <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GITS_PARTIDR.">GITS_MPAMIDR</a>.PARTIDmax controls the usable width of this field, so some upper bits might be RES0.</td>
</tr>
</tbody>
</table>
