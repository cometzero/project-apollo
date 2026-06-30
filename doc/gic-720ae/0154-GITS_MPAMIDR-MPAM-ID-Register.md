# GITS_MPAMIDR, MPAM ID Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register>

### GITS\_MPAMIDR, MPAM ID Register

This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GITS\_PARTIDR.

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

Figure 1. GITS\_MPAMIDR bit assignments

![GITS_MPAMIDR bit assignments](images/0154-GITS_MPAMIDR-MPAM-ID-Register-img01.svg)



<table id="mjo1493722739946__tbl.gits_MPAMIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_MPAMIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d149110e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149110e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d149110e145" rowspan="1">Description</th>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Performance monitoring group. Returns <span>2<sup><code class="documents-parmname">pmg_width</code></sup> − 1</span>, and indicates the maximum value that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" title="This register sets the Partition ID and PMG values that the ITS uses during memory accesses.">GITS_PARTIDR</a>.PMG can be set to.<span> <code class="documents-parmname"> pmg_width</code> is a configuration parameter.</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PARTIDmax</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns <span>2<sup><code class="documents-parmname">partid_width</code></sup> − 1</span>, and indicates the maximum value that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" title="This register sets the Partition ID and PMG values that the ITS uses during memory accesses.">GITS_PARTIDR</a>.PARTID can be set to.<span> <code class="documents-parmname"> partid_width</code> is a configuration parameter.</span></td>
</tr>
</tbody>
</table>
