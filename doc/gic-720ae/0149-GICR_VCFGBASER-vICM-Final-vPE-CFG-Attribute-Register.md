# GICR_VCFGBASER, vICM Final vPE CFG Attribute Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register>

### GICR\_VCFGBASER, vICM Final vPE CFG Attribute Register

This register returns the access attributes of the vPE Configuration table.

### Configurations

This register is available in all configurations that support vLPIs.

### Attributes

Width
:   64-bit

Functional group
:   See
    [vLPI register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en "The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_VCFGBASER bit assignments

![GICR_VCFGBASER bit assignments](images/0149-GICR_VCFGBASER-vICM-Final-vPE-CFG-Attribute-Register-img01.svg)



<table id="qli1491822303213__tbl.gicr_vcfgbaser">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_VCFGBASER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d17131e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d17131e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d17131e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the access attributes of the vPE Configuration table are valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The access attributes of the vPE Configuration table are not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The access attributes of the vPE Configuration table are valid.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Sleep</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER</a>.Sleep</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Entry_Size</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.Entry_Size</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58:56]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">OuterCache</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.OuterCache</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[55]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indirect</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.Indirect</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[54:53]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Page_Size</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.Page_Size</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[52]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[51:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Addr</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns bits[51:12] of the vPE Configuration table base address</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11:10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Shareability</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.Shareability</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9:7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">InnerCache</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.InnerCache</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[6:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Size</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the value of GICR_VPROPBASER.Size</td>
</tr>
</tbody>
</table>
