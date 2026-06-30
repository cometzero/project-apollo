# FMU_TIMEOUT, Timeout duration register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-TIMEOUT--Timeout-duration-register>

### FMU\_TIMEOUT, Timeout duration register

When FMU\_STATUS.BUSY == 1, this register controls the duration before the FMU sets FMU\_STATUS.TIMEOUT = 1.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

After a write to this register, poll [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").BUSY to ensure that the effect of the write is complete.

### Bit description

Figure 1. FMU\_TIMEOUT bit assignments

![FMU_TIMEOUT bit assignments](images/0206-FMU_TIMEOUT-Timeout-duration-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_TIMEOUT bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d98770e143" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d98770e146" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d98770e149" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">DURATION</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Timeout count duration in FMU clock cycles.<p>If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS</a>.BUSY asserts for longer than the value of this field, then an <span>AXI5-Stream</span> timeout occurs and the FMU sets:</p>
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS</a>.BUSY = 0</li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS</a>.TIMEOUT = 1</li>
</ul> When TIMEOUT == 1, the FMU stops waiting for the <span>AXI5-Stream</span> response, so software can then start a new <span>AXI5-Stream</span> request.<p>The initial value on reset is <span class="documents-g.number.hex">0xFFFFFFFF</span>, which provides the longest possible timeout allowed.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_TIMEOUT is accessible only by Secure accesses.
