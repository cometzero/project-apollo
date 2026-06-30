# ITS vSGI register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-vSGI-register-summary>

### ITS vSGI register summary

Virtual SGIs to be injected directly into a virtual machine are written to the ITS translation register GITS\_SGIR.

This page does not exist in GIC-720AE configurations that do not support vSGIs or that do not have an ITS. For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, the GITS\_SGIR register is accessible for view 0 and view 1 only.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>ITS vSGI register summary</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d180663e87" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d180663e90" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d180663e93" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d180663e96" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d180663e99" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d180663e103" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span>- <span class="documents-g.number.hex">0x001C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_SGIR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ITS vSGI Register. See the <a href="https://developer.arm.com/documentation/ihi0069/hb" target="_blank"><span><cite><span class="documents-keyword">Arm®</span> Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4</cite></span></a>.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0028</span>- <span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
</tbody>
</table>
