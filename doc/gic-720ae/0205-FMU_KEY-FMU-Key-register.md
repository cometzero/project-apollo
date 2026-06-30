# FMU_KEY, FMU Key register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-KEY--FMU-Key-register>

### FMU\_KEY, FMU Key register

This register receives the unlock key that is required for writes to FMU registers to be successful. This register reads as 0 if the FMU register file is locked.

Software does not need to write to FMU\_KEY when it performs FMU reads.

To handle 64-bit write accesses to 64-bit RAS registers, the key register is not affected by writes to the upper 32 bits of a 64-bit RAS register. This design functionality copes with the situation where an APB bridge reverses the order of the two 32-bit writes in a 64-bit write access.

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

Figure 1. FMU\_KEY bit assignments

![FMU_KEY bit assignments](images/0205-FMU_KEY-FMU-Key-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_KEY bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d27463e145" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d27463e148" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d27463e151" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">KEY</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Writing the correct key to this field enables the next write to any other writable FMU register to succeed. The register file is unlocked when a write to FMU_KEY occurs that satisfies all the following conditions:

          <ul>
<li>Is Secure.</li>
<li>Is for 32 bits.</li>
<li>Bits[7:0] are <span class="documents-g.number.hex">0xBE</span>.</li>
</ul> <p>If the register file is unlocked, the FMU_KEY register reads as <span class="documents-g.number.hex">0x000000BE</span>. Otherwise, the FMU_KEY register reads as <span class="documents-g.number.hex">0x00000000</span>.</p> <p>The FMU_KEY register automatically locks after any Secure write access with correct strobes, even if the write is ignored. For example, the write might be ignored if it accesses an invalid address. The only exception is writing to the upper 32 bits of the 64-bit RAS registers, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" title="For even error records, this register controls whether the FMU can generate a critical error interrupt. For odd error records, this register controls whether the FMU can generate an error recovery interrupt. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR&lt;n&gt;CTLR</a> and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS</a>.</p> <p>See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" title="The FMU registers are protected against inadvertent writes by a lock and key mechanism.">Lock and key mechanism</a>.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_KEY is accessible only by Secure accesses.
