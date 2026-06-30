# Distributor registers (GICD/GICDA) summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary>

### Distributor registers (GICD/GICDA) summary

The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.

The following table lists the Distributor registers in base offset order and provides a reference to the register description that is described in either this document or the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).

Address offsets are relative to the Distributor base address defined by the system memory map.

Offsets that are not shown or are marked as reserved, are Reserved and RAZ/WI. Accesses to these offsets might be reported in error record 0 as a SYN\_ACE\_BAD access.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, the accessibility of a GICD register depends on the view. See [Multi view access to the GICD registers](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en#iik1489161020206__section.multiview_access_to_the_GICD_registers) for information about the views that a register is accessible in.



<table id="iik1489161020206__tbl.distributor_registers_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Distributor registers (GICD/GICDA) summary</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d71992e105" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e108" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e111" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e114" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e117" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e121" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d71992e124" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Controller Type Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Distributor.">GICD_IIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x070nn43B</span><p>The <code>nn</code> value depends on the r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor Implementer Identification Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x000C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER2--Interrupt-Controller-Type-Register-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER2--Interrupt-Controller-Type-Register-2?lang=en" title="This register returns the number of bits that GIC-720AE uses for a vPEID.">GICD_TYPER2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Controller Type 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0010</span>- <span class="documents-g.number.hex">0x001C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR--Function-Control-Register?lang=en" title="This register controls non-architectural functionality such as the scrubbing of all RAMs in the local Distributor. The register is not distributed and acts only on the local chip.">GICD_FCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Function Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0024</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" title="This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.">GICD_SAC</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Tie-off signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Secure Access Control register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0028</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cross-Chip Control Group Register. Only present for multichip configurations when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.ACE_CC == 0 and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.CHIPS_UPPER == 0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x002C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" title="This register controls the number of outstanding AXI5-Stream transactions to a set of remote chips that are assigned to the same credit group. The GICD_CCCGR register controls the assignment of chips to a credit group.">GICD_CCCCR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cross-Chip Control Credit Register. Only present for multichip configurations when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.ACE_CC == 0 and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.CHIPS_UPPER == 0.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0030</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" title="This register controls clock gating and other non-architectural controls in the local Distributor. The register is not distributed and acts only on the local chip.">GICD_FCTLR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Function Control Register 2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0034</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-UTILR--Utilization-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-UTILR--Utilization-Register?lang=en" title="This register controls the utilization engine in the LPI caches. The register is not distributed and acts only on the local chip.">GICD_UTILR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Utilization Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0038</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3?lang=en" title="This register allows software to set some limitations on the cross-chip AXI5-Stream communications. The register is not distributed and acts only on the local chip. The GIC ignores this register for cross-chip ACE5-Lite communications, that is, when GICD_CFGID.ACE_CC == 1.">GICD_FCTLR3</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x9F</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Function Control Register 3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x003C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" title="This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.">GICD_CCCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cross-Chip Control Register. Only present when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.ACE_CC == 1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0040</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_SETSPI_NSR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-secure SPI Set Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0044</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0048</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CLRSPI_NSR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-secure SPI Clear Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x004C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0050</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_SETSPI_SR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Secure SPI Set Register. Only present when Security support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0054</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0058</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CLRSPI_SR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Secure SPI Clear Register. Only present when Security support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x005C</span>- <span class="documents-g.number.hex">0x007C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080</span>- <span class="documents-g.number.hex">0x00FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGROUPRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0100</span>- <span class="documents-g.number.hex">0x017C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISENABLERn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Enable Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0180</span>- <span class="documents-g.number.hex">0x01FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICENABLERn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Enable Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0200</span>- <span class="documents-g.number.hex">0x027C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISPENDRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Pending Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0280</span>- <span class="documents-g.number.hex">0x02FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICPENDRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Pending Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0300</span>- <span class="documents-g.number.hex">0x037C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISACTIVERn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Active Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0380</span>- <span class="documents-g.number.hex">0x03FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICACTIVERn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Active Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0400</span>- <span class="documents-g.number.hex">0x07FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IPRIORITYRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Security dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Priority Registers, n = 0-255, but n=0-7 are Reserved when affinity routing is enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0800</span>- <span class="documents-g.number.hex">0x0BFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0C00</span>- <span class="documents-g.number.hex">0x0CFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICFGRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Configuration Registers, n = 0-63, but n=0-1 are Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D00</span>- <span class="documents-g.number.hex">0x0D7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGRPMODRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Modifier Registers, n = 0-31, but n=0 is Reserved. If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a>.DS == 1, then this register is RAZ/WI.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D80</span>- <span class="documents-g.number.hex">0x0DFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0E00</span>- <span class="documents-g.number.hex">0x0EFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_NSACRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-secure Access Control Registers, n = 0-63, but n=0-1 are Reserved when affinity routing is enabled. Only present when Security support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0F00</span>- <span class="documents-g.number.hex">0x0F7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0F80</span>- <span class="documents-g.number.hex">0x0FFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_INMIRn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿Non-maskable Interrupt Registers, n = 0-31. Only present when ﻿<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.NMI==1, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1000</span>- <span class="documents-g.number.hex">0x107C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGROUPRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1080</span>- <span class="documents-g.number.hex">0x11FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1200</span>- <span class="documents-g.number.hex">0x127C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISENABLERnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Enable Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1280</span>- <span class="documents-g.number.hex">0x13FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1400</span>- <span class="documents-g.number.hex">0x147C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICENABLERnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Enable Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1480</span>- <span class="documents-g.number.hex">0x15FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1600</span>- <span class="documents-g.number.hex">0x167C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISPENDRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Pending Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1680</span>- <span class="documents-g.number.hex">0x17FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1800</span>- <span class="documents-g.number.hex">0x187C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICPENDRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI signal dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Pending Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1880</span>- <span class="documents-g.number.hex">0x19FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1A00</span>- <span class="documents-g.number.hex">0x1A7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISACTIVERnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set-Active Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1A80</span>- <span class="documents-g.number.hex">0x1BFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1C00</span>- <span class="documents-g.number.hex">0x1C7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICACTIVERnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear-Active Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1C80</span>- <span class="documents-g.number.hex">0x1FFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2000</span>- <span class="documents-g.number.hex">0x23FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IPRIORITYRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Priority Registers Extended, n = 0-255. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2400</span>- <span class="documents-g.number.hex">0x2FFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3000</span>- <span class="documents-g.number.hex">0x30FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICFGRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Configuration Registers Extended, n = 0-63. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3100</span>- <span class="documents-g.number.hex">0x33FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3400</span>- <span class="documents-g.number.hex">0x347C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGRPMODRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Group Modifier Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved. If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a>.DS == 1, then this register is RAZ/WI.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3480</span>- <span class="documents-g.number.hex">0x35FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3600</span>- <span class="documents-g.number.hex">0x36FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_NSACRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-secure Access Control Registers Extended, n = 0-63. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3700</span>- <span class="documents-g.number.hex">0x3AFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3B00</span>- <span class="documents-g.number.hex">0x3B7C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_INMIRnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿Non-maskable Interrupt Registers Extended, n = 0-31. Only present when ﻿&gt; 960 SPIs and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.NMI==1, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3B80</span>- <span class="documents-g.number.hex">0x5FFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6000</span>- <span class="documents-g.number.hex">0x7FF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IROUTERn</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080000000</span> if configured.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Routing Registers, n = 0-991, but n=0-31 are Reserved when affinity routing is enabled.<p>See the <a href="https://developer.arm.com/documentation/198123/latest" target="_blank"><span><cite>Learn the architecture - Generic Interrupt Controller v3 and v4, Overview</cite></span></a>.</p> <p>All SPIs are reset with Interrupt_Routing_Mode == 1. The first register is GICD_IROUTER32, at address <span class="documents-g.number.hex">0x6100</span>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8000</span>- <span class="documents-g.number.hex">0x9FF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IROUTERnE</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Routing Registers Extended, n = 0-1023. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xA000</span>- <span class="documents-g.number.hex">0xBFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en" title="This register returns the status of the chip in a multichip configuration. A single copy of this register exists on each chip in a multichip configuration.">GICD_CHIPSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">P-Channel dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Chip Status Register. Reserved in single-chip configurations.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en" title="This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.">GICD_DCHIPR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Default Chip Register. Reserved in single-chip configurations.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC008</span>- <span class="documents-g.number.hex">0xC200</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Chip Registers, n = 0-63. Reserved in single-chip configurations.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC208</span>- <span class="documents-g.number.hex">0xC7FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC800</span>- <span class="documents-g.number.hex">0xC838</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" title="Each register allows Secure software to remove up to 64 cores from the GIC.">GICD_RDOFFRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor Off Registers, n = 0-7. Only present when <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.RDC == 1.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC840</span>- <span class="documents-g.number.hex">0xD010</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD014</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" title="This register controls the chicken bit functionality in the vICM. You can use GICD_VFCTLR to restrict the vLPI and vSGI buffer size to 1, and restrict the number of cross-chip vSGI tokens.">GICD_VFCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Copy of GICR_VFCTLR. Only present when no local redistributors.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD018</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" title="This register returns the access attributes of the vPE Configuration table.">GICD_VCFGBASER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Copy of GICR_VCFGBASER. Only present when no local redistributors.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD020</span>- <span class="documents-g.number.hex">0xD05C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD060</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" title="This register allows software to put the virtual ITS Communication Module (vICM) to sleep and drain interrupts and programming out of the GICD.">GICD_VSLEEPR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vICM Sleep Register. Only present when no local redistributors.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD064</span>- <span class="documents-g.number.hex">0xDFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE000</span>- <span class="documents-g.number.hex">0xE0FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers?lang=en" title="These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_ICLAR2-GICD_ICLAR61.">GICD_ICLARn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Class Registers, n = 0-63, but n=0-1 are Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE100</span>- <span class="documents-g.number.hex">0xE17C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRn--Interrupt-Clear-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRn--Interrupt-Clear-Error-Registers?lang=en" title="These registers can clear the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICERRR1-GICD_ICERRR30.">GICD_ICERRRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Error Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE180</span>- <span class="documents-g.number.hex">0xE1FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" title="These registers can clear the error status of the GICD_IGROUPRn, GICD_IGRPMODRn, and GICD_NSACRn registers of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICGERR1-GICD_ICGERR30.">GICD_ICGERRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Group Error registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE200</span>- <span class="documents-g.number.hex">0xE27C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRn--Interrupt-Set-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRn--Interrupt-Set-Error-Registers?lang=en" title="These registers can set the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ISERRR1-GICD_ISERRR30. Software can use these registers to test the operation of its interrupt error clear function.">GICD_ISERRRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set Error Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE280</span>- <span class="documents-g.number.hex">0xE2FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE400</span>- <span class="documents-g.number.hex">0xE47C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRnE--Interrupt-Clear-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRnE--Interrupt-Clear-Error-Registers-Extended?lang=en" title="These registers can clear the error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICERRR0E-GICD_ICERRR31E.">GICD_ICERRRnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Error Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE480</span>- <span class="documents-g.number.hex">0xE5FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE600</span>- <span class="documents-g.number.hex">0xE67C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" title="These registers can clear the error status of the GICD_IGROUPRnE, GICD_IGRPMODRnE, and GICD_NSACRnE registers of an SPI, or it returns the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICGERR0E-GICD_ICGERR31E.">GICD_ICGERRnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear Group Error registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE680</span>- <span class="documents-g.number.hex">0xE7FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE800</span>- <span class="documents-g.number.hex">0xE87C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRnE--Interrupt-Set-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRnE--Interrupt-Set-Error-Registers-Extended?lang=en" title="These registers can set the error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 extended registers, GICD_ISERRR0E-GICD_ISERRR31E. Software can use these registers to test the operation of its interrupt error clear function.">GICD_ISERRRnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Set Error Registers Extended, n = 0-31. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE880</span>- <span class="documents-g.number.hex">0xE9FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xEA00</span>- <span class="documents-g.number.hex">0xEA78</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" title="This register can insert errors into the internal RAMs. You can use this register to test your error recovery software.">GICD_ERRINSRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Error Insertion Registers, n = 0-15</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xEA78</span>- <span class="documents-g.number.hex">0xEBFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xEC00</span>- <span class="documents-g.number.hex">0xECFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARnE--Interrupt-Class-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARnE--Interrupt-Class-Registers-Extended?lang=en" title="These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_ICLAR0E-GICD_ICLAR63E.">GICD_ICLARnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Class Registers Extended, n = 0-63. Only present when &gt; 960 SPIs, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xED00</span>- <span class="documents-g.number.hex">0xEFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration ID Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF008</span>- <span class="documents-g.number.hex">0xF1FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF200</span>- <span class="documents-g.number.hex">0xF27C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" title="These registers can clear the view error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICVERRR1-GICD_ICVERRR30.">GICD_ICVERRRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear View Error Registers, n = 0-31, but n=0 is Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF280</span>- <span class="documents-g.number.hex">0xF3FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF400</span>- <span class="documents-g.number.hex">0xF47C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" title="These registers can clear the view error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICVERRR0E-GICD_ICVERRR31E.">GICD_ICVERRRnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt Clear View Error Registers Extended</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF480</span>- <span class="documents-g.number.hex">0xF5FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF600</span>- <span class="documents-g.number.hex">0xF6FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt View Registers, n = 0-63, but n=0-1 are Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF700</span>- <span class="documents-g.number.hex">0xF7FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF800</span>- <span class="documents-g.number.hex">0xF8FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt View Registers Extended</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF900</span>- <span class="documents-g.number.hex">0xFFCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" title="This register returns byte[4] of the peripheral ID. The GICD_PIDR4 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR4</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 4 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 5 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 6 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 7 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" title="This register returns byte[0] of the peripheral ID. The GICD_PIDR0 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR0</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x92</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" title="This register returns byte[1] of the peripheral ID. The GICD_PIDR1 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR1</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICD_PIDR2 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR3--Peripheral-ID3-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR3--Peripheral-ID3-register?lang=en" title="This register returns byte[3] of the peripheral ID. The GICD_PIDR3 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR3</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 3 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICD_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Component ID 3 Register</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Yes</td>
</tr>
</tbody>
</table>



### Multi view access to the GICD registers

The following table shows the views that a GICD register is accessible in.



<table id="iik1489161020206__tbl.distributor_registers_summary_multiview">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>Multi view access to the Distributor registers</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d71992e3746" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d71992e3749" rowspan="1">View</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en" title="This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.">GICD_CTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Banked</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Banked</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IIDR--Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the Distributor.">GICD_IIDR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER2--Interrupt-Controller-Type-Register-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER2--Interrupt-Controller-Type-Register-2?lang=en" title="This register returns the number of bits that GIC-720AE uses for a vPEID.">GICD_TYPER2</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR--Function-Control-Register?lang=en" title="This register controls non-architectural functionality such as the scrubbing of all RAMs in the local Distributor. The register is not distributed and acts only on the local chip.">GICD_FCTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en" title="This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.">GICD_SAC</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register?lang=en" title="This register controls the number of outstanding AXI5-Stream transactions to a set of remote chips that are assigned to the same credit group. The GICD_CCCGR register controls the assignment of chips to a credit group.">GICD_CCCCR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" title="This register controls clock gating and other non-architectural controls in the local Distributor. The register is not distributed and acts only on the local chip.">GICD_FCTLR2</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">See register for more information.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-UTILR--Utilization-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-UTILR--Utilization-Register?lang=en" title="This register controls the utilization engine in the LPI caches. The register is not distributed and acts only on the local chip.">GICD_UTILR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3?lang=en" title="This register allows software to set some limitations on the cross-chip AXI5-Stream communications. The register is not distributed and acts only on the local chip. The GIC ignores this register for cross-chip ACE5-Lite communications, that is, when GICD_CFGID.ACE_CC == 1.">GICD_FCTLR3</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en" title="This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.">GICD_CCCTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_SETSPI_NSR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CLRSPI_NSR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_SETSPI_SR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CLRSPI_SR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGROUPRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISENABLERn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICENABLERn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISPENDRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICPENDRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISACTIVERn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICACTIVERn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IPRIORITYRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICFGRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGRPMODRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_NSACRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_INMIRn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGROUPRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISENABLERnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICENABLERnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISPENDRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICPENDRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ISACTIVERnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICACTIVERnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IPRIORITYRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_ICFGRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IGRPMODRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_NSACRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_INMIRnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IROUTERn</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_IROUTERnE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en" title="This register returns the status of the chip in a multichip configuration. A single copy of this register exists on each chip in a multichip configuration.">GICD_CHIPSR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en" title="This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.">GICD_DCHIPR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en" title="Each register allows Secure software to remove up to 64 cores from the GIC.">GICD_RDOFFRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VFCTLR--Virtual-Function-Control-Register?lang=en" title="This register controls the chicken bit functionality in the vICM. You can use GICD_VFCTLR to restrict the vLPI and vSGI buffer size to 1, and restrict the number of cross-chip vSGI tokens.">GICD_VFCTLR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" title="This register returns the access attributes of the vPE Configuration table.">GICD_VCFGBASER</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-VSLEEPR--vICM-Sleep-Register?lang=en" title="This register allows software to put the virtual ITS Communication Module (vICM) to sleep and drain interrupts and programming out of the GICD.">GICD_VSLEEPR</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers?lang=en" title="These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_ICLAR2-GICD_ICLAR61.">GICD_ICLARn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRn--Interrupt-Clear-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRn--Interrupt-Clear-Error-Registers?lang=en" title="These registers can clear the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICERRR1-GICD_ICERRR30.">GICD_ICERRRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" title="These registers can clear the error status of the GICD_IGROUPRn, GICD_IGRPMODRn, and GICD_NSACRn registers of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICGERR1-GICD_ICGERR30.">GICD_ICGERRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRn--Interrupt-Set-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRn--Interrupt-Set-Error-Registers?lang=en" title="These registers can set the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ISERRR1-GICD_ISERRR30. Software can use these registers to test the operation of its interrupt error clear function.">GICD_ISERRRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRnE--Interrupt-Clear-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRnE--Interrupt-Clear-Error-Registers-Extended?lang=en" title="These registers can clear the error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICERRR0E-GICD_ICERRR31E.">GICD_ICERRRnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" title="These registers can clear the error status of the GICD_IGROUPRnE, GICD_IGRPMODRnE, and GICD_NSACRnE registers of an SPI, or it returns the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICGERR0E-GICD_ICGERR31E.">GICD_ICGERRnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRnE--Interrupt-Set-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRnE--Interrupt-Set-Error-Registers-Extended?lang=en" title="These registers can set the error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 extended registers, GICD_ISERRR0E-GICD_ISERRR31E. Software can use these registers to test the operation of its interrupt error clear function.">GICD_ISERRRnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" title="This register can insert errors into the internal RAMs. You can use this register to test your error recovery software.">GICD_ERRINSRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARnE--Interrupt-Class-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARnE--Interrupt-Class-Registers-Extended?lang=en" title="These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_ICLAR0E-GICD_ICLAR63E.">GICD_ICLARnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and the view that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a> sets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Banked, see register for more information.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRn--Interrupt-Clear-View-Error-Registers?lang=en" title="These registers can clear the view error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICVERRR1-GICD_ICVERRR30.">GICD_ICVERRRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICVERRRnE--Interrupt-Clear-View-Error-Registers-Extended?lang=en" title="These registers can clear the view error status of an SPI in the extended SPI range, or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICVERRR0E-GICD_ICVERRR31E.">GICD_ICVERRRnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRn--Interrupt-View-Registers?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_IVIEWR2-GICD_IVIEWR61.">GICD_IVIEWRn</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended?lang=en" title="These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_IVIEWR0E-GICD_IVIEWR63E.">GICD_IVIEWRnE</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR4--Peripheral-ID4-register?lang=en" title="This register returns byte[4] of the peripheral ID. The GICD_PIDR4 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR4</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR5</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR6</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_PIDR7</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR0--Peripheral-ID0-register?lang=en" title="This register returns byte[0] of the peripheral ID. The GICD_PIDR0 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR0</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR1--Peripheral-ID1-register?lang=en" title="This register returns byte[1] of the peripheral ID. The GICD_PIDR1 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR1</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR2--Peripheral-ID2-register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICD_PIDR2 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR2</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR3--Peripheral-ID3-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-PIDR3--Peripheral-ID3-register?lang=en" title="This register returns byte[3] of the peripheral ID. The GICD_PIDR3 register is part of the set of Distributor peripheral identification registers.">GICD_PIDR3</a></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICD_CIDR2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICD_CIDR3</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
</tbody>
</table>
