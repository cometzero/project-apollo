# GICM_IIDR, Message-based Distributor Implementer Identification Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register>

### GICM\_IIDR, Message-based Distributor Implementer Identification Register

This register provides information about the implementer and revision of the message-based Distributor page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICM) for message-based SPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary?lang=en "The functions for the GIC-720AE message-based SPIs are controlled through the Distributor registers identified with the prefix GICM.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICM\_IIDR bit assignments

![GICM_IIDR bit assignments](images/0123-GICM_IIDR-Message-based-Distributor-Implementer-Identification-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICM_IIDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d153540e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d153540e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d153540e136" rowspan="1">Description</th>
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
