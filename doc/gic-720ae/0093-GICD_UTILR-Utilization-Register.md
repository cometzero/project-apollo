# GICD_UTILR, Utilization Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-UTILR--Utilization-Register>

### GICD\_UTILR, Utilization Register

This register controls the utilization engine in the LPI caches. The register is not distributed and acts only on the local chip.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_UTILR bit assignments

![GICD_UTILR bit assignments](images/0093-GICD_UTILR-Utilization-Register-img01.svg)



<table>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-cell-norowborder" colspan="4" id="d9010e133" rowspan="1">Out of location utilization engine settings</th>
</tr>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e142" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e145" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d9010e148" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UEOT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Out of location utilization engine trigger.<p>The LPI system merges LPIs of the same ID after they reach the target cache. The engine ensures optimal use of the LPI cache and it merges LPIs of the same ID that have not reached the Point-of-Serialization in the target cache.</p> <p>UEOE must be 1 for this bit to have any effect.</p> <p>No effect in configurations without LPIs.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">WO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UEOE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Out of location utilization engine enable:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Engine is disabled

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Enable the engine for any triggers

           </dd>
</dl> <p>No effect in configurations without LPIs.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, RES0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[19:16]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">UEOU</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Out of location utilization engine upper threshold.<p>Automatically trigger the engine when the LPI cache bank is UEOU/16 full.</p> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>




<table>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-cell-norowborder" colspan="4" id="d9010e257" rowspan="1">Disabled utilization engine settings</th>
</tr>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e263" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e266" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d9010e269" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d9010e272" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UEDT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disabled utilization engine trigger.<p>By default the LPI system evicts disabled LPIs as a priority when it needs space in the cache. This engine automatically evicts all disabled interrupts to improve cache performance.</p> <p>UEDE must be 1 for this bit to have any effect.</p> No effect in configurations without LPIs.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">WO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UEDE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disabled utilization engine enable:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Engine is disabled

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Enable the engine for any triggers

           </dd>
</dl> <p>No effect in configurations without LPIs.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, RES0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[3:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">UEDU</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Disabled utilization engine upper threshold.<p>Automatically trigger the engine when the LPI cache bank is UEDU/16 full.</p> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>
