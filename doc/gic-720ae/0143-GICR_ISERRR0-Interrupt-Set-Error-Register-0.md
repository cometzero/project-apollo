# GICR_ISERRR0, Interrupt Set Error Register 0

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR0--Interrupt-Set-Error-Register-0>

### GICR\_ISERRR0, Interrupt Set Error Register 0

This register indicates if the SGI or PPI data has been corrupted in the GCI RAM. For testing purposes, software can use this register to set an SGI or PPI error.

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

Figure 1. GICR\_ISERRR0 bit assignments

![GICR_ISERRR0 bit assignments](images/0143-GICR_ISERRR0-Interrupt-Set-Error-Register-0-img01.svg)



<table id="wtz1496412568521__tbl.gicr_iserrr0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_ISERRR0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d149362e135" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149362e138" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d149362e141" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">Status</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether a PPI is in an error state:

          <dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             If read, PPI[

            <code class="documents-option">n</code>−16] is not in an error state. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             If read, PPI[

            <code class="documents-option">n</code>−16] is in an error state, so the interrupt is not delivered. Writing 1 sets the error on PPI[

            <code class="documents-option">n</code>−16].

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Indicates whether an SGI is in an error state:

          <dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             If read, SGI[

            <code class="documents-option">n</code>] is not in an error state. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             If read, SGI[

            <code class="documents-option">n</code>] is in an error state, so the interrupt is not delivered. Writing 1 sets the error on SGI[

            <code class="documents-option">n</code>].

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_ISERRR0 is accessible only by Secure accesses.
