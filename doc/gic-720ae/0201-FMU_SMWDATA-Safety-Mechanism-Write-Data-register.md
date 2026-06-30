# FMU_SMWDATA, Safety Mechanism Write Data register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register>

### FMU\_SMWDATA, Safety Mechanism Write Data register

This register contains the data that is written during a page write access.

Writes to this register does not set [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").BUSY = 1 or the sending of AXI5-Stream messages.

The format of the register depends on which page is being written, by using [FMU\_SMWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en "This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.").PAGEID. The number of pages available depends on the protection mechanism:

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

If a GIC configuration does not include a particular protection type, then software can still perform page accesses to the corresponding PROTIDs. In this case, when using [FMU\_SMWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en "This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.") and FMU\_SMWDATA to perform a write:

- Writes to page 0 are visible for subsequent reads using [FMU\_SMRD](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en "This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.") and [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").
- Writes to page 1 and higher are ignored, and reading them back using [FMU\_SMRD](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en "This register performs a page read access. When the FMU receives a write access to this register, it sends an FMU_PAGE_ACCESS message to the fault collator that the BLKTYPE and BLKID fields select.") and [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.") returns zeros.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

Software must program this register before each write to [FMU\_SMWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en "This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.").

### Bit descriptions

The bit descriptions depend on the page that is written. Some protection mechanisms provide multiple pages for the control and status information.

The following table shows the page 0 writes for all protection mechanisms.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_SMWDATA bit descriptions for page 0 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==0)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e300" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e303" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e306" rowspan="1">Description</th>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Insert, or clear, an error for testing purposes:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Error is not inserted.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Insert, or clear, an error.

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
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the criticality of a <span>protection mechanism</span>:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span>protection mechanism</span>, with the ID that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a>.SMID wrote, is set as a non-critical error. As the GIC exits reset, it applies this setting to the RAM SEC

            <span>protection mechanism</span>s, that is, the SM_SEC*

            <span>protection mechanism</span>s.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span>protection mechanism</span>, with the ID that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a>.SMID wrote, is set as a critical error. As the GIC exits reset, it applies this setting to all

            <span>protection mechanism</span>s except for the RAM SEC

            <span>protection mechanism</span>s.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">enable</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Enables or disables a <span>protection mechanism</span>:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Disables a

            <span>protection mechanism</span> with the ID that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a>.SMID wrote.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Enables a

            <span>protection mechanism</span> with the ID that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a>.SMID wrote.

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



### Page 1 writes for AXI5-Stream protection and CPUIF protection

For AXI5-Stream interface and CPUIF protection, this write sets the timeout behavior for CRC protection. CRC protection schedules a ping packet to be sent after any mission or FMU packet, except the PowerdownAck packet. After a ping packet is received, the recipient must respond with a ping acknowledge packet.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>FMU_SMWDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e545" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e548" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e551" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SendTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the duration when it becomes a high priority for the block to send a ping or a ping acknowledge packet:

          <ul>
<li>4 × (SendTime + 1) − 1 cycles.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the duration when the block detects a timeout error because a ping or a ping acknowledge packet is missing:

          <ul>
<li>64 × (ErrTime + 1) − 1 cycles.</li>
</ul> <p>We recommend that the time to error is at least 4 times longer than the time to send a ping or a ping acknowledge packet. However, interconnect delays or the different frequencies of both domains might require this recommendation to be longer.</p> </td>
</tr>
</tbody>
</table>



### Page 1 writes for AXI5-Stream cross-chip protection

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 0, sets the timeout behavior for the CRC protection that an AXI5-Stream cross-chip interface uses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 3. </span>FMU_SMWDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e644" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e647" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e650" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ReadyErrTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the duration when the block detects a timeout error, because the transmitter does not receive a <span class="documents-g.signal.name"><span class="documents-keyword">TREADY</span></span> response:

          <ul>
<li>12 × ReadyErrTime + 1 to 16 × ReadyErrTime cycles.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CRCErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the duration when the block detects a timeout error, because a CRC request packet or a CRC acknowledge packet is missing:

          <ul>
<li>56 × CRCErrTime + 1 to 64 × CRCErrTime cycles.</li>
</ul> </td>
</tr>
</tbody>
</table>



### Page 1 writes for ACE5-Lite cross-chip protection

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 1, sets the timeout behavior for the CRC protection that an ACE5-Lite cross-chip interface uses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 4. </span>FMU_SMWDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e744" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e747" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e750" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ReadyErrTime</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the duration when the block detects a timeout error, because the manager does not receive an <span class="documents-g.signal.name"><span class="documents-keyword">AWREADY</span></span> response:

          <ul>
<li>12 × ReadyErrTime + 1 to 16 × ReadyErrTime cycles.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CRCErrTime</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the duration when the block detects a timeout error, because a CRC request packet or a CRC acknowledge packet is missing:

          <ul>
<li>56 × CRCErrTime + 1 to 64 × CRCErrTime cycles.</li>
</ul> </td>
</tr>
</tbody>
</table>



### Page 1 writes for interrupt protection

If a GIC configuration does not enable interrupt protection for the block being accessed, the GIC ignores writes to interrupt protection page 1 and [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").PROTID\_ERR returns 0b0. The `spi_protection_type`, `rlt_spi_protection_type`, and `ppi_protection_type` parameters control whether a configuration supports interrupt protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 5. </span>FMU_SMWDATA bit descriptions for page 1 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==1)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e852" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e855" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e858" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enable</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Enable interrupt protection:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Disable interrupt protection for the interrupt that INTID selects.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Enable interrupt protection for the interrupt that INTID selects.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EnableTransient</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Enable transient protection:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Disable transient protection for the interrupt that INTID selects.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Enable transient protection for the interrupt that INTID selects.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>[13:12]</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span>[11:0]</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">INTID_index</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Selects the interrupt ID of the PPI or SPI to write to. This value is the wire index for that block of protected interrupts.</td>
</tr>
</tbody>
</table>



### Page 2 writes for AXI5-Stream protection and CPUIF protection

The following table shows the page 2 writes that clear the CRC timeout and CRC checksum errors for AXI5-Stream protection and CPUIF protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 6. </span>FMU_SMWDATA bit descriptions for page 2 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==2)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1011" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1014" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e1017" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_crc_timeout_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a CRC timeout error.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">clr_crc_chksum_err</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Set to 1, to clear a CRC checksum error.</td>
</tr>
</tbody>
</table>



### Page 2 writes for interrupt protection

If a GIC configuration does not enable interrupt protection for the block being accessed, the GIC ignores writes to interrupt protection page 2 and [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").PROTID\_ERR returns 0b0. The `spi_protection_type`, `rlt_spi_protection_type`, and `ppi_protection_type` parameters control whether a configuration supports interrupt protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 7. </span>FMU_SMWDATA bit descriptions for page 2 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==2)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1118" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1121" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e1124" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clear_err_INTID_valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Clears the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_INTID_valid bit:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No change in the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_INTID_valid bit.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Clear the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_INTID_valid bit. The clear is successful only if the value of clear_error_overflow is the same as

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_overflow, in interrupt protection page 2, when the clear is received.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clear_error_overflow</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Clears the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_overflow bit:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No change in the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_overflow bit.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Clear the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_overflow bit, for the reported INTID that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a> reports for page 2 interrupt protection. The clear of

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_overflow is successful only when software sets clear_err_INTID_valid=1 and clear_error_overflow=1 in the same write access.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clear_error_DetectionPaused</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Clears the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_DetectionPaused bit:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No change in the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_DetectionPaused bit.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Clear the

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en" title="This register contains the data that is read during a page read access.">FMU_SMRDATA</a>.error_DetectionPaused bit, for page 2 interrupt protection.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[27:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
</tbody>
</table>



### Page 3 writes for CPUIF protection

In the following table, `NUM_EXT_ERR_IF` is a build-time option of the CPUIF protection block. See [External error inputs](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/External-error-inputs?lang=en "Each GIC block has generic fault inputs that allow the SoC integrator to connect and flag external faults to the FMU.") for more information.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 8. </span>FMU_SMWDATA bit descriptions for page 3 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==3)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1380" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1383" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e1386" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[<code class="documents-parmname">NUM_EXT_ERR_IF</code> + 23:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ext_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear an error on an external interface on a CPUIF protection block.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_lockstep_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a lock-step error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[22]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_cpu_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a CPU parity error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[21]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_ci_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a <span>GCI</span> parity error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_axit_crc_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear an <span>AXI5-Stream</span> CRC error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_dft_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a DFT error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_qch_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a Q-Channel error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_clk_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a clock error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">clr_reset_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to clear a reset error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[<code class="documents-parmname">NUM_EXT_ERR_IF</code> + 7:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_ext_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want an external interface error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_lockstep_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a lock-step error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_cpu_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a CPU parity error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_ci_parity_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a <span>GCI</span> parity error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_axit_crc_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want an <span>AXI5-Stream</span> CRC error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_dft_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a DFT error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_qch_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a Q-Channel error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">en_clk_err</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, if you want a clock error to contribute to a CPUIF protection fault.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">en_reset_err</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Set to 1, if you want a reset error to contribute to a CPUIF protection fault.</td>
</tr>
</tbody>
</table>



### Page 4 writes for CPUIF protection

The following table shows the page 4 writes for a CPUIF protection.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 9. </span>FMU_SMWDATA bit descriptions for page 4 (<span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU_PAGE_ACCESS message to the fault collators that reside in the other GIC components.">FMU_SMWR</a></span>.PAGEID==4)</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1665" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1668" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36333e1671" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d36333e1674" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_error_seen</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">When set to 1, it indicates the occurrence of a deadlock error. Write one to clear this bit.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">R/W1C</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_detection_enable</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to 1, to enable deadlock detection.<p>We recommend that deadlock detection timeout is not disabled because it could cause transactions to back up during error conditions, which impacts other processors and complicates the recovery.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">deadlock_correction_enable</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to 1, to enable deadlock correction.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">iritready_timeout</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Sets the value of the <span class="documents-g.signal.name"><span class="documents-keyword">iritready</span></span> signal timeout to 8192 × (iritready_timeout + 1) − 1 cycles. Times out if the processor does not respond. However, this timeout is not on the interface, so there must be two transactions stuck ahead before it times out. These are protected by lock-stepping.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[4:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">interbeat_timeout</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Sets the value of the interbeat timeout to 256 × (interbeat_timeout + 1) − 1 cycles. Used for timing between beats of multi-beat transactions.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_SMWDATA is accessible only by Secure accesses.
