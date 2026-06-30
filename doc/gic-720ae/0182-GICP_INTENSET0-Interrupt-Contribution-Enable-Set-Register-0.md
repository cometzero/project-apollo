# GICP_INTENSET0, Interrupt Contribution Enable Set Register 0

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-INTENSET0--Interrupt-Contribution-Enable-Set-Register-0>

### GICP\_INTENSET0, Interrupt Contribution Enable Set Register 0

This register contains the set mechanism for the counter interrupt contribution enables. The GIC-720AE supports five counters, `n` = 0-4.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICP register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary?lang=en "The GIC-720AE Performance Monitoring Unit functions are controlled through registers that are identified with the prefix GICP.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICP\_INTENSET0 bit assignments

![GICP_INTENSET0 bit assignments](images/0182-GICP_INTENSET0-Interrupt-Contribution-Enable-Set-Register-0-img01.svg)



<table id="aov1469193713214__tbl.gicp_intenset0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_INTENSET0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d35290e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d35290e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d35290e142" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[4:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">INTEN</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Interrupt enable. The INTEN[<code class="documents-option">n</code>] bit is the interrupt enable for counter <code class="documents-option">n</code>. This field resets to an unknown value. Reads return the state of the interrupt enables.<p>Writing:</p>
<dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             Sets the interrupt enable for counter

            <code class="documents-option">n</code>.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             No effect. To disable a counter interrupt enable, use

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-INTENCLR0--Interrupt-Contribution-Enable-Clear-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-INTENCLR0--Interrupt-Contribution-Enable-Clear-Register-0?lang=en" title="This register contains the clear mechanism for the counter interrupt contribution enables. The GIC-720AE supports five counters, n = 0-4.">GICP_INTENCLR0</a>.

           </dd>
</dl> <p>The interrupt enable for counter <code class="documents-option">n</code> is enabled when INTEN[<code class="documents-option">n</code>] == 1 and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register?lang=en" title="This register controls whether all counters are enabled or disabled.">GICP_CR</a>.E == 1.</p> <p>Overflow of counter <code class="documents-option">n</code> sets <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-OVSSET0--Overflow-Status-Set-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-OVSSET0--Overflow-Status-Set-Register-0?lang=en" title="This register provides the set mechanism for the counter overflow status bits and provides read access to the counter overflow status bit values. The GIC-720AE supports five counters, n = 0-4.">GICP_OVSSET0</a>.OVS[<code class="documents-option">n</code>] to 1 and that triggers the PMU interrupt if INTEN[<code class="documents-option">n</code>] == 1.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_INTENSET0 is accessible only by Secure accesses.
