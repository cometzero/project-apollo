# GICR_ICERRR1E, Interrupt Clear Error Register Extended

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICERRR1E--Interrupt-Clear-Error-Register-Extended>

### GICR\_ICERRR1E, Interrupt Clear Error Register Extended

This register indicates if the PPI[47:16] data has been corrupted in the GCI RAM. Software can use this register to clear an error.

### Configurations

This register available in configurations with > 16 PPIs, that is, when [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.").PPInum >0.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for SGIs and PPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en "The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_ICERRR1E bit assignments

![GICR_ICERRR1E bit assignments](images/0142-GICR_ICERRR1E-Interrupt-Clear-Error-Register-Extended-img01.svg)



<table id="krl1496836906759__tbl.gicr_icerrr1e">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_ICERRR1E bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d148701e144" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d148701e147" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d148701e150" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Status</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Indicates whether a PPI[47:16] is in an error state:

          <dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 0

           </dt>
<dd>
             If read, PPI[

            <code class="documents-option">n</code>+16] is not in an error state. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">n</code>] = 1

           </dt>
<dd>
             If read, PPI[

            <code class="documents-option">n</code>+16] is in an error state, so the interrupt is not delivered. Writing 1 clears the error on PPI[

            <code class="documents-option">n</code>+16].

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_ICERRR1E is accessible only by Secure accesses.
