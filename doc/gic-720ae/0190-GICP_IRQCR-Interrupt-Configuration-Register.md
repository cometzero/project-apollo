# GICP_IRQCR, Interrupt Configuration Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-IRQCR--Interrupt-Configuration-Register>

### GICP\_IRQCR, Interrupt Configuration Register

This register controls which SPI is generated when a PMU overflow interrupt occurs.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICP register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary?lang=en "The GIC-720AE Performance Monitoring Unit functions are controlled through registers that are identified with the prefix GICP.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICP\_IRQCR bit assignments

![GICP_IRQCR bit assignments](images/0190-GICP_IRQCR-Interrupt-Configuration-Register-img01.svg)



<table id="atm1469206024122__tbl.gicp_irqcr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_IRQCR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d98110e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d98110e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d98110e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[10:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SPIID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the SPI ID that the GIC generates when a PMU overflow interrupt occurs.<p>If the value is less than 32, out of range, or not owned on chip for multichip configurations, the register updates to 0 and no internal delivery occurs.</p> <p>Set this field to 0 when the interrupt routes externally to a core that does not receive interrupts directly from the GIC such as a central system control processor.</p>
<blockquote id="atm1469206024122__note_w703ab1b7b7c10b3b3b7b5b3_w704ab1b7b7c10b3b3b7b5_w705ab1b7b7c10b3b3b7_w706ab1b7b7c10b3b3_w707ab1b7b7c10b3_w708ab1b7b7c10_w709ab1b7b7_w710ab1b7_w711ab1" title="Note info">
<h3 class="documents-underline">Note</h3> The behavior is unpredictable if software attempts to share the same interrupt ID in GICP_IRQCR with an external source using either:

           <ul>
<li>An SPI wire.</li>
<li>The GICD_SETSPI_NSR or GICD_SETSPI_SR registers.</li>
</ul>
</blockquote> <p>Creates a level-triggered interrupt<span> if it is owned on chip</span>. Otherwise it behaves as a normal message-based SPI.</p> <p>In a multichip configuration, the SPIID field must be programmed only to an SPI ID that the chip owns. The relevant <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPRn</a> register controls the SPI ownership.</p> <p>We recommend that if these registers are used, then the SPI must not be used for another device either with a wire or as a message-based interrupt.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_IRQCR is accessible only by Secure accesses.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then GICP\_IRQCR is accessible only for view 0.
