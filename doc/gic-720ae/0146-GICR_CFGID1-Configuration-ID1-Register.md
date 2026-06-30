# GICR_CFGID1, Configuration ID1 Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register>

### GICR\_CFGID1, Configuration ID1 Register

This register returns information about the configuration of the Redistributors.

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

Figure 1. GICR\_CFGID1 bit assignments

![GICR_CFGID1 bit assignments](images/0146-GICR_CFGID1-Configuration-ID1-Register-img01.svg)



<table id="vfi1469523982487__tbl.gicr_cfgid1">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_CFGID1 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d127309e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d127309e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d127309e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Version</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Identifies the major and minor revisions of <span class="documents-keyword">GIC-720AE</span>:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x0</span>
</dt>
<dd>
             r0p0

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x1</span>
</dt>
<dd>
             r0p1

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x2</span>
</dt>
<dd>
             r1p0

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x3</span>
</dt>
<dd>
             r2p0

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x4</span>
</dt>
<dd>
             r2p1

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UserValue</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Modification value that you can set. Indicates whether the customer has modified the behavior of the Redistributor. Usually, this field is <span class="documents-g.number.hex">0x0</span>. Customers change this value when they make authorized modifications to the Redistributor.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPIs_per_Processor</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of PPIs for each core. The possible values are:

          <ul>
<li><span class="documents-g.number.bin">0b0001_0000</span>, 16 PPIs</li>
<li><span class="documents-g.number.bin">0b0010_0000</span>, 32 PPIs</li>
<li><span class="documents-g.number.bin">0b0011_0000</span>, 48 PPIs</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">NumCPUs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of cores that this Redistributor supports.<p><span class="documents-keyword">GIC-720AE</span> supports up to 64 cores, so the maximum value of this field is <span class="documents-g.number.hex">0x3F</span>.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[3:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
</tbody>
</table>
