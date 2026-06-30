# GICR_SGIDR, SGI Default Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-SGIDR--SGI-Default-Register>

### GICR\_SGIDR, SGI Default Register

This register controls the default value of SGI settings, for use in the case of a Double-bit Error Detect Error (DEDERR).

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, this register is banked for each view.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [Redistributor registers for SGIs and PPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en "The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions



<table id="zwq1469461703668__tbl.gicr_sgidr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_SGIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d70531e141" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d70531e144" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d70531e147" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3] + 4n:<p>[63, 59, 55, 51, 47, 43, 39, 35, 31, 27, 23, 19, 15, 11, 7, 3]</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2] + 4n:<p>[62, 58, 54, 50, 46, 42, 38, 34, 30, 26, 22, 18, 14, 10, 6, 2]</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GRPMOD</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">As GICR_IGRPMODR0 register.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1] + 4n:<p>[61, 57, 53, 49, 45, 41, 37, 33, 29, 25, 21, 17, 13, 9, 5, 1]</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GRP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">As GICR_IGROUPR0 register.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0] + 4n:<p>[60, 56, 52, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0]</p> </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NSACR</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">1 = Allow Non-secure access to interrupt &lt;n&gt;.</td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_SGIDR is accessible only by Secure accesses.
