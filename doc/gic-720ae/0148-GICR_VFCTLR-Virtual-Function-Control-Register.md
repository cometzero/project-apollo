# GICR_VFCTLR, Virtual Function Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VFCTLR--Virtual-Function-Control-Register>

### GICR\_VFCTLR, Virtual Function Control Register

This register controls the chicken bit functionality in the vICM. You can use GICR\_VFCTLR to restrict the vLPI and vSGI buffer size to 1, and restrict the number of cross-chip vSGI tokens.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [vLPI register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en "The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_VFCTLR bit assignments

![GICR_VFCTLR bit assignments](images/0148-GICR_VFCTLR-Virtual-Function-Control-Register-img01.svg)



<table id="pro1496219669987__tbl.GICR_VFCTLR">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_VFCTLR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d159841e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d159841e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d159841e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4:3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CredLimCount</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When CredLim == 1, this field can reduce the number of vSGIs that can be sent to each chip:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             1 vSGI can be outstanding to each chip.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             2 vSGIs can be outstanding to each chip.

           </dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             3 vSGIs can be outstanding to each chip.

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
             4 vSGIs can be outstanding to each chip.

           </dd>
</dl> <p>If you set a value that is greater than <code class="documents-parmname">vsgi_cc_tokens</code> − 1, then the GIC behaves as if CredLim == 0.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPILim</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, limits vLPI buffer size to 1.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGILim</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, limits vSGI buffer size to 1.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CredLim</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">This bit enables you to reduce the number of vSGIs that can be sent to each chip:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <code class="documents-parmname">vsgi_cc_tokens</code> configuration parameter sets the number of vSGIs that can be sent to each chip.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The CredLimCount field sets the number of vSGIs that can be sent to each chip.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_VFCTLR is accessible only by Secure accesses.
