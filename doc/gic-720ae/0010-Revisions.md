# Revisions

Source: <https://developer.arm.com/documentation/102666/0201/Revisions>

### Revisions

This appendix describes the technical changes between released issues of this document.



<table id="giu1630663327295__table.r0p0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Issue 0000-01</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e62" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e65" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">First release</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">-</td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r0p1">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>Differences between issue 0000-01 and issue 0001-02</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e97" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e100" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctrl_ds</span></span> to <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds</span></span>. Corrected <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctrl_ds_chk</span></span> to <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds_chk</span></span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Interrupt-groups-and-security?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Interrupt-groups-and-security?lang=en" title="The GIC-720AE configures the interrupts that it receives into one of three groups. Each group determines the security status of an interrupt and how it is routed.">Interrupt groups and security</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Revision value for r0p1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Distributor.">GICD_IIDR, Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the message-based Distributor page.">GICM_IIDR, Message-based Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Redistributor.">GICR_IIDR, Redistributor Implementation Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the ITS.">GITS_IIDR, ITS Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the trace page.">GICT_IIDR, Trace Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the PMU page.">GICP_IIDR, PMU Implementer Identification Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Version value for r0p1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">For CPU interface protection, added information about instability in the <span class="documents-g.signal.name"><span class="documents-keyword">iritdest_*_crc</span></span> signal.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Corrected <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctrl_ds</span></span> to <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds</span></span>.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Connecting-the-chips?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Connecting-the-chips?lang=en" title="Use the following procedure to connect the chips in a multichip configuration.">Connecting the chips</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r1p0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 3. </span>Differences between issue 0001-02 and issue 0100-03</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e265" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e268" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added multi view feature and its associated registers.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" title="The multi view feature allows software to allocate GIC resources into three or fewer different views. This feature allows control firmware to allocate the GIC to three, or fewer, different OS or hypervisors that are running independent software stacks.">Multi view</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" title="These registers can clear the view error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICVERRR1-GICD_ICVERRR30.">GICD_ICVERRRn, Interrupt Clear View Error Registers</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" title="These registers can clear the view error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICVERRR0E-GICD_ICVERRR31E.">GICD_ICVERRRnE, Interrupt Clear View Error Registers Extended</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn, Interrupt View Registers</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE, Interrupt View Registers Extended</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" title="This register controls the view that this Redistributor belongs to.">GICR_VIEWR, View Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Variant value for r1p0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Distributor.">GICD_IIDR, Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the message-based Distributor page.">GICM_IIDR, Message-based Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Redistributor.">GICR_IIDR, Redistributor Implementation Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the ITS.">GITS_IIDR, ITS Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the trace page.">GICT_IIDR, Trace Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the PMU page.">GICP_IIDR, PMU Implementer Identification Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Version value for r1p0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a register for GSPV.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" title="This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.">GICR_FLUSHR, Flush Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the <code class="documents-parmname">number_ll_int_credit</code> parameter name.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-CFGID--Configuration-ID-Register?lang=en" title="This register returns information about the configuration of the ITS block such as its ID number.">GITS_CFGID, Configuration ID Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Add information about page accesses to PROTIDs that are not present in the configuration.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">For CPU interface protection, an instability in the <span class="documents-g.signal.name"><span class="documents-keyword">iritdest_*_crc</span></span> signal sets the crc_chksum_err bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the number of CPUIF protection blocks from 64 to 16.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" title="The GIC assigns an ID for each protection mechanism in a functional block. For each protection mechanism ID we provide a description and the recommended recovery process.">Protection mechanism IDs</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Corrected the description of the Direct LPI support feature.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Implementation-defined-features-of-GIC-720AE?lang=en" href="https://developer.arm.com/documentation/102666/0201/Implementation-defined-features-of-GIC-720AE?lang=en" title="The GIC-720AE implements features that are defined in the GICv4.1 architecture. Many of these features also have options in the GICv4.1 architecture, which determine behavior that is specific to the GIC-720AE. These features and options are configurable at build time.">Implementation-defined features of GIC-720AE</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r0p1_safety">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 4. </span>Differences between issue 0100-03 and issue 0001-04</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e568" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e571" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">For the SMID field, added information about setting EN and SMID=255.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" title="This register enables or disables particular protection mechanisms inside a specified GIC block. At reset, the GIC enables all the protection mechanisms. We recommend that software does not disable any protection mechanisms.">FMU_SMEN, Safety Mechanism Enable register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the bit names and description for the <span>AXI5-Stream</span> cross-chip protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about page 1 timeouts for <span>ACE5-Lite</span> cross-chip protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added a restriction for the SMID field when BLKID_ERR == 1 or BLKID_PWROFF == 1.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS, FMU Status Register</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r2p0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 5. </span>Differences between issue 0001-04 and issue 0200-05</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e698" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e701" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added support for real-time interrupts.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/SPIs?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/SPIs?lang=en" title="A Shared Peripheral Interrupt (SPI) is generated by a peripheral that is accessible across the whole system such as a USB receiver, and which can connect to several cores. SPIs are typically used for peripherals that are not tightly coupled to a specific core.">SPIs</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the description about reassigning SPIs with GICD_IVIEWRn.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" title="The multi view feature allows software to allocate GIC resources into three or fewer different views. This feature allows control firmware to allocate the GIC to three, or fewer, different OS or hypervisors that are running independent software stacks.">Multi view</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about the excessive assertion of the <span class="documents-g.signal.name"><span class="documents-keyword">pmu_int</span></span> signal.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt">Overflow interrupt</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed GICT_ERR1MISC0 to GICT_ERR&lt;n&gt;MISC0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" title="SPI RAM error record 1 records RAM ECC errors that are correctable. SPI RAM error record 2 records RAM ECC errors that are uncorrectable.">SPI RAM error records 1-2</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the SPF bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" title="This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.">GICD_SAC, Secure Access Control register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the CC_SHARED bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" title="This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.">GICD_CCCTLR, Cross-Chip Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the SPI_BLOCK_MIN and SPI_BLOCKS descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPR&lt;n&gt;, Chip Registers</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GSPV_CGO bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" title="This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.">GICR_FCTLR, Function Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the AccessType bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-MISCSTATUSR--Miscellaneous-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-MISCSTATUSR--Miscellaneous-Status-Register?lang=en" title="Use this register to test the integration of the cpu_active and wake_request input signals. You can also use the register to debug the CPU interface enables that GIC-720AE observes.">GICR_MISCSTATUSR, Miscellaneous Status Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Variant value for r2p0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Distributor.">GICD_IIDR, Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the message-based Distributor page.">GICM_IIDR, Message-based Distributor Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-IIDR--Redistributor-Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Redistributor.">GICR_IIDR, Redistributor Implementation Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the ITS.">GITS_IIDR, ITS Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the trace page.">GICT_IIDR, Trace Implementer Identification Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IIDR--PMU-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the PMU page.">GICP_IIDR, PMU Implementer Identification Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Version value for r2p0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the OF bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS, Error Record Primary Status Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clarified the behavior of successive writes to the FMU_KEY register.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" title="The FMU registers are protected against inadvertent writes by a lock and key mechanism.">Lock and key mechanism</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added a limitation for the FMU.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" title="The GIC can be configured to either enable Secure software or a tie-off signal to remove cores from a GIC configuration. This feature enables you to use a single GIC configuration in multiple products that contain a different number of cores.">Removing cores from a preconfigured GIC</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r0p1_safety_2nd_release">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 6. </span>Differences between issue 0001-04 and issue 0001-06</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e1001" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e1004" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about the excessive assertion of the <span class="documents-g.signal.name"><span class="documents-keyword">pmu_int</span></span> signal.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt">Overflow interrupt</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed GICT_ERR1MISC0 to GICT_ERR&lt;n&gt;MISC0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" title="SPI RAM error record 1 records RAM ECC errors that are correctable. SPI RAM error record 2 records RAM ECC errors that are uncorrectable.">SPI RAM error records 1-2</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the SPI_BLOCK_MIN and SPI_BLOCKS descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPR&lt;n&gt;, Chip Registers</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the OF bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS, Error Record Primary Status Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clarified the behavior of successive writes to the FMU_KEY register.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" title="The FMU registers are protected against inadvertent writes by a lock and key mechanism.">Lock and key mechanism</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added a limitation for the FMU.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" title="The GIC can be configured to either enable Secure software or a tie-off signal to remove cores from a GIC configuration. This feature enables you to use a single GIC configuration in multiple products that contain a different number of cores.">Removing cores from a preconfigured GIC</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r1p0_safety">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 7. </span>Differences between issue 0100-03 and issue 0100-07</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e1112" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e1115" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the description about reassigning SPIs with GICD_IVIEWRn.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" title="The multi view feature allows software to allocate GIC resources into three or fewer different views. This feature allows control firmware to allocate the GIC to three, or fewer, different OS or hypervisors that are running independent software stacks.">Multi view</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about the excessive assertion of the <span class="documents-g.signal.name"><span class="documents-keyword">pmu_int</span></span> signal.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Performance-Monitoring-Unit?lang=en#fpu1489160639895__section.overflow_interrupt">Overflow interrupt</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed GICT_ERR1MISC0 to GICT_ERR&lt;n&gt;MISC0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en" title="SPI RAM error record 1 records RAM ECC errors that are correctable. SPI RAM error record 2 records RAM ECC errors that are uncorrectable.">SPI RAM error records 1-2</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the SPF bit and GICTNS bit descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" title="This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.">GICD_SAC, Secure Access Control register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the CC_SHARED bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" title="This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.">GICD_CCCTLR, Cross-Chip Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the SPI_BLOCK_MIN and SPI_BLOCKS descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPR&lt;n&gt;, Chip Registers</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the ACRC bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en#col1468512211793__tbl.gicd_cfgid_with_view_column" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en#col1468512211793__tbl.gicd_cfgid_with_view_column">GICD_CFGID bit assignments</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GSPV_CGO bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" title="This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.">GICR_FCTLR, Function Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added two usage constraints.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" title="This register controls the view that this Redistributor belongs to.">GICR_VIEWR, View Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a usage constraint.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" title="This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.">GICR_FLUSHR, Flush Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the usage constraint.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" title="This register allows Secure software to write the affinity values of a Redistributor.">GICR_MPIDR, MPIDR Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the width of the PPIs_per_Processor field.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the OF bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS, Error Record Primary Status Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">For the SMID field, added information about setting EN and SMID=255.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" title="This register enables or disables particular protection mechanisms inside a specified GIC block. At reset, the GIC enables all the protection mechanisms. We recommend that software does not disable any protection mechanisms.">FMU_SMEN, Safety Mechanism Enable register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the bit names and description for the <span>AXI5-Stream</span> cross-chip protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about page 1 timeouts for <span>ACE5-Lite</span> cross-chip protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the error_INTID field width and description for page 2 interrupt protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a restriction for the SMID field when BLKID_ERR == 1 or BLKID_PWROFF == 1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS, FMU Status Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added ACE5-Lite to the SM_AXITCRC_GICD_ICDR description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" title="The GIC assigns an ID for each protection mechanism in a functional block. For each protection mechanism ID we provide a description and the recommended recovery process.">Protection mechanism IDs</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GSPV error recovery description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1">GSPV error recovery</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clarified the behavior of successive writes to the FMU_KEY register.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Lock-and-key-mechanism?lang=en" title="The FMU registers are protected against inadvertent writes by a lock and key mechanism.">Lock and key mechanism</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about interrupt protection BIST.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added a limitation for the FMU.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" title="The GIC can be configured to either enable Secure software or a tie-off signal to remove cores from a GIC configuration. This feature enables you to use a single GIC configuration in multiple products that contain a different number of cores.">Removing cores from a preconfigured GIC</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r2p0_safety">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 8. </span>Differences between issue 0200-05 and issue 0200-08</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e1535" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e1538" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about the FMU.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-?lang=en" title="The Distributor is the main communication point between all GIC-720AE blocks. It performs SPI management, real-time SPI prioritization, and LPI caching, and all communications with other blocks and chips. It also contains the Fault Management Unit (FMU).">Distributor (GICD)</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the MTE_Support information for <span>ACE5-Lite</span> manager interfaces.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface/AMBA-bus-properties--GICD-manager-interface?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface/AMBA-bus-properties--GICD-manager-interface?lang=en" title="The AMBA protocols define multiple property types that indicate the capabilities of a device.">AMBA bus properties, GICD manager interface</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added an option for the number of real-time <span>GCI</span>s.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-configuration?lang=en" title="You can configure several options that relate to the operation of the Distributor block.">Distributor configuration</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated both data bus widths for a real-time <span>GCI</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-configuration?lang=en" title="You can configure several options that relate to the operation of the GCI.">GCI configuration</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the <span class="documents-g.signal.name"><span class="documents-keyword">spi_col_id[4:0]</span></span> signal to the SPI Collator figure.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator?lang=en" title="The SPI Collator converts SPI wires into messages to be sent to the Distributor. The GIC can be configured to provide up to 32 SPI Collators.">SPI Collator</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the names of the <code class="documents-parmname">SPI_PROT_RESET_DISABLED</code> and <code class="documents-parmname">SPI_PROT_RESET_PERMONLY</code> build-time options.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-configuration?lang=en" title="You can configure several options that relate to the operation of an SPI Collator block.">SPI Collator configuration</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clarified the register programming order when GICD_CFGID.RDC == 1.<p>Updated the description about reassigning SPIs with GICD_IVIEWRn.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en" title="The multi view feature allows software to allocate GIC resources into three or fewer different views. This feature allows control firmware to allocate the GIC to three, or fewer, different OS or hypervisors that are running independent software stacks.">Multi view</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed SPI IDs to INTIDs, in the NumSPIS description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" title="This register returns information about the number of SPIs that are assigned to the frame.">GICM_TYPER, Message-based Type Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the GICR_FCTLR reset value for a real-time <span>GCI</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" title="The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.">Redistributor registers for control and physical LPIs summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the ECP bit description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en" title="This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.">GICR_FCTLR, Function Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added two usage constraints.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en" title="This register controls the view that this Redistributor belongs to.">GICR_VIEWR, View Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a usage constraint.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en" title="This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.">GICR_FLUSHR, Flush Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the usage constraint.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en" title="This register allows Secure software to write the affinity values of a Redistributor.">GICR_MPIDR, MPIDR Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the width of the PPIs_per_Processor field.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the VID and ChipOffset fields.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" title="This register can invalidate the vICM RAM in selected chips.">GICR_VINVCHIPR, vPE Invalidate Chip Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added some Q-Channel information to events <span class="documents-g.number.hex">0x94</span> and <span class="documents-g.number.hex">0x95</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.gicp_evcntr_n" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.gicp_evcntr_n">GICP_EVTYPERn bit descriptions</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a usage constraint about clearing the V bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS, Error Record &lt;n&gt; Primary Status register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the error_INTID field width and description for page 2 interrupt protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added Q-Channel information.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/FMU-Q-Channel?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/FMU-Q-Channel?lang=en" title="The Fault Management Unit (FMU) has a Q-Channel interface which controls requests from an external clock gating source.">FMU Q-Channel</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GSPV error recovery description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1">GSPV error recovery</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a recommendation to enable the block error signals in all blocks.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Enabling-or-disabling-both-error-signals-on-a-block?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Enabling-or-disabling-both-error-signals-on-a-block?lang=en" title="Each block has a critical error signal output and a non-critical error signal output. Software can enable or disable both output signals on a block.">Enabling or disabling both error signals on a block</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added information about interrupt protection BIST.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r1p0_safety_2nd_release">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 9. </span>Differences between issue 0100-07 and issue 0100-09</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e1952" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e1955" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed 0001-07 to 0100-07 in the Document history table.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a href="https://developer.arm.com/deb1346331407548.xhtml">Release Information</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about the FMU.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-?lang=en" title="The Distributor is the main communication point between all GIC-720AE blocks. It performs SPI management, real-time SPI prioritization, and LPI caching, and all communications with other blocks and chips. It also contains the Fault Management Unit (FMU).">Distributor (GICD)</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the MTE_Support information for <span>ACE5-Lite</span> manager interfaces.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface/AMBA-bus-properties--GICD-manager-interface?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface/AMBA-bus-properties--GICD-manager-interface?lang=en" title="The AMBA protocols define multiple property types that indicate the capabilities of a device.">AMBA bus properties, GICD manager interface</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the <span class="documents-g.signal.name"><span class="documents-keyword">spi_col_id[4:0]</span></span> signal to the SPI Collator figure.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator?lang=en" title="The SPI Collator converts SPI wires into messages to be sent to the Distributor. The GIC can be configured to provide up to 32 SPI Collators.">SPI Collator</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the names of the <code class="documents-parmname">SPI_PROT_RESET_DISABLED</code> and <code class="documents-parmname">SPI_PROT_RESET_PERMONLY</code> build-time options.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-configuration?lang=en" title="You can configure several options that relate to the operation of an SPI Collator block.">SPI Collator configuration</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GICD_IVIEWR[1:0] and GICD_ICVERRR0 descriptions because those registers are Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" title="The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.">Distributor registers (GICD/GICDA) summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed SPI IDs to INTIDs, in the NumSPIS description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" title="This register returns information about the number of SPIs that are assigned to the frame.">GICM_TYPER, Message-based Type Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the VID and ChipOffset fields.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" title="This register can invalidate the vICM RAM in selected chips.">GICR_VINVCHIPR, vPE Invalidate Chip Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a usage constraint about clearing the V bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS, Error Record &lt;n&gt; Primary Status register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the PAGEID field description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR, Safety Mechanism Page Write Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD, Safety Mechanism Page Read Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added Q-Channel information.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/FMU-Q-Channel?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/FMU-Q-Channel?lang=en" title="The Fault Management Unit (FMU) has a Q-Channel interface which controls requests from an external clock gating source.">FMU Q-Channel</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added a recommendation to enable the block error signals in all blocks.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Enabling-or-disabling-both-error-signals-on-a-block?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Enabling-or-disabling-both-error-signals-on-a-block?lang=en" title="Each block has a critical error signal output and a non-critical error signal output. Software can enable or disable both output signals on a block.">Enabling or disabling both error signals on a block</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r2p0_safety_2nd_release">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 10. </span>Differences between issue 0200-08 and issue 0200-10</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e2212" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e2215" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Changed 0001-07 to 0100-07 in the Document history table</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a href="https://developer.arm.com/deb1346331407548.xhtml">Release Information</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r2p1_safety_release">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 11. </span>Differences between issue 0200-10 and issue 0201-11</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e2249" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e2252" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the number of chips from 16 to 64.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/About-the-GIC-720AE?lang=en" href="https://developer.arm.com/documentation/102666/0201/About-the-GIC-720AE?lang=en" title="The GIC-720AE is a Functional Safety (FuSa) variant of the GIC‑700. The GIC-720AE is a Generic Interrupt Controller (GIC) that handles interrupts from peripherals to the cores and between cores. The GIC-720AE supports a distributed microarchitecture containing several individual blocks that are used to provide a flexible GIC implementation.">About the GIC-720AE</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GICv4.2 support option.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-configuration?lang=en" title="You can configure several options that relate to the operation of the Distributor block.">Distributor configuration</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added a 1024-bit data width option.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-ACE5-Lite-subordinate-interface?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-ACE5-Lite-subordinate-interface?lang=en" title="The ITS AMBA ACE5-Lite subordinate interface has a configurable data width of 64 bits, 128 bits, 256 bits, 512 bits, or 1024 bits.">ITS ACE5-Lite subordinate interface</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-configuration?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-configuration?lang=en" title="You can configure several options that relate to the operation of the ITS block.">ITS configuration</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed all instances of GICR_VPROPBASER to GICR_VPENDBASER.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Direct-injection/Residency-and-VMOVP?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Direct-injection/Residency-and-VMOVP?lang=en" title="Software freely moves vPEs around between PEs on both the local and remote chips, using the ITS VMOVP command.">Residency and VMOVP</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the (E) option to those registers that support the extended range.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/SPIs/SPI-error-recovery-procedure?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/SPIs/SPI-error-recovery-procedure?lang=en" title="If an uncorrectable SPI error occurs, then software must clear the error for that SPI. After clearing the error, software can reprogram the interrupt to the intended settings.">SPI error recovery procedure</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added configurable Memory Partitioning and Monitoring (MPAM) widths.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Memory-access-and-attributes/MPAM-information?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Memory-access-and-attributes/MPAM-information?lang=en" title="The GIC-720AE supports Memory Partitioning and Monitoring (MPAM) and it assigns PARTIDR and PMG values to all memory accesses that it issues on the ACE5-Lite manager interface.">MPAM information</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Removed some entries in the <span class="documents-q">“No v4.1 support”</span> column.<p>Added information about the presence of one or two 64KB pages for a cross-chip <span>ACE5-Lite</span> subordinate interface.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages?lang=en#bak1489161065998__table.register_pages" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages?lang=en#bak1489161065998__table.register_pages">Register map pages</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GICD_CCCGR and GICD_CCCCR descriptions. Added the GICD_INMIR and GICD_INMIRnE registers. Added the GICD_VFCTLR register. Corrected the upper address range of the GICD_CHIPRn registers. Updated the GICD_IVIEWR[1:0] and GICD_ICVERRR0 descriptions because those registers are Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" title="The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.">Distributor registers (GICD/GICDA) summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added CHIPS_UPPER ≠ 0 restriction to the Configuration section.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR, Cross-Chip Control Group Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" title="This register controls the number of outstanding AXI5-Stream transactions to a set of remote chips that are assigned to the same credit group. The GICD_CCCGR register controls the assignment of chips to a credit group.">GICD_CCCCR, Cross-Chip Control Credit Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GICD Virtual Function Control Register.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" title="This register controls the chicken bit functionality in the vICM. You can use GICD_VFCTLR to restrict the vLPI and vSGI buffer size to 1, and restrict the number of cross-chip vSGI tokens.">GICD_VFCTLR, Virtual Function Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GICR_MPAMIDR reset value.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" title="The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.">Redistributor registers for control and physical LPIs summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the Quiescent and Sleep descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER, Power Management Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the PMGmax and PARTIDmax descriptions, because the values they return now depend on the configuration.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPAMIDR--Report-maximum-PARTID-and-PMG-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GICR_PARTIDR.">GICR_MPAMIDR, Report maximum PARTID and PMG Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GITS_PARTIDR.">GITS_MPAMIDR, MPAM ID Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Increased the PMG and PARTID field widths.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PARTIDR--Set-PARTID-and-PMG-Register?lang=en" title="This register sets the Partition ID and PMG values that the Redistributor uses during memory accesses.">GICR_PARTIDR, Set PARTID and PMG Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" title="This register sets the Partition ID and PMG values that the ITS uses during memory accesses.">GITS_PARTIDR, PART ID Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the RDGPO and RDGPD descriptions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" title="This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.">GICR_PWRR, Power Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GICR_INMIR0 and GICR_INMIRnE registers.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en" title="The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.">Redistributor registers for SGIs and PPIs summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the Version value for r2p1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1, Configuration ID1 Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GITS_MPAMIDR reset value.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en" title="The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.">ITS control register summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the ITS Affinity register.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" title="This register returns the ITS affinity when the vPE table is shared with Redistributors.">GITS_MPIDR, ITS Affinity Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Changed the reset value of WO registers from <span class="documents-g.number.hex">0x0</span> to -.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en" title="The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.">FMU register summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about error records 2 and 3, when <code class="documents-parmname">wake_local</code> == 1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" title="This register defines which of the common architecturally defined features are implemented and, of the implemented features, which are software programmable. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR&lt;n&gt;FR, Error Record &lt;n&gt; Feature Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" title="For even error records, this register controls whether the FMU can generate a critical error interrupt. For odd error records, this register controls whether the FMU can generate an error recovery interrupt. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR&lt;n&gt;CTLR, Error Record &lt;n&gt; Control Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS, Error Record &lt;n&gt; Primary Status register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the PAGEID field description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR, Safety Mechanism Page Write Register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD, Safety Mechanism Page Read Register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Increased the INTID_index field width to 12 bits.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the clear_error_DetectionPaused bit in page 2 interrupt protection.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA, Safety Mechanism Write Data register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the DetectionPaused and the BISTBusy bit descriptions in page 1 interrupt protection.<p>Added the error_DetectionPaused, BISTBusy, and error_BIST_valid bits in page 2 interrupt protection.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA, Safety Mechanism Read Data register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the GSPV error recovery description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.gspv_error_recovery_r2p1">GSPV error recovery</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the interrupt protection initialization description.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Updated the powerup sequence when CRC protection is enabled on the cross-chip interface.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Isolating-a-chip-from-the-system?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Isolating-a-chip-from-the-system?lang=en" title="In a multichip system, you can isolate a chip from the system.">Isolating a chip from the system</a></td>
</tr>
</tbody>
</table>





<table id="giu1630663327295__table.r2p1_safety_2nd_release">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 12. </span>Differences between issue 0201-11 and issue 0201-12</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d121698e2899" rowspan="1">Change</th>
<th class="documents-cell-norowborder" colspan="1" id="d121698e2902" rowspan="1">Location</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about interrupt corruption when SPI Collators overlap.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator/Using-multiple-SPI-Collators?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/Using-multiple-SPI-Collators?lang=en" title="If a GIC configuration uses multiple SPI Collators, then the SPI_BASE value must be set so that the SPI wires do not overlap.">Using multiple SPI Collators</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added information about software clearing the LPI memory tables.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/LPIs/LPI-programming-and-generation?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/LPIs/LPI-programming-and-generation?lang=en" title="Only an ITS can generate an LPI. See Learn the architecture - Generic Interrupt Controller v3 and v4, LPIs for more information.">LPI programming and generation</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the fault_int, err_int, fmu_cri, and fmu_eri signals to show that they are level-sensitive outputs.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-recovery-and-fault-handling-interrupts?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-recovery-and-fault-handling-interrupts?lang=en" title="You can assign a recorded correctable ECC error to the fault handling interrupt by setting GICT_ERR&lt;n&gt;CTLR.CFI.">Error recovery and fault handling interrupts</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" title="This section describes how the GIC blocks can signal errors, and how the FMU reports these errors.">Error signaling</a></li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the description of the CC_CREDIT field.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" title="This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.">GICD_CCCTLR, Cross-Chip Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the address of the GICR_VFCTLR, GICR_VCFGBASER, and GICR_VINVCHIPR registers.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en" title="The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.">vLPI register summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Corrected the reset value of GICT_PIDR2.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en" title="The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.">GICT register summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the QDENY bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-FCTLR--Function-Control-Register?lang=en" title="This register controls clock gating of the FMU, and whether it always denies a Q-Channel quiescence request.">FMU_FCTLR, Function Control Register</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Updated the ERI and CRI interrupts to state that they are disabled at reset.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Error-signaling?lang=en" title="This section describes how the GIC blocks can signal errors, and how the FMU reports these errors.">Error signaling</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Added the GICR_VIEWR and GICR_FLUSHR registers.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" title="The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.">Redistributor registers for control and physical LPIs summary</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Deleted the <cite>Error record bank, by view</cite> column.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view">GICT_ERR&lt;n&gt;MISC0.Data field encoding</a></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Added information about manager restrictions on attributes.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/MSI-64-Encapsulator?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/MSI-64-Encapsulator?lang=en" title="The MSI-64 Encapsulator reduces system wiring by combining the DeviceID onto the data bus for writes to the GITS_TRANSLATER register.">MSI-64 Encapsulator</a></td>
</tr>
</tbody>
</table>
