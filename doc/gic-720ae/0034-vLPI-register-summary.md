# vLPI register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary>

### vLPI register summary

The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.

This page does not exist in GIC-720AE configurations that do not support vLPIs.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, these GICR registers are accessible for view 0 and the view that [GICR\_VIEWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en "This register controls the view that this Redistributor belongs to.") sets.

See the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb) for information about the vLPI registers.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>vLPI register summary</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e111" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e114" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e117" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e120" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e123" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d15174e127" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d15174e130" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span>- <span class="documents-g.number.hex">0x001C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VFCTLR--Virtual-Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VFCTLR--Virtual-Function-Control-Register?lang=en" title="This register controls the chicken bit functionality in the vICM. You can use GICR_VFCTLR to restrict the vLPI and vSGI buffer size to 1, and restrict the number of cross-chip vSGI tokens.">GICR_VFCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual Function Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0024</span>- <span class="documents-g.number.hex">0x006C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0070</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_VPROPBASER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual Redistributor Properties Base Address Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0078</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_VPENDBASER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual Pending Table Base Address Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_VSGIR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual SGI Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0084</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0088</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_VSGIPENDR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual SGI Pending Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x008C</span>- <span class="documents-g.number.hex">0x0FFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" title="This register returns the access attributes of the vPE Configuration table.">GICR_VCFGBASER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vICM Final vPE CFG Attribute Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0108</span>- <span class="documents-g.number.hex">0x011C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0120</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" title="This register can invalidate the vICM RAM in selected chips.">GICR_VINVCHIPR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vPE Invalidate Chip Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0124</span>- <span class="documents-g.number.hex">0xE0FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" title="This register can set and clear the error bit for a vPE in the vICM RAM. You can use the register to find vPEs with an error in the vICM and obtain vPE information from the vTGT cache and the vICM.">GICR_VERRR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vICM vPE Error Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE108</span>- <span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">-</td>
</tr>
</tbody>
</table>
