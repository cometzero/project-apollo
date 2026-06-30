# ITS translation register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-translation-register-summary>

### ITS translation register summary

Interrupts to be translated by the GIC-720AE Interrupt Translation Service (ITS) are identified by EventIDs that are written to GITS\_TRANSLATER, the ITS Translation Register.

This page does not exist in GIC-720AE configurations that do not support LPIs or that do not have an ITS.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>ITS translation register summary</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d11817e81" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d11817e84" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d11817e87" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d11817e90" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d11817e93" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d11817e97" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span>- <span class="documents-g.number.hex">0x003C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0040</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_TRANSLATER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ITS Translation Register. See the <a href="https://developer.arm.com/documentation/ihi0069/hb" target="_blank"><span><cite><span class="documents-keyword">Arm®</span> Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4</cite></span></a>.<p>For GIC configurations that support multi view, that is when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.VIEW == 1, the GITS_TRANSLATER ignores the value of view.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0044</span>- <span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
</tbody>
</table>
