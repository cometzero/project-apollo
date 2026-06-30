# GICP_CR, Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register>

### GICP\_CR, Control Register

This register controls whether all counters are enabled or disabled.

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

Figure 1. GICP\_CR bit assignments

![GICP_CR bit assignments](images/0188-GICP_CR-Control-Register-img01.svg)



<table id="pjo1469204987214__tbl.gicp_cr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_CR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d90414e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d90414e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d90414e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">E</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Global counter enable:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No events are counted and the values in

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVCNTRn--Event-Counter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVCNTRn--Event-Counter-Registers?lang=en" title="These registers contain the values of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_EVCNTRn</a> do not change.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The counters are enabled.

           </dd>
</dl> <p>Resets to 0.</p> <p>This bit takes precedence over the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENSET0--Counter-Enable-Set-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENSET0--Counter-Enable-Set-Register-0?lang=en" title="These registers contain the counter enables for each event counter. The GIC-720AE supports five event counters.">GICP_CNTENSET0</a>.CNTEN bits.                        </p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_CR is accessible only by Secure accesses.
