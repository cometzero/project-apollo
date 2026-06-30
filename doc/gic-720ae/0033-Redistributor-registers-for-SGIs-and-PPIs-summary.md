# Redistributor registers for SGIs and PPIs summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary>

### Redistributor registers for SGIs and PPIs summary

The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, these GICR registers are accessible for view 0 and the view that [GICR\_VIEWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en "This register controls the view that this Redistributor belongs to.") sets.

For descriptions of registers that are not specific to the GIC-720AE, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).



<table id="aba1434383918260__tbl.redistributor_registers_for_sgis_and_ppis_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Redistributor registers for SGIs and PPIs summary</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d160480e108" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d160480e111" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d160480e114" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d160480e117" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d160480e120" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d160480e124" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d160480e127" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span>- <span class="documents-g.number.hex">0x007C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IGROUPR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0084</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IGROUPR1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0088</span>- <span class="documents-g.number.hex">0x00FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISENABLER0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Enable Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0104</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISENABLER1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Enable Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0108</span>- <span class="documents-g.number.hex">0x017C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0180</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICENABLER0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Enable Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0184</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICENABLER1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Enable Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0188</span>- <span class="documents-g.number.hex">0x01FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0200</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISPENDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Pending Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0204</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISPENDR1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Pending Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0208</span>- <span class="documents-g.number.hex">0x027C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0280</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICPENDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral Clear Pending Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0284</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICPENDR1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral Clear-Pending Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0288</span>- <span class="documents-g.number.hex">0x02FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0300</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISACTIVER0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Active Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0304</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ISACTIVER1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Active Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0308</span>- <span class="documents-g.number.hex">0x037C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0380</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICACTIVER0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Active Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0384</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICACTIVER1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Active Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0388</span>- <span class="documents-g.number.hex">0x03FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0400</span>- <span class="documents-g.number.hex">0x041C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IPRIORITYRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Priority Registers</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0420</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IPRIORITYRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Priority Registers Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0440</span>- <span class="documents-g.number.hex">0x0BFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0C00</span>- <span class="documents-g.number.hex">0x0C04</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICFGRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xAAAAAAAA</span> when <code class="documents-option">n</code> == 0.<p><span class="documents-g.number.hex">0x0</span> when <code class="documents-option">n</code> == 1.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Configuration Registers</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0C08</span>- <span class="documents-g.number.hex">0x0C0C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_ICFGRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Configuration Registers Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0C10</span>- <span class="documents-g.number.hex">0x0CFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IGRPMODR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Modifier Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D04</span>- <span class="documents-g.number.hex">0x0C0C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_IGRPMODR1E</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Modifier Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D08</span>- <span class="documents-g.number.hex">0x0DFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0E00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_NSACR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-secure Access Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0E04</span>- <span class="documents-g.number.hex">0x0F7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0F80</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INMIR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿Non-maskable Interrupt Register for PPIs and SGIs. Only present when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.NMI==1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0F84</span>- <span class="documents-g.number.hex">0x0F88</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INMIRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿Non-maskable Interrupt Register for Extended PPIs, n = 1-2. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16 and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.NMI==1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0F8C</span>- <span class="documents-g.number.hex">0xBFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-MISCSTATUSR--Miscellaneous-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-MISCSTATUSR--Miscellaneous-Status-Register?lang=en" title="Use this register to test the integration of the cpu_active and wake_request input signals. You can also use the register to debug the CPU interface enables that GIC-720AE observes.">GICR_MISCSTATUSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Miscellaneous Status Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICDERRR--Interrupt-Clear-Distribution-Error-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICDERRR--Interrupt-Clear-Distribution-Error-Register?lang=en" title="This register indicates if the SGI distribution data has been corrupted in SRAM. You can use this register to clear an SGI error.">GICR_ICDERRR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Distribution Error Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC00C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC010</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-SGIDR--SGI-Default-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-SGIDR--SGI-Default-Register?lang=en" title="This register controls the default value of SGI settings, for use in the case of a Double-bit Error Detect Error (DEDERR).">GICR_SGIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI Default Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC018</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-DPRIR--Default-Priority-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-DPRIR--Default-Priority-Register?lang=en" title="This register controls the default priority of errored interrupts.">GICR_DPRIR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Default Priority Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC01C</span>- <span class="documents-g.number.hex">0xC0FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICERRR0--Interrupt-Clear-Error-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICERRR0--Interrupt-Clear-Error-Register-0?lang=en" title="This register indicates if the SGI or PPI data has been corrupted in the GCI RAM. Software can use this register to clear an SGI or PPI error.">GICR_ICERRR0</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Error Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC104</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICERRR1E--Interrupt-Clear-Error-Register-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ICERRR1E--Interrupt-Clear-Error-Register-Extended?lang=en" title="This register indicates if the PPI[47:16] data has been corrupted in the GCI RAM. Software can use this register to clear an error.">GICR_ICERRR1E</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Error Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC108</span>- <span class="documents-g.number.hex">0xC17C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC180</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR0--Interrupt-Set-Error-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR0--Interrupt-Set-Error-Register-0?lang=en" title="This register indicates if the SGI or PPI data has been corrupted in the GCI RAM. For testing purposes, software can use this register to set an SGI or PPI error.">GICR_ISERRR0</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set Error Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC184</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR1E--Interrupt-Set-Error-Register-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ISERRR1E--Interrupt-Set-Error-Register-Extended?lang=en" title="This register indicates if the PPI[47:16] data has been corrupted in the GCI RAM. For testing purposes, software can use this register to set a PPI error.">GICR_ISERRR1E</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set Error Register Extended. Only present when <code class="documents-parmname">ppis_per_cpu</code> &gt; 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC188</span>- <span class="documents-g.number.hex">0xEFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID0--Configuration-ID0-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID0--Configuration-ID0-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID0</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration ID0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration ID1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF010</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ERRINSR--Error-Insertion-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ERRINSR--Error-Insertion-Register?lang=en" title="This register can inject errors into the PPI RAM. You can use this register to test your error recovery software.">GICR_ERRINSR</a></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RW</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">64</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Error Insertion Register</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">No</td>
</tr>
</tbody>
</table>
