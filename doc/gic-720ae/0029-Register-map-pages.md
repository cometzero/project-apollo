# Register map pages

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages>

### Register map pages

The GIC-720AE address map has multiple pages. The number of pages and the address aliasing depends on the GIC configuration.

The registers in the following table are accessible through the ACE5-Lite interface. For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then each view sees the register map pages that the table shows.

The Fault Management Unit (FMU) registers are accessible through the APB5 interface. See:

- [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.")
- [FMU APB5 interface](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/FMU-APB5-interface?lang=en "The programmer view registers inside the FMU are accessible through an APB5 interface that is protected with AMBA parity extensions.")



<table id="bak1489161065998__table.register_pages">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Register map pages</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="2" id="d45301e125" rowspan="1">Page offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d45301e128" rowspan="2">Page</th>
<th class="documents-cell-norowborder" colspan="1" id="d45301e131" rowspan="2">Description</th>
</tr>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d45301e137" rowspan="1">No v4.1 support</th>
<th class="documents-cell-norowborder" colspan="1" id="d45301e140" rowspan="1">With v4.1 support</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="2" rowspan="1">0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en" title="The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.">GICD main page</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="2" rowspan="1">1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary?lang=en" title="The functions for the GIC-720AE message-based SPIs are controlled through the Distributor registers identified with the prefix GICM.">GICM message-based interrupts</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="2" rowspan="1">2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en" title="The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.">GIC trace and debug page</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="2" rowspan="1">3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary?lang=en" title="The GIC-720AE Performance Monitoring Unit functions are controlled through registers that are identified with the prefix GICP.">GIC PMU page</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">4 + 2×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">4 + 4×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en" title="The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.">ITS address page</a>.<p>ITSnum is the serial number of each ITS, which is from 0 to ITScount−1.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">5 + 2×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">5 + 4×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS (translate)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-translation-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-translation-register-summary?lang=en" title="Interrupts to be translated by the GIC-720AE Interrupt Translation Service (ITS) are identified by EventIDs that are written to GITS_TRANSLATER, the ITS Translation Register.">ITS translation page</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">6 + 4×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS (vSGI)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-vSGI-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-vSGI-register-summary?lang=en" title="Virtual SGIs to be injected directly into a virtual machine are written to the ITS translation register GITS_SGIR.">ITS vSGI page</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">7 + 4×ITSnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">4 + 2×ITScount + 2×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">4 + 4×ITScount + 4×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR (LPI)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en" title="The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.">GICR LPI registers</a>.<p>ITScount is the total number of ITS.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">5 + 2×ITScount + 2×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">5 + 4×ITScount + 4×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR (SGI)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary?lang=en" title="The functions for the GIC-720AE SGIs and PPIs are controlled through the Redistributor registers identified with the prefix GICR.">GICR PPI + SGI registers</a>.<p>RDnum is the serial number of each <span class="documents-q">“internal Redistributor”</span>, which is from 0 to RDcount−1.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">6 + 4×ITScount + 4×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICR (vLPI)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en" title="The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.">GICR vLPI registers</a></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">7 + 4×ITScount + 4×RDnum</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">4 + 2×ITScount + 2×RDcount</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">4 + 4×ITScount + 4×RDcount</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICDA</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Alias to GICD (page after last GICR page).<p>RDcount is the total number of <span class="documents-q">“internal Redistributors”</span>, which equals total number of CPU cores.</p> <p>RDcount can change if the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" title="Each register allows Secure software to remove up to 64 cores from the GIC.">GICD_RDOFFRn</a> registers or the <span class="documents-g.signal.name"><span class="documents-keyword">gicd_pe_off</span></span> tie-off signal removes Redistributors. In this case, the GICDA page moves to the page above the last Redistributor.</p> </td>
</tr>
</tbody>
</table>



For more information, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).

You must set up the system address map so that each core accesses the GICD page on its local chip at the same address. All other pages must be globally accessible, although access of pages on a remote chip by a core is expected to be rare. Allowing the GIC pages to be globally accessible might require the system interconnect to alias the page addresses.

For multichip configurations, if the cross-chip traffic uses an ACE5-Lite interface ([GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 1), then the ACE5-Lite subordinate interface has a single 64KB page, or two 64KB pages if CRC is enabled. Each GICD must be at a unique address location that is accessible from any other GICD.

### Page offset

The ACE5-Lite address bits[`x`:16] control which GIC register page is accessed in [Register map pages](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages?lang=en#bak1489161065998__table.register_pages). The value of `x` depends on the `axis_addr_width` GICD configuration parameter.

In non-monolithic configurations, the GIC-720AE ignores address bits above ceil[log2(page\_count)] + 15. For example, a configuration that uses 11 pages ignores address bits above 19, so any address bits of the form 0xXXXXX00000 is accepted and it accesses the GICD page.

In monolithic configurations, where the Distributor and ITS share the ACE5-Lite subordinate port, the gicd\_page\_offset and its\_transr\_page\_offset address tie-off signals control the full page address of the GICD and GITS\_TRANSLATER pages. The page address comprises address bits[`x`:16]. For example, if the GICD page is at 32-bit address 0xFFFF0000, the gicd\_page\_offset tie-off is 16-bit 0xFFFF.

In multi view configurations, the two address bits that are higher than those that identify all the pages in a particular view are used as a view identifier. For example, if a view has 16 pages, then it requires 4 bits to address those pages. Therefore, address bits[21:20] are used to select a view.
