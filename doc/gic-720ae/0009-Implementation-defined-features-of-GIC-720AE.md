# Implementation-defined features of GIC-720AE

Source: <https://developer.arm.com/documentation/102666/0201/Implementation-defined-features-of-GIC-720AE>

### Implementation-defined features of GIC-720AE

The GIC-720AE implements features that are defined in the GICv4.1 architecture. Many of these features also have options in the GICv4.1 architecture, which determine behavior that is specific to the GIC-720AE. These features and options are configurable at build time.

The following table summarizes the implementation-defined features of the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb) that GIC-720AE uses. The table also gives references to sections within this manual that provide information about implementation-defined behavior that is specific to the GIC-720AE.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Declared implementation-defined features</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d48726e96" rowspan="2">GICv<span>4.1</span> architecture feature</th>
<th class="documents-nocellnorowborder" colspan="2" id="d48726e102" rowspan="1">Architectural specification reference</th>
<th class="documents-cell-norowborder" colspan="1" id="d48726e105" rowspan="2">Description</th>
</tr>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d48726e111" rowspan="1">Chapter</th>
<th class="documents-cell-norowborder" colspan="1" id="d48726e114" rowspan="1">Section</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1 of N model</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Introduction</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Models for handling interrupts</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/SPIs/SPI-routing-and-1-of-N-selection?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/SPIs/SPI-routing-and-1-of-N-selection?lang=en" title="If GICD_TYPER.No1N==0, then the GIC-720AE supports 1 of N selection of SPI interrupts. You can program an SPI to target several cores, and the GIC-720AE can select which cores receive an SPI.">SPI routing and 1 of N selection</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Direct LPI support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GIC partitioning</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The GIC logical components</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Direct LPI support, that is, using the GICR_SETLPIR and GICR_CLRLPIR registers, is not supported.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS to Redistributor communications</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Locality-specific peripheral interrupts and the ITS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPIs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">This communication occurs over a fully credited <span>AXI5-Stream</span>.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">INTIDs</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distribution and routing of interrupts</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">INTIDs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>16-bit width when supporting LPIs, otherwise the width is set to support the number of SPIs and SGIs.</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">All error cases</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Pseudocode throughout the document</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">All errors are reported through error records, see <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" title="The GIC-720AE uses a range of RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and Scrub, software and bus error reporting.">Reliability, Accessibility, and Serviceability</a>.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based SPIs</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Shared peripheral interrupts</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Pending bits for level sensitive SPIs that are set by writes to GICD_SETSPI_* or GICM_SETSPI_* are not affected by writes to GICD_ICPENDRn.<p>Writes to GICD_CLRSPI_* or GICM_CLRSPI_* have no effect on pending bits set by GICD_ISPENDRn.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt grouping</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt grouping</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">All implemented SPIs, SGIs, and PPIs have programmable groups.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt enables</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enabling individual interrupts</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">All SGIs have a programmable enable.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">Interrupt prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interaction of group and individual interrupt enables</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Interrupts that are disabled through the GICC_CTLR register or the ICC_CTLR_* registers are not considered in the selection of the highest pending interrupt and do not block fully enabled interrupts of a lower priority.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt prioritization</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span><span class="documents-keyword">GIC-720AE</span> supports 32 priority levels, 16 for LPIs that are always Non-secure.</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Effects of disabling interrupts</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Effect of disabling interrupts</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Interrupts are set pending irrespective of the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a>.EnableGrp* settings.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changing priority</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Physical interrupt handling and prioritization</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"> <p>Interrupt prioritization.</p> <p>Changing the priority of enabled PPIs, SGIs, and SPIs.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reprogramming an IPRIORITYRn register does not change the priority of an active interrupt but causes a pending and not active interrupt to be recalled from the CPU interface so that the new priority value can be applied.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI caching</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Locality-specific peripheral interrupts and the ITS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPIs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/LPIs/LPI-caching?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/LPIs/LPI-caching?lang=en" title="If LPI support is configured, the GIC-720AE supports a single LPI cache for each chip with up to 4 banks.">LPI caching</a> and <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/ITS?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/ITS?lang=en" title="The GIC-720AE supports up to 32 Interrupt Translation Services (ITSs) for each chip. Each ITS is responsible for translating message-based interrupts from peripherals into LPIs or vLPIs.">ITS</a>.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI Configuration tables</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Locality-specific peripheral interrupts and the ITS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI Configuration tables</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The <span class="documents-keyword">GIC-720AE</span> has one GICR_PROPBASER register for all cores on a chip and therefore points to a single table.<p>Each chip in a multichip configuration can point to a copy of the table in local memory. See <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.CommonLPIAff for more information.</p> <p>When interrupts are sent between chips, they keep the properties associated with them until the next invalidate. All property fetches are always from the offset specified in the GICR_PROPBASER register of the issuing chip.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">LPI Pending tables</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Locality-specific peripheral interrupts and the ITS</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">LPI Pending tables</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">See the <a href="https://developer.arm.com/documentation/ihi0069/hb" target="_blank"><span><cite><span class="documents-keyword">Arm®</span> Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4</cite></span></a></td>
</tr>
</tbody>
</table>
