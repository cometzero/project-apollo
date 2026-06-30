# FMU_SMRDATA, Safety Mechanism Read Data register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register>

### FMU\_SMRDATA, Safety Mechanism Read Data register

This register contains the data that is read during a page read access.

The format of the register depends on which page is being read, by using [FMU\_SMRD](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en "This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.").PAGEID. The number of pages available depends on the protection mechanism:

Page 0
:   Available for all
    protection mechanisms.

Page 1
:   Available for:

    - AXI5-Stream protection, AXI5-Stream cross-chip protection, ACE5-Lite cross-chip protection, and CPU interface (CPUIF) protection.
    - Interrupt protection.

Page 2
:   Available for interrupt protection
    , AXI5-Stream protection, and CPUIF protection.

Page 3 -4
:   Available for CPUIF protection.

### Configurations

This register is available in all configurations.

If a GIC configuration does not include a particular protection type, then software can still perform page accesses to the corresponding PROTIDs. Reads from page 0 return valid data, but reads from page 1 and higher return zeros.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

If [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").PROTID\_ERR == 1, then software must ignore the value of this register.

### Bit descriptions

The bit descriptions depend on the page that is read. Some protection mechanisms provide multiple pages for the status information.

The following table shows the page 0 reads for all protection mechanisms.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_SMRDATA bit descriptions for page 0 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==0)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e242" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e245" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e248" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">inserted</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the error insertion status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No error inserted.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Error inserted.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">critical</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the <span>protection mechanism</span> criticality:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span>protection mechanism</span> reports a non-critical error.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span>protection mechanism</span> reports a critical error.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">enable</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">For <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a>.SMID ≠ 255, this bit returns whether the <span>protection mechanism</span> is enabled:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span>protection mechanism</span> with the ID that SMID contains is not enabled.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span>protection mechanism</span> with the ID that SMID contains is enabled.

           </dd>
</dl> For <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a>.SMID = 255, this bit returns whether the error wire outputs for that block are enabled:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Both error wire outputs for that block are not enabled.

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a>.[BLKTYPE|BLKID] selects the block.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Both error wire outputs for that block are enabled.

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a>.[BLKTYPE|BLKID] selects the block.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
</tbody>
</table>



### Page 1 reads for AXI5-Stream protection and CPUIF protection

Returns the timeout behavior for the CRC protection that the AXI5-Stream interfaces and CPUIFs use.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>FMU_SMRDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e496" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e499" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e502" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SendTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the duration when it becomes a high priority for the block to send a ping or a ping acknowledge packet:

          <ul>
<li>4 × (SendTime + 1) − 1 cycles.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the duration when the block detects a timeout error, because a ping or a ping acknowledge packet is missing:

          <ul>
<li>64 × (ErrTime + 1) − 1 cycles.</li>
</ul> <p>We recommend that the time to error is at least 4 times longer than the time to send a ping or a ping acknowledge packet. However, interconnect delays or the different frequencies of both domains might require this recommendation to be longer.</p> </td>
</tr>
</tbody>
</table>



### Page 1 reads for AXI5-Stream cross-chip protection

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 0, returns the timeout behavior for the CRC protection that an AXI5-Stream cross-chip interface uses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 3. </span>FMU_SMRDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e595" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e598" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e601" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ReadyErrTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the duration for the <span class="documents-g.signal.name"><span class="documents-keyword">TREADY</span></span> timeout. The value is in the range of 12 × ReadyErrTime + 1 to 16 × ReadyErrTime cycles, and depends on what was written using <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a>.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CRCErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the duration when the block detects a timeout error, because a CRC request packet or a CRC acknowledge packet is missing. The value is in the range of 56 × CRCErrTime + 1 to 64 × CRCErrTime cycles, and depends on what was written using <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a>.</td>
</tr>
</tbody>
</table>



### Page 1 reads for ACE5-Lite cross-chip protection

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 1, returns the timeout behavior for the CRC protection that an ACE5-Lite cross-chip interface uses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 4. </span>FMU_SMRDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e699" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e702" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e705" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ReadyErrTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the duration for the <span class="documents-g.signal.name"><span class="documents-keyword">AWREADY</span></span> timeout. The value is in the range of 12 × ReadyErrTime + 1 to 16 × ReadyErrTime cycles, and depends on what was written using <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a>.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CRCErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the duration when the block detects a timeout error, because a CRC request packet or a CRC acknowledge packet is missing. The value is in the range of 56 × CRCErrTime + 1 to 64 × CRCErrTime cycles, and depends on what was written using <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a>.</td>
</tr>
</tbody>
</table>



### Page 1 reads for interrupt protection

If a GIC configuration does not enable interrupt protection for the block being accessed, FMU\_SMRDATA interrupt protection page 1 returns zero and [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").PROTID\_ERR returns 0b0. The `spi_protection_type`, `rlt_spi_protection_type`, and `ppi_protection_type` parameters control whether a configuration supports interrupt protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 5. </span>FMU_SMRDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e811" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e814" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e817" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DetectionPaused</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if error detection is paused for the INTID being read:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Error detection is not paused for the interrupt that INTID selects.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Error detection is paused for the interrupt that INTID selects. This value occurs when software uses

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en" title="This register contains the data that is written during a page write access.">FMU_SMWDATA</a> to program the interrupt that INTID selects. The GIC re-enables error detection, when the interrupt protection detects level consistency over a 16-cycle clock period.

            <p>This value also occurs when the BIST check completes successfully and the interrupt protection initialization starts. See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a> for more information.</p>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">BISTBusy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When the GIC exits reset, this bit is set to 1 for a fixed duration, while the GIC performs BIST for the interrupt protection.<span> This bit has identical functionality to the BISTBusy bit in read page 2, for interrupt protection.</span> See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a> for more information.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enable</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the interrupt protection status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Interrupt protection is disabled for the interrupt that INTID selects.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Interrupt protection is enabled for the interrupt that INTID selects.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EnableTransient</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the transient protection status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Transient protection is disabled for the interrupt that INTID selects.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Transient protection is enabled for the interrupt that INTID selects.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13:<span>12</span>]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[<span>11</span>:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">INTID_index</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the interrupt ID of the PPI or SPI that is read. This value is the wire index for that block of protected interrupts.</td>
</tr>
</tbody>
</table>



### Page 2 reads for AXI5-Stream protection and CPUIF protection

The following table shows the page 2 reads that return the CRC timeout and CRC checksum errors for AXI5-Stream protection and CPUIF protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 6. </span>FMU_SMRDATA bit descriptions for page 2 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==2)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1063" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1066" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e1069" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">crc_timeout_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a CRC timeout error has occurred.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">crc_chksum_err</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">When set to 1, it indicates that a CRC checksum error has occurred.</td>
</tr>
</tbody>
</table>



A stability error on the AXI5-Stream iritdest\_\*\_ crc signal, results in bit[0] being set.

### Page 2 reads for interrupt protection

If a GIC configuration does not enable interrupt protection for the block being accessed, FMU\_SMRDATA interrupt protection page 2 returns zero and [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").PROTID\_ERR returns 0b0. The `spi_protection_type`, `rlt_spi_protection_type`, and `ppi_protection_type` parameters control whether a configuration supports interrupt protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 7. </span>FMU_SMRDATA bit descriptions for page 2 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==2)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1179" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1182" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e1185" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">error_INTID_valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether an INTID-specific error has occurred:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Error valid bit is not set for the reported INTID.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Error valid bit is set for the reported INTID. See

            <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.interrupt_error_recovery" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs/Error-recovery-procedures?lang=en#gtn1540373734160__section.interrupt_error_recovery">Interrupt error recovery</a> for more information about INTID-specific errors.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">error_overflow</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the error overflow bit status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No additional INTIDs have had an error, other than the error that error_INTID reports.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             An error has occurred in one or more different INTIDs, including the error that error_INTID reports.

            <p>Multiple errors on the same INTID do not set error_overflow, but those errors set the OFX, OFB, or OF bit in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Primary-Status-register?lang=en" title="This register indicates information relating to the recorded errors in FMU error record &lt;n&gt;, where n = 0-11.">FMU_ERR&lt;n&gt;STATUS</a>.</p>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DetectionPaused</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">This bit is the logical OR of all page-1 DetectionPaused bits. If set to 1, then detection is paused for one or more INTIDs.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">error_DetectionPaused</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">After the BIST check completes successfully, the page-1 DetectionPaused bits are set to 1, which causes page-2 DetectionPaused = 1. If page-2 DetectionPaused fails to clear to 0, then this bit is set to 1.

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             All interrupt protection initialization was able to reach a state of error detection.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Not all interrupt protection initialization was able to reach a state of error detection. This value might occur due to either:

            <ul>
<li>A permanent fault on an interrupt wire, or its check wire.</li>
<li>Continuous state toggling on an interrupt wire, or its check wire, preventing the 16-cycle clock period level consistency to occur.</li>
</ul>
<p>See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a> for more information.</p>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">error_INTID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">This value is the wire index for the protected interrupts on either a:

          <dl>
<dt class="documents-dlterm">
<span>GIC Cluster Interface (GCI)</span>
</dt>
<dd>
             For PPIs, this field returns an ID that indexes sequentially across all PPIs, for each PE that a

            <span>GCI</span> supports. Therefore, to calculate the PPI INTID:

            <pre><code>index = error_INTID % <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1</a>.PPIs_Per_Processor

if index &lt; 16 then
    INTID = index + 16
else
    INTID = index + 1040
end</code></pre>
<p>To determine the PE that corresponds to this error, use:</p>
<pre><code>CPUID = INT(error_INTID / <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-CFGID1--Configuration-ID1-Register?lang=en" title="This register returns information about the configuration of the Redistributors.">GICR_CFGID1</a>.PPIs_Per_Processor)</code></pre>
</dd>
<dt class="documents-dlterm">
             SPI Collator

           </dt>
<dd>
             For SPIs, this field returns the interrupt ID on an SPI Collator that has an error. The sum of error_INTID and INTID_base_offset provides the INTID value.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">BISTBusy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When the GIC exits reset, this bit is set to 1 for a fixed duration, while the GIC performs BIST for the interrupt protection. This bit has identical functionality to the BISTBusy bit in read page 1, for interrupt protection. See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a> for more information.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">error_BIST_valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether an interrupt protection BIST error has occurred:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No error occurred during interrupt protection BIST.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             An error has occurred during interrupt protection BIST. See

            <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en" title="When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.">Interrupt protection initialization</a> for more information.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13:11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[10:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">INTID_base_offset</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the base offset of the interrupt signal. For PPIs, this field returns zero. For SPIs, this field returns the base offset ID of the SPI Collator.</td>
</tr>
</tbody>
</table>



Error overflow can be set only when valid is set. Overflow means that a different INTID to the reported INTID also had an error.

If the FMU is reporting an interrupt protection error but error\_INTID\_valid reads back as 0, this means that the observed interrupt protection error is not associated with a specific INTID.

### Page 3 reads for CPUIF protection

In the following table, `NUM_EXT_ERR_IF` is a build-time option of the CPUIF protection block. See [External error inputs](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/External-error-inputs?lang=en "Each GIC block has generic fault inputs that allow the SoC integrator to connect and flag external faults to the FMU.") for more information.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 8. </span>FMU_SMRDATA bit descriptions for page 3 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==3)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1543" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1546" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e1549" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[<code class="documents-parmname">NUM_EXT_ERR_IF</code> + 23:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ext_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that an external error has occurred on a CPUIF protection block.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">lockstep_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a lock-step error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[22]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">cpu_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a CPU parity error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[21]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ci_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a <span>GCI</span> parity error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">axit_crc_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that an <span>AXI5-Stream</span> CRC error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">dft_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a DFT error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">qch_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a Q-Channel error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clk_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a clock error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">reset_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a reset error has occurred.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[<code class="documents-parmname">NUM_EXT_ERR_IF</code> + 7:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ext_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that an external interface error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">lockstep_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a lock-step error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">cpu_parity_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a CPU parity error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ci_parity_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a <span>GCI</span> parity error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">axit_crc_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that an <span>AXI5-Stream</span> CRC error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">dft_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a DFT error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">qch_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a Q-Channel error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clk_err_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that a clock error can generate a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">reset_err_enabled</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">When set to 1, it indicates that a reset error can generate a CPUIF protection fault.</td>
</tr>
</tbody>
</table>



### Page 4 reads for CPUIF protection

The following table shows the page 4 reads for a CPUIF protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 9. </span>FMU_SMRDATA bit descriptions for page 4 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.">FMU_SMRD</a></span>.PAGEID==4)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1827" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d105325e1830" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d105325e1833" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_error_seen</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates the occurrence of a deadlock error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_detection_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that deadlock detection is active.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_correction_enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, it indicates that deadlock correction is active.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">iritready_timeout</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the value of the <span class="documents-g.signal.name"><span class="documents-keyword">iritready</span></span> signal timeout. The timeout value is 8192 × (iritready_timeout + 1) − 1 cycles.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[4:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">interbeat_timeout</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the value of the interbeat timeout. The timeout value is 256 × (interbeat_timeout + 1) − 1 cycles.</td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_SMRDATA is accessible only by Secure accesses.
