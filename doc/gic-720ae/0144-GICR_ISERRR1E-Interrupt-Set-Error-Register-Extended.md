# GICR_ISERRR1E, Interrupt Set Error Register Extended

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR1E--Interrupt-Set-Error-Register-Extended>

### GICR\_ISERRR1E, Interrupt Set Error Register Extended

This register indicates if the PPI[47:16] data has been corrupted in the GCI RAM. For testing purposes, software can use this register to set a PPI error.

### Configurations

This register is available in configurations with > 16 PPIs, that is, when [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.").PPInum >0.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for SGIs and PPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en "The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_ISERRR1E bit assignments

![GICR_ISERRR1E bit assignments](images/0144-GICR_ISERRR1E-Interrupt-Set-Error-Register-Extended-img01.svg)



<table id="qph1496409788983__tbl.gicr_iserrr1e">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_ISERRR1E bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d54754e144" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d54754e147" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d54754e150" rowspan="1">Description</th>
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

            <code class="documents-option">n</code>+16] is in an error state, so the interrupt is not delivered. Writing 1 sets the error on PPI[

            <code class="documents-option">n</code>+16].

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_ISERRR1E is accessible only by Secure accesses.
