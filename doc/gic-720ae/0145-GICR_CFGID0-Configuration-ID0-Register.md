# GICR_CFGID0, Configuration ID0 Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID0--Configuration-ID0-Register>

### GICR\_CFGID0, Configuration ID0 Register

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

Figure 1. GICR\_CFGID0 bit assignments

![GICR_CFGID0 bit assignments](images/0145-GICR_CFGID0-Configuration-ID0-Register-img01.svg)



<table id="xdt1469520331259__tbl.gicr_cfgid0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_CFGID0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d50986e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d50986e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d50986e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ECCSupport</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>1 = ECC is supported</span>.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[8:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PPINumber</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RedistributorID.<p>The <span class="documents-g.signal.name"><span class="documents-keyword">ppi_id[15:0]</span></span> tie-off signal sets the value of the ID. Each Redistributor must have a unique ID.</p> </td>
</tr>
</tbody>
</table>
