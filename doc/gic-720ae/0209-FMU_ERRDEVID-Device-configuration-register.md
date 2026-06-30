# FMU_ERRDEVID, Device configuration register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRDEVID--Device-configuration-register>

### FMU\_ERRDEVID, Device configuration register

This register returns the number of error records in the FMU.

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

Figure 1. FMU\_ERRDEVID bit assignments

![FMU_ERRDEVID bit assignments](images/0209-FMU_ERRDEVID-Device-configuration-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_ERRDEVID bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d86623e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d86623e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d86623e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NUM</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">This field returns <span class="documents-g.number.hex">0x000C</span> because the FMU has 12 error records. The <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" title="This register shows the status of all FMU_ERR&lt;n&gt;STATUS.V bits.">FMU_ERRGSR</a> effectively lists the error records, 0-11, and the block a record associates with.</td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_ERRDEVID is accessible only by Secure accesses.
