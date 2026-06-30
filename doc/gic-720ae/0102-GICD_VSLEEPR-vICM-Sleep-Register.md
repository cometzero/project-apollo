# GICD_VSLEEPR, vICM Sleep Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register>

### GICD\_VSLEEPR, vICM Sleep Register

This register allows software to put the virtual ITS Communication Module (vICM) to sleep and drain interrupts and programming out of the GICD.

### Configurations

This register is available in all configurations when `ppi_count` == 0, that is, there are zero GCIs.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_VSLEEPR bit assignments

![GICD_VSLEEPR bit assignments](images/0102-GICD_VSLEEPR-vICM-Sleep-Register-img01.svg)



<table id="rqf1475068690861__tbl.gicd_vsleepr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_VSLEEPR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d155558e140" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d155558e143" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d155558e146" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d155558e149" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Quiescent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Indicates whether the vICM is active:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             vICM is awake

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             vICM is asleep

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Sleep</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Controls whether the vICM is asleep:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Abandon sleep

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Put vICM to sleep and drain interrupts and programming out of the GICD.

           </dd>
</dl> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>
