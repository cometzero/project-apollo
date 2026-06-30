# GICP_SVRn, Shadow Value Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-SVRn--Shadow-Value-Registers>

### GICP\_SVRn, Shadow Value Registers

These registers contain the shadow value of event counter `n`. The GIC-720AE supports five counters, `n` = 0-4.

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

Figure 1. GICP\_SVRn bit assignments

![GICP_SVRn bit assignments](images/0178-GICP_SVRn-Shadow-Value-Registers-img01.svg)



<table id="qzt1469112007754__tbl.gicp_svr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_SVRn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d95995e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d95995e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d95995e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">COUNT</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Captured counter value.<p>This field holds the captured counter values of the corresponding entry in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVCNTRn--Event-Counter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVCNTRn--Event-Counter-Registers?lang=en" title="These registers contain the values of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_EVCNTRn</a>.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_SVRn is accessible only by Secure accesses.
