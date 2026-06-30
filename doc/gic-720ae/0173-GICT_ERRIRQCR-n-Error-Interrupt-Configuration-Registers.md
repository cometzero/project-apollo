# GICT_ERRIRQCR<n>, Error Interrupt Configuration Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRIRQCR-n---Error-Interrupt-Configuration-Registers>

### GICT\_ERRIRQCR<n>, Error Interrupt Configuration Registers

GICT\_ERRIRQCR0 controls which SPI is generated when a fault handling interrupt occurs. GICT\_ERRIRQCR1 controls which SPI is generated when an error recovery interrupt occurs.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICT\_ERRIRQCR<n> bit assignments

![GICT_ERRIRQCR<n> bit assignments](images/0173-GICT_ERRIRQCR-n-Error-Interrupt-Configuration-Registers-img01.svg)



<table id="col1468851908653__tbl.gict_errirqcr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERRIRQCR&lt;n&gt; bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d88990e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d88990e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d88990e136" rowspan="1">Description</th>
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
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the SPI ID that the GIC generates when a fault handling interrupt occurs (&lt;n&gt;==0) or when an error recovery interrupt occurs (&lt;n&gt;==1).<p>If the value is less than 32, out of range, or not owned on chip for multichip configurations, the register updates to 0 and no internal delivery occurs.</p> <p>Set this field to 0 when the interrupt routes externally to a core that does not receive interrupts directly from the GIC such as a central system control processor.</p>
<blockquote id="col1468851908653__note_w607ab1b7b7c10b3b3b7b5b3_w608ab1b7b7c10b3b3b7b5_w609ab1b7b7c10b3b3b7_w610ab1b7b7c10b3b3_w611ab1b7b7c10b3_w612ab1b7b7c10_w613ab1b7b7_w614ab1b7_w615ab1" title="Note info">
<h3 class="documents-underline">Note</h3> The behavior is unpredictable if software attempts to share the same interrupt ID in GICT_ERRIRQCRn with an external source using either:

           <ul>
<li>An SPI wire.</li>
<li>The GICD_SETSPI_NSR or GICD_SETSPI_SR registers.</li>
</ul>
</blockquote> <p>In a multichip configuration, only program the SPIID field to an SPI ID that the chip owns. The relevant <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en" title="Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.">GICD_CHIPRn</a> register controls the SPI ownership.</p> <p>We recommend that if these registers are used, then the SPI must not be used for another device, either with a wire or as a message-based interrupt.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERRIRQCR<n> is accessible only by Secure accesses.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, GICT\_ERRIRQCR<n> is accessible for view 0 only.
