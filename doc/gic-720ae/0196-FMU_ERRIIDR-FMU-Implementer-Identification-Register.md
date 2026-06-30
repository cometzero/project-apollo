# FMU_ERRIIDR, FMU Implementer Identification Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRIIDR--FMU-Implementer-Identification-Register>

### FMU\_ERRIIDR, FMU Implementer Identification Register

This register provides information about the implementer and revision of the FMU.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. FMU\_ERRIIDR bit assignments

![FMU_ERRIIDR bit assignments](images/0196-FMU_ERRIIDR-FMU-Implementer-Identification-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_ERRIIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d154544e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d154544e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d154544e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ProductID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the part number of the component:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x49A</span>
</dt>
<dd>
<span class="documents-keyword">GIC-720AE</span> FMU

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Variant</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the major revision, or variant, of the FMU:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x0</span>
</dt>
<dd>
             r0

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Revision</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the minor revision of the FMU:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x0</span>
</dt>
<dd>
             p0

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[11:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Implementer</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Identifies the implementer:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x43B</span>
</dt>
<dd>
<span class="documents-keyword">Arm</span>
</dd>
</dl> </td>
</tr>
</tbody>
</table>
