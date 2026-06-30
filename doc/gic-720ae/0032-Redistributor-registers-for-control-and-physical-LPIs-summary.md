# Redistributor registers for control and physical LPIs summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary>

### Redistributor registers for control and physical LPIs summary

The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.

For more information about LPIs, see the [Learn the architecture - Generic Interrupt Controller v3 and v4, LPIs](https://developer.arm.com/documentation/102923/latest).

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, these GICR registers are accessible for view 0 and when the view matches the PE. See [Multi view access to the GICR registers](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en#aba1429015518698__section.multiview_access_to_the_GICR_registers) for information about the views that a register is accessible in.

For descriptions of registers that are not specific to the GIC-720AE, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).



<table id="aba1429015518698__tbl.redistributor_registers_for_control_and_physical_lpis_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span><span>Redistributor registers for control and physical LPIs summary</span></span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d108186e115" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e118" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e121" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e124" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e127" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e131" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d108186e134" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Redistributor.">GICR_IIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x070nn43B</span><p>The <code>nn</code> value depends on the r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor Implementation Identification Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor Type Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0010</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0014</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Power Management Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Some bits are architecture defined and the others are microarchitecture defined.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0018</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR_PARTIDR.">GICR_MPAMIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Report maximum PARTID and PMG Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x001C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" title="This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.">GICR_PARTIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>RW</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set PARTID and PMG Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" title="This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.">GICR_FCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span><span class="documents-g.number.hex">0x00000200</span> if the <span>GCI</span> supports real-time interrupts, otherwise <span class="documents-g.number.hex">0x0</span>.</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Function Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0024</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" title="This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.">GICR_PWRR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Power Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0028</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" title="This register specifies which class of 1 of N interrupt the CPU accepts.">GICR_CLASSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Class Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x002C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" title="This register controls the view that this Redistributor belongs to.">GICR_VIEWR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">View Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0030</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" title="This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.">GICR_FLUSHR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3CFFFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Flush Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0034</span>- <span class="documents-g.number.hex">0x006C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0070</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PROPBASER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor Properties Base Address Register. Only present when ITS and LPI support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0078</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PENDBASER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor LPI Pending Table Base Address Register. Only present when ITS and LPI support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080</span>- <span class="documents-g.number.hex">0x009C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00A0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INVLPIR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>-</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00A8</span>- <span class="documents-g.number.hex">0x00AC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00B0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INVALLR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>-</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00B8</span>- <span class="documents-g.number.hex">0x00BC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00C0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_SYNCR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>-</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00C4</span>- <span class="documents-g.number.hex">0x00FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" title="This register allows Secure software to write the affinity values of a Redistributor.">GICR_MPIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPIDR Register. Present only when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.RDC == 1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0104</span>- <span class="documents-g.number.hex">0xFFCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 4 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 5 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 6 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 7 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x93</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PIDR2--Peripheral-ID2-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PIDR2--Peripheral-ID2-Register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICR_PIDR2 register is part of the set of Redistributor peripheral identification registers.">GICR_PIDR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 3 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICR_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Component ID 3 Register</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">No</td>
</tr>
</tbody>
</table>



### Multi view access to the GICR registers

The following table shows the views that a GICR register is accessible in.



<table id="aba1429015518698__tbl.gci_registers_summary_multiview">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>Multi view access to the GICR registers</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d108186e1268" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d108186e1271" rowspan="1">View</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Redistributor.">GICR_IIDR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR_PARTIDR.">GICR_MPAMIDR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" title="This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.">GICR_PARTIDR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" title="This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.">GICR_FCTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" title="This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.">GICR_PWRR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" title="This register specifies which class of 1 of N interrupt the CPU accepts.">GICR_CLASSR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" title="This register controls the view that this Redistributor belongs to.">GICR_VIEWR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" title="This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.">GICR_FLUSHR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PROPBASER</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PENDBASER</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INVLPIR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_INVALLR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_SYNCR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" title="This register allows Secure software to write the affinity values of a Redistributor.">GICR_MPIDR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Not 2 or 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR4</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR5</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR6</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR7</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PIDR2--Peripheral-ID2-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PIDR2--Peripheral-ID2-Register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICR_PIDR2 register is part of the set of Redistributor peripheral identification registers.">GICR_PIDR2</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_PIDR3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR_CIDR2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICR_CIDR3</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Set by GICD_IVIEWRn or GICD_IVIEWRnE.</td>
</tr>
</tbody>
</table>
