# GICR_ICDERRR, Interrupt Clear Distribution Error Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICDERRR--Interrupt-Clear-Distribution-Error-Register>

### GICR\_ICDERRR, Interrupt Clear Distribution Error Register

This register indicates if the SGI distribution data has been corrupted in SRAM. You can use this register to clear an SGI error.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for SGIs and PPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en "The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_ICDERRR bit assignments

![GICR_ICDERRR bit assignments](images/0138-GICR_ICDERRR-Interrupt-Clear-Distribution-Error-Register-img01.svg)



<table id="gqf1499093418133__tbl.gicr_icderrr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_ICDERRR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d71558e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71558e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d71558e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Error</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Indicates whether an SGI is in an error state:

          <dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             If read, SGI

            <code class="documents-option">n</code> is not in an error state. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             If read, SGI

            <code class="documents-option">n</code> is in an error state, so the interrupt is not delivered. Writing 1 clears the error on SGI

            <code class="documents-option">n</code>.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_ICDERRR is accessible only by Secure accesses.
