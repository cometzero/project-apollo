# GICD_VCFGBASER, vICM Final vPE CFG Attribute Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register>

### GICD\_VCFGBASER, vICM Final vPE CFG Attribute Register

This register returns the access attributes of the vPE Configuration table.

### Configurations

This register is available in all configurations when `ppi_count` == 0, that is, there are zero GCIs.

### Attributes

Width
:   64-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_VCFGBASER bit assignments

![GICD_VCFGBASER bit assignments](images/0101-GICD_VCFGBASER-vICM-Final-vPE-CFG-Attribute-Register-img01.svg)



<table id="mas1475058552510__tbl.gicd_vcfgbaser">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_VCFGBASER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d101163e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d101163e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d101163e142" rowspan="1">Description</th>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" title="This register allows software to put the virtual ITS Communication Module (vICM) to sleep and drain interrupts and programming out of the GICD.">GICD_VSLEEPR</a>.Sleep</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Entry_Size</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.Entry_Size</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58:56]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">OuterCache</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.OuterCache</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[55]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indirect</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.Indirect</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[54:53]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Page_Size</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.Page_Size</td>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.Shareability</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9:7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">InnerCache</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.InnerCache</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[6:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Size</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the value of GITS_BASER2.Size</td>
</tr>
</tbody>
</table>
