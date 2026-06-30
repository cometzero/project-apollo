# GICP_CNTENCLR0, Counter Enable Clear Register 0

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENCLR0--Counter-Enable-Clear-Register-0>

### GICP\_CNTENCLR0, Counter Enable Clear Register 0

This register contains the counter disables for each event counter. The GIC-720AE supports five event counters.

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

Figure 1. GICP\_CNTENCLR0 bit assignments

![GICP_CNTENCLR0 bit assignments](images/0181-GICP_CNTENCLR0-Counter-Enable-Clear-Register-0-img01.svg)



<table id="sir1469192804358__table.gicp_cntenclr0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_CNTENCLR0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d49574e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d49574e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d49574e139" rowspan="1">Description</th>
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
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CNTEN</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Counter disable. The CNTEN[<code class="documents-option">n</code>] bit is the disable for counter <code class="documents-option">n</code>. This field resets to an unknown value. Reads return the state of the counter enables.<p>Writing:</p>
<dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             Disables counter

            <code class="documents-option">n</code>.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             No effect. To enable a counter, use

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENSET0--Counter-Enable-Set-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENSET0--Counter-Enable-Set-Register-0?lang=en" title="These registers contain the counter enables for each event counter. The GIC-720AE supports five event counters.">GICP_CNTENSET0</a>.

           </dd>
</dl> <p>Counter <code class="documents-option">n</code> is disabled when CNTEN[<code class="documents-option">n</code>] == 0 or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register?lang=en" title="This register controls whether all counters are enabled or disabled.">GICP_CR</a>.E == 0.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_CNTENCLR0 is accessible only by Secure accesses.
