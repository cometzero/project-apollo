# GICR_VINVCHIPR, vPE Invalidate Chip Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register>

### GICR\_VINVCHIPR, vPE Invalidate Chip Register

This register can invalidate the vICM RAM in selected chips.

### Configurations

This register is available in all configurations that support vLPIs.

### Attributes

Width
:   32-bit

Functional group
:   See
    [vLPI register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en "The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_VINVCHIPR bit assignments

![GICR_VINVCHIPR bit assignments](images/0150-GICR_VINVCHIPR-vPE-Invalidate-Chip-Register-img01.svg)



<table id="tcu1499093416176__tbl.gicr_vinvchipr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_VINVCHIPR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d125573e132" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d125573e135" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d125573e138" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to start an invalidation request to the vPEs in the chips that GICR_VINVCHIPR.ChipList selects.<p>When read as 0, it indicates that the invalidate request is complete.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual invalidate disable. If set to 1, the invalidation request does not invalidate the vICM RAM, but the GIC performs a drain of vLPIs, vSGIs, commands and streams. RAZ/WI in single chip configurations.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29:28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ChipOffset</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When written, this field controls which range of chips that GICR_VINVCHIPR.ChipList selects:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             Chips 0-15

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             Chips 16-31

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             Chips 32-47

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             Chips 48-63

           </dd>
</dl> <p>For reads, returns <span class="documents-archterm">RES0</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0] </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ChipList</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">When one or more bits are set to 1, it selects a list of chips. Only vPEs with chip information set in this field are invalidated in RAM. The GIC ignores writes that attempts to select a chip that exceeds the number of configured chips.<p>For reads, returns <span class="documents-archterm">RES0</span>.</p> </td>
</tr>
</tbody>
</table>
