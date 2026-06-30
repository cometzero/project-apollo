# GICP_IIDR, PMU Implementer Identification Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register>

### GICP\_IIDR, PMU Implementer Identification Register

This register provides information about the implementer and revision of the PMU page.

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

Figure 1. GICP\_IIDR bit assignments

![GICP_IIDR bit assignments](images/0189-GICP_IIDR-PMU-Implementer-Identification-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_IIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d29520e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d29520e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d29520e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ProductID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the product ID:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x07</span>
</dt>
<dd>
<span class="documents-keyword">GIC-720AE</span>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Variant</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the major revision, or variant, of the product r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x0</span>
</dt>
<dd>
             r0

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x1</span>
</dt>
<dd>
             r1

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x2</span>
</dt>
<dd>
             r2

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Revision</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the minor revision of the product r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x0</span>
</dt>
<dd>
             p0

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x1</span>
</dt>
<dd>
             p1

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[11:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Implementer</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Identifies the implementer:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x43B</span>
</dt>
<dd>
<span class="documents-keyword">Arm</span>
</dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_IIDR is accessible only by Secure accesses.
