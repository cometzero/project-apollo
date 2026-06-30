# GICT register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary>

### GICT register summary

The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.

All registers comply with the [Arm® Reliability, Availability, and Serviceability (RAS) System Architecture for A-profile architecture](https://developer.arm.com/documentation/ihi0100/latest), except for the GICT\_PIDR\* and GICT\_CIDR\* registers.

> ### Note
>
> The
> [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS bit controls whether Non-secure software can access the GICT registers.



<table id="col1468572954224__tbl.gict_register_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT register summary</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d101958e101" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d101958e104" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d101958e107" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d101958e110" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d101958e113" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d101958e117" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-FR--Error-Record-Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-FR--Error-Record-Feature-Register?lang=en" title="This register returns information about the Armv8.2 RAS features that the GIC-720AE implements.">GICT_ERR&lt;n&gt;FR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Record dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Feature Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0008</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" title="This register controls how interrupts are handled.">GICT_ERR&lt;n&gt;CTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Control Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0010</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Record dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Primary Status register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0018</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR&lt;n&gt;ADDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unknown</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Address Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.">GICT_ERR&lt;n&gt;MISC0</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unknown</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Miscellaneous Register 0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0028</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" title="This register contains the data value of an uncorrectable error in the LPI RAM, TGT_LPI RAM, or ITS software information. The register is not present for other error records.">GICT_ERR&lt;n&gt;MISC1</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unknown</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record Miscellaneous Register 1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRGSR--Error-Group-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRGSR--Error-Group-Status-Register?lang=en" title="This register shows the status of the GIC-720AE Armv8.2 RAS architecture-compliant error records for correctable and uncorrectable RAM ECC errors, ITS command and translation errors, and uncorrectable software errors.">GICT_ERRGSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Group Status Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE008</span>- <span class="documents-g.number.hex">0xE0FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-IIDR--Trace-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the trace page.">GICT_IIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x070nn43B</span><p>The <code>nn</code> value depends on the r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Trace Implementer Identification Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE104</span>- <span class="documents-g.number.hex">0xE7FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE800</span>- <span class="documents-g.number.hex">0xE808</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRIRQCR-n---Error-Interrupt-Configuration-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRIRQCR-n---Error-Interrupt-Configuration-Registers?lang=en" title="GICT_ERRIRQCR0 controls which SPI is generated when a fault handling interrupt occurs. GICT_ERRIRQCR1 controls which SPI is generated when an error recovery interrupt occurs.">GICT_ERRIRQCR&lt;n&gt;</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Interrupt Configuration Registers</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE810</span>- <span class="documents-g.number.hex">0xFFB8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFBC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_DEVARCH</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x47700A00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Device Architecture register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFC0</span>- <span class="documents-g.number.hex">0xFFC4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFC8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-DEVID--Device-Configuration-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-DEVID--Device-Configuration-register?lang=en" title="This register returns information about the configuration of the GIC-720AE GICT such as whether an LPI or ITS is available.">GICT_DEVID</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Device Configuration register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 4 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 5 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 6 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 7 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x95</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 0 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 1 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-PIDR2--Peripheral-ID2-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-PIDR2--Peripheral-ID2-Register?lang=en" title="This register returns byte[2] of the peripheral ID. The GICT_PIDR2 register is part of the set of trace and debug peripheral identification registers.">GICT_PIDR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 2 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_PIDR3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 3 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 0 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 1 register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICT_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 2 register</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICT_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Component ID 3 register</td>
</tr>
</tbody>
</table>
