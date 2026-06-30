# FMU register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary>

### FMU register summary

The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.

Unless otherwise stated in the accompanying FMU register descriptions:

- Do not modify Reserved register bits.
- Ignore Reserved register bits on reads.



<table id="yui1524760614758__tbl.fmu_register_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU register summary</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d114456e87" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d114456e90" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d114456e93" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d114456e96" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d114456e99" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d114456e103" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x000</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" title="This register defines which of the common architecturally defined features are implemented and, of the implemented features, which are software programmable. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR&lt;n&gt;FR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00000XXX_00000022</span> for odd error records &lt;n&gt;.<p><span class="documents-g.number.hex">0x00000XXX_00800002</span> for even error records &lt;n&gt;.</p> <p>Depending on the GIC block type, bits[43:32] are configuration dependent.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record &lt;n&gt; Feature Register, n = 0-11</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x008</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register?lang=en" title="For even error records, this register controls whether the FMU can generate a critical error interrupt. For odd error records, this register controls whether the FMU can generate an error recovery interrupt. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR&lt;n&gt;CTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record &lt;n&gt; Control Register, n = 0-11</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x010</span> + (n × 64)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Record &lt;n&gt; Primary Status register, n = 0-11</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" title="This register shows the status of all FMU_ERR&lt;n&gt;STATUS.V bits.">FMU_ERRGSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error Group Status Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE10</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRIIDR--FMU-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRIIDR--FMU-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the FMU.">FMU_ERRIIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x49A0043B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Implementation ID Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-register?lang=en" title="This register enables or disables particular protection mechanisms inside a specified GIC block. At reset, the GIC enables all the protection mechanisms. We recommend that software does not disable any protection mechanisms.">FMU_SMEN</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Enable and disable register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF04</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMERR--Safety-Mechanism-Inject-Error-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMERR--Safety-Mechanism-Inject-Error-register?lang=en" title="This register injects one error into the specified protection mechanism inside a GIC block. Writes to this register cause an FMU_CTRL_ACCESS message to be sent with err_insert=1.">FMU_SMERR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Inject Error register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF08</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMCR--Safety-Mechanism-Set-Criticality-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMCR--Safety-Mechanism-Set-Criticality-Register?lang=en" title="This register sets the protection mechanism criticality. When the FMU receives a write access to this register then it sends an FMU_CTRL_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMCR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Set Criticality Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Page Write Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF10</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Write Data register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF14</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Page Read register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF18</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism Read Data register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF1C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.">FMU_STATUS</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">FMU Status register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF20</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-KEY--FMU-Key-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-KEY--FMU-Key-register?lang=en" title="This register receives the unlock key that is required for writes to FMU registers to be successful. This register reads as 0 if the FMU register file is locked.">FMU_KEY</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">FMU Key register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF24</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-TIMEOUT--Timeout-duration-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-TIMEOUT--Timeout-duration-register?lang=en" title="When FMU_STATUS.BUSY == 1, this register controls the duration before the FMU sets FMU_STATUS.TIMEOUT = 1.">FMU_TIMEOUT</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFFFFFF</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Timeout duration register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF28</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRUPDATE--Error-Update-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRUPDATE--Error-Update-register?lang=en" title="This register updates an error record pair FMU_ERR&lt;n&gt;STATUS and FMU_ERR&lt;n+1&gt;STATUS, with all the reported error states. If software clears the FMU_ERR&lt;n&gt;STATUS.OFX bit, then it can use FMU_ERRUPDATE to discover the source of the error that caused the OFX to resend its error.">FMU_ERRUPDATE</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error update register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF2C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-FCTLR--Function-Control-Register?lang=en" title="This register controls clock gating of the FMU, and whether it always denies a Q-Channel quiescence request.">FMU_FCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Function Control Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFBC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_ERRDEVARCH</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">FMU Device Architecture register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFC8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRDEVID--Device-configuration-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERRDEVID--Device-configuration-register?lang=en" title="This register returns the number of error records in the FMU.">FMU_ERRDEVID</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Device configuration register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x04</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 4 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 5 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 6 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 7 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x9A</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 0 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 1 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-PIDR2--Peripheral-ID2-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-PIDR2--Peripheral-ID2-Register?lang=en" title="This register returns byte[2] of the peripheral ID. The FMU_PIDR2 register is part of the peripheral identification registers.">FMU_PIDR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 2 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_PIDR3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Peripheral ID 3 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 0 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 1 Register</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">FMU_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Component ID 2 Register</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">FMU_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Component ID 3 Register</td>
</tr>
</tbody>
</table>
