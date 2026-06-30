# GICT_ERR<n>FR, Error Record Feature Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-FR--Error-Record-Feature-Register>

### GICT\_ERR<n>FR, Error Record Feature Register

This register returns information about the Armv8.2 RAS features that the GIC-720AE implements.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICT\_ERR<n>FR bit assignments

![GICT_ERR<n>FR bit assignments](images/0165-GICT_ERR-n-FR-Error-Record-Feature-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERR&lt;n&gt;FR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d159228e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d159228e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d159228e142" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Repeat corrected error count:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not implement a repeat corrected error counter.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CEC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Corrected error count:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b000</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not implement a standard corrected error counter in

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.">GICT_ERR&lt;n&gt;MISC0</a>.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11:10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CFI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Corrected errors fault interrupt. Depending on the configuration, returns either:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not provide a fault handling interrupt for corrected errors.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> provides a controllable fault handling interrupt for corrected errors.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrected error. Depending on the configuration, returns either:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not provide an in-band uncorrected error reporting.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> provides a controllable in-band uncorrected error reporting.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Fault handling interrupt for uncorrected errors. Depending on the configuration, returns either:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not provide a fault handling interrupt.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> provides a controllable fault handling interrupt.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error recovery interrupt for uncorrected errors. Depending on the configuration, returns either:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not provide an error recovery interrupt for uncorrected errors.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> provides a controllable error recovery interrupt for uncorrected errors.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3:2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Deferring of errors support:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not support the deferring of errors.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[1:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ED</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Uncorrected error reporting:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             Uncorrected error reporting is always enabled.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERR<n>FR is accessible only by Secure accesses.
