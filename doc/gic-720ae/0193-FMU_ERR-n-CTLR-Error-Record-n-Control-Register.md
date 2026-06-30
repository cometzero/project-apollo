# FMU_ERR<n>CTLR, Error Record <n> Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register>

### FMU\_ERR<n>CTLR, Error Record <n> Control Register

For even error records, this register controls whether the FMU can generate a critical error interrupt. For odd error records, this register controls whether the FMU can generate an error recovery interrupt. GIC-720AE supports 12 error records, `n` = 0-11.

The value of
`n` maps to the following FMU error records:

n=0
:   GICD, critical error record

n=1
:   GICD, non-critical error record

n=2
:   Wake Request, critical error record

n=3
:   Wake Request, non-critical error record

n=4
:   SPI Collator, critical error record

n=5
:   SPI Collator, non-critical error record

n=6
:   GCI, critical error record

n=7
:   GCI, non-critical error record

n=8
:   ITS, critical error record

n=9
:   ITS, non-critical error record

n=10
:   FMU, critical error record

n=11
:   FMU, non-critical error record

If a GIC configuration contains a Wake Request block and the `wake_local` configuration parameter is set to 1, then the Wake Request is an integral part of the GICD. Therefore, the n=2 and n=3 records are not implemented.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. FMU\_ERR<n>CTLR bit assignments

![FMU_ERR<n>CTLR bit assignments](images/0193-FMU_ERR-n-CTLR-Error-Record-n-Control-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_ERR&lt;n&gt;CTLR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d104416e274" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d104416e277" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d104416e280" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Critical error interrupt enable. For even records:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The FMU does not generate critical error interrupts.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             When ED == 1, the FMU generates a critical error interrupt when a critical error condition occurs. See

            <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" title="This section describes how the GIC blocks can signal errors, and how the FMU reports these errors.">Error signaling</a> for more information.

           </dd>
</dl> <p>RAZ/WI for odd records.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WDUI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DUI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WCFI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CFI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WUE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WFI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WUI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Feature not supported, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">For odd records, this bit controls whether an Error Recovery Interrupt (ERI) is generated for errors that are reported through this error record:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The FMU does not generate an error recovery interrupt.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             When ED == 1, the FMU generates an error recovery interrupt for all errors that this odd error record reports. See

            <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" title="This section describes how the GIC blocks can signal errors, and how the FMU reports these errors.">Error signaling</a> for more information.

           </dd>
</dl> <p>RAZ/WI for even records.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">W_EN</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">If a fault causes the error record &lt;<code class="documents-option">n</code>&gt; input signal to assert permanently, software can use this bit to disable that error record input signal:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The error record &lt;

            <code class="documents-option">n</code>&gt; input signal is disabled.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The error record &lt;

            <code class="documents-option">n</code>&gt; input signal is enabled. This setting occurs at reset.

           </dd>
</dl> <p>The error record &lt;<code class="documents-option">n</code>&gt; input error signals are <span class="documents-g.signal.name"><span class="documents-keyword">cr_err_in_*</span></span> and <span class="documents-g.signal.name"><span class="documents-keyword">ncr_err_in_*</span></span>, where * is ci, its, wake, or spicol. The error record &lt;<code class="documents-option">n</code>&gt; input error signals for the GICD and FMU are not externally accessible.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ED</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Error reporting and logging enable:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Error reporting and logging is disabled for this record.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Error reporting and logging is enabled for this record. This setting occurs at reset.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_ERR<n>CTLR is accessible only by Secure accesses.
