# GITS_MPIDR, ITS Affinity Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register>

### GITS\_MPIDR, ITS Affinity Register

This register returns the ITS affinity when the vPE table is shared with Redistributors.

### Configurations

When `gicv41_support` == 1, this register is available in all configurations that have one or more ITS blocks.

### Attributes

Width
:   32-bit

Functional group
:   See
    [ITS control register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en "The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GITS\_MPIDR bit assignments

![GITS_MPIDR bit assignments](images/0156-GITS_MPIDR-ITS-Affinity-Register-img01.svg)



<table id="hlc1478966338385__tbl.gits_MPIDR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_MPIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d172714e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d172714e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d172714e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Aff3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The Affinity level 3 value for the ITS.<span> The value of this field depends on the value of the <code class="documents-parmname">﻿chip_affinity_select_level</code> configuration parameter. If <code class="documents-parmname">﻿chip_affinity_select_level</code> is set to:</span>
<ul>
<li>2, this field returns zero.</li>
<li>3, this field returns the value of the ﻿<span class="documents-g.signal.name"><span class="documents-keyword">chip_id</span></span> signal.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Aff2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The Affinity level 2 value for the ITS.<span> The value of this field depends on the value of the <code class="documents-parmname">﻿chip_affinity_select_level</code> configuration parameter. If <code class="documents-parmname">﻿chip_affinity_select_level</code> is set to:</span>
<ul>
<li>2, this field returns the value of the ﻿<span class="documents-g.signal.name"><span class="documents-keyword">chip_id</span></span> signal.</li>
<li>3, this field returns zero.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Aff1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The Affinity level 1 value for the ITS. Returns zero.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
</tbody>
</table>
