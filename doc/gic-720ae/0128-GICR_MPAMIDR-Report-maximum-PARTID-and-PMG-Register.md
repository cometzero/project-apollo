# GICR_MPAMIDR, Report maximum PARTID and PMG Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register>

### GICR\_MPAMIDR, Report maximum PARTID and PMG Register

This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR\_PARTIDR.

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

Figure 1. GICR\_MPAMIDR bit assignments

![GICR_MPAMIDR bit assignments](images/0128-GICR_MPAMIDR-Report-maximum-PARTID-and-PMG-Register-img01.svg)



<table id="slh1497365528824__tbl.gicr_MPAMIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_MPAMIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d7264e137" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d7264e140" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d7264e143" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PMGmax</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>Performance monitoring group. Returns <span>2<sup><code class="documents-parmname">pmg_width</code></sup> − 1</span>, and indicates the maximum value that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" title="This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.">GICR_PARTIDR</a>.PMG can be set to.</span><span> <code class="documents-parmname"> pmg_width</code> is a configuration parameter.</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PARTIDmax</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><span>Returns <span>2<sup><code class="documents-parmname">partid_width</code></sup> − 1</span>, and indicates the maximum value that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" title="This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.">GICR_PARTIDR</a>.PARTID can be set to.</span><span> <code class="documents-parmname"> partid_width</code> is a configuration parameter.</span></td>
</tr>
</tbody>
</table>
