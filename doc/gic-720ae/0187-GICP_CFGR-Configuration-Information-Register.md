# GICP_CFGR, Configuration Information Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CFGR--Configuration-Information-Register>

### GICP\_CFGR, Configuration Information Register

This register returns information about the PMU implementation.

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

Figure 1. GICP\_CFGR bit assignments

![GICP_CFGR bit assignments](images/0187-GICP_CFGR-Configuration-Information-Register-img01.svg)



<table id="eli1469202683034__tbl.gicp_cfgr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_CFGR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d90102e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d90102e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d90102e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:23]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[22]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CAPTURE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 1, to indicate that the GIC supports capture.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[21:14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SIZE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 31, to indicate that the GIC supports 32-bit counters.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[5:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NCTR</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns 4, to indicate that the GIC provides five counters.</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_CFGR is accessible only by Secure accesses.
