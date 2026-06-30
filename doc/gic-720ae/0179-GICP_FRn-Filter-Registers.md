# GICP_FRn, Filter Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers>

### GICP\_FRn, Filter Registers

These registers configure the filtering of event counter `n`. The GIC-720AE supports five counters, `n` = 0-4.

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

Figure 1. GICP\_FRn bit assignments

![GICP_FRn bit assignments](images/0179-GICP_FRn-Filter-Registers-img01.svg)



<table id="bma1469118914609__table.gicp_fr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_FRn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d44170e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d44170e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d44170e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FilterType</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Filter type:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             Filter on core

            <span> or vPE or both</span>.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             Filter on INTID.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
<span>Filter on chip or ITS</span>.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             Reserved, no effect.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FilterEncoding</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Filter on range.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Filter on an exact match.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Filter</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">If the corresponding <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en" title="These registers configure which events that event counter n counts. The GIC-720AE supports five counters, n = 0-4.">GICP_EVTYPERn</a>.EVENT indicates an event that cannot be filtered, then the value in this register is ignored.<p>When FilterEncoding == 1, counter <code class="documents-option">n</code> counts events that are associated only with an exact match of the FilterType.</p> <p>When FilterEncoding == 0, this field is encoded so that the first LSB that is zero, indicates the uppermost of a contiguous span of least significant FilterType content bits, that the GIC ignores for the purposes of matching. For example, setting Filter to:</p>
<ul>
<li><span class="documents-g.number.bin">0b11110111_11110111</span> matches with values of <span class="documents-g.number.bin">0b11110111_1111xxxx</span> for FilterType content.</li>
<li><span class="documents-g.number.bin">0b11110111_11110110</span> matches with values of <span class="documents-g.number.bin">0b11110111_1111011x</span> for FilterType content.</li>
<li><span class="documents-g.number.bin">0b11110101_11111111</span> matches with values of <span class="documents-g.number.bin">0b111101xx_xxxxxxxx</span> for FilterType content.</li>
</ul> <p>For events with filtering that is specified as TargetVP in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.event_field_encoding_with_view" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.event_field_encoding_with_view">GICP_EVTYPERn.EVENT field encoding</a>, then the top 2 bits of the filter value have alternative functionality:</p>
<dl>
<dt class="documents-dlterm">
             Filter bit[15]

           </dt>
<dd>
             0 = Use vPE in match.

            <p>1 = Do not use vPE. Virtual events fail in the filter.</p>
</dd>
<dt class="documents-dlterm">
             Filter bit[14]

           </dt>
<dd>
             0 = Use PE in match.

            <p>1 = Do not use PE. Physical events fail in the filter.</p>
</dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_FRn is accessible only by Secure accesses.
