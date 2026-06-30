# GICP_OVSCLR0, Overflow Status Clear Register 0

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-OVSCLR0--Overflow-Status-Clear-Register-0>

### GICP\_OVSCLR0, Overflow Status Clear Register 0

This register provides the clear mechanism for the counter overflow status bits and provides read access to the counter overflow status bit values. The GIC-720AE supports five counters, `n` = 0-4.

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

Figure 1. GICP\_OVSCLR0 bit assignments

![GICP_OVSCLR0 bit assignments](images/0184-GICP_OVSCLR0-Overflow-Status-Clear-Register-0-img01.svg)



<table id="ymz1469198672399__tbl.gicp_ovsclr0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_OVSCLR0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d11560e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d11560e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d11560e142" rowspan="1">Description</th>
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
<td class="documents-row-nocellborder" colspan="1" rowspan="1">OVS</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Overflow status. The OVS[<code class="documents-option">n</code>] bit is the overflow clear for counter <code class="documents-option">n</code>. This field resets to zero. Reads return the state of the overflow status bits.<p>Writing:</p>
<dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             Clears the overflow status for counter

            <code class="documents-option">n</code>.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             No effect. To set a counter overflow status, use

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-OVSSET0--Overflow-Status-Set-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-OVSSET0--Overflow-Status-Set-Register-0?lang=en" title="This register provides the set mechanism for the counter overflow status bits and provides read access to the counter overflow status bit values. The GIC-720AE supports five counters, n = 0-4.">GICP_OVSSET0</a>.

           </dd>
</dl> <p>Overflow of counter <code class="documents-option">n</code>, that is a transition past the maximum unsigned value of the counter that causes the value to wrap and become zero, sets the corresponding OVS bit. In addition, this event can trigger the PMU interrupt and cause a capture of the PMU counter values, see <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en" title="These registers configure which events that event counter n counts. The GIC-720AE supports five counters, n = 0-4.">GICP_EVTYPERn, Event Type Configuration Registers</a>.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_OVSCLR0 is accessible only by Secure accesses.
