# GICR_VERRR, vICM vPE Error Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register>

### GICR\_VERRR, vICM vPE Error Register

This register can set and clear the error bit for a vPE in the vICM RAM. You can use the register to find vPEs with an error in the vICM and obtain vPE information from the vTGT cache and the vICM.

### Configurations

This register is available in all configurations that support vLPIs.

### Attributes

Width
:   64-bit

Functional group
:   See
    [vLPI register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary?lang=en "The functions for the GIC-720AE vLPIs are controlled through the Redistributor registers identified with the prefix GICR.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

The bit assignments within this register can change, depending on whether you are initiating a request or reading the information of a read (RD) request.

The following table shows the bit assignments when initiating a request.



<table id="hxe1491907107521__tbl.gicr_verrr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_VERRR bit assignments, for request initiation</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e128" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e131" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e134" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d91956e137" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Busy</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to 1, to start a request. The GIC sets this bit to 0 when it completes the request.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">This bit indicates if the request was successful, and is valid only when Busy == 0:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The GIC performed the request.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The GIC failed to perform the request.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Opcode</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Request type:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             RD. Read vPE information.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             SET. Set the error bit.

           </dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             CLR. Clear the error bit.

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
             FIND. Find a vPE that contains an error.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59:17]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[16:14]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read_block</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Controls which data to retrieve for an RD operation (Opcode == 0):

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Doorbell data. See

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_Doorbell_read_request" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_Doorbell_read_request">GICR_VERRR bit assignments, for a Doorbell read request</a>.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             vPT data. See

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vPT_read_request" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vPT_read_request">GICR_VERRR bit assignments, for a vPT read request</a>.

           </dd>
<dt class="documents-dlterm">
             2, 5-7

           </dt>
<dd>
             vCONF data. See

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vCONF_read_request" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vCONF_read_request">GICR_VERRR bit assignments, for a vCONF read request</a>.

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
             vSGI[15:8] programming. See

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vSGI_read_request" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vSGI_read_request">GICR_VERRR bit assignments, for a vSGI read request</a>.

           </dd>
<dt class="documents-dlterm">
             4

           </dt>
<dd>
             vSGI[7:0] programming. See

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vSGI_read_request" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en#hxe1491907107521__table.response_to_a_vSGI_read_request">GICR_VERRR bit assignments, for a vSGI read request</a>.

           </dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[13:n]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[n−1:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">vPEID</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">For RD, SET, and CLR requests (Opcode ≤ 2), this field selects the vPE that receives the request.<p>For FIND requests (Opcode == 3), this field selects the vPE where the error search starts. If no errors are found for that vPE, the search incrementally checks the other vPEs. The search wraps around to ensure all vPEs are searched. The search ends when an error is found or when the search has checked all the vPEs.</p> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>



When you read the GICR\_VERRR register, the following tables show the bit assignments for the different request types:

Response to a Doorbell read request
:   The following table shows the bit assignments when the GIC performs a read (RD) request of the Doorbell information.




<table id="hxe1491907107521__table.response_to_a_Doorbell_read_request">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>GICR_VERRR bit assignments, for a Doorbell read request</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e409" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e412" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d91956e415" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the read request is complete:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 Doorbell read request is complete.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 Doorbell read request is in progress.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request was successful, and is valid only when Busy == 0:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The GIC performed the request.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The GIC failed to perform the request.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Opcode</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 0 because an RD request was requested.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Errored</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request has errored in the vTGT cache:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The request did not cause an error.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The request has errored in the vTGT cache. The Doorbell ID might be incorrect.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[57:42]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DB_ID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the default Doorbell identifier.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[41]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DB_Mask</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the default Doorbell mask.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[40:38]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[37]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DB_Prop</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the default Doorbell properties are valid:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The default Doorbell properties are not valid.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The default Doorbell properties are valid.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[36]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DB_Enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the default Doorbell is enabled:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The default Doorbell is not enabled.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The default Doorbell is enabled.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[35:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DB_Priority</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the priority of the default Doorbell. <span class="documents-g.number.bin">0b0000</span> is the lowest priority and <span class="documents-g.number.bin">0b1111</span> is the highest priority.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[8:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">DB_PE</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the PE that the default Doorbell targets.</td>
</tr>
</tbody>
</table>



Response to a vPT read request
:   The following table shows the bit assignments when the GIC performs a read (RD) request of the vPT information.




<table id="hxe1491907107521__table.response_to_a_vPT_read_request">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 3. </span>GICR_VERRR bit assignments, for a vPT read request</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e714" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e717" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d91956e720" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the read request is complete:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 vPT read request is complete.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 vPT read request is in progress.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request was successful, and is valid only when Busy == 0:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The GIC performed the request.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The GIC failed to perform the request.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Opcode</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 0 because an RD request was requested.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Mapped</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the vPE is mapped on the local chip:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vPE is not mapped on the local chip.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vPE is mapped on the local chip.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Errored</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the vPE is errored:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vPE is not errored.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vPE is errored.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[57:42]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Mapped_ITS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the ITSs that the vPE is mapped on:

              <ul>
<li>Bit[57] is ITS15</li>
<li>Bit[56] is ITS14</li>
<li>…</li>
<li>Bit[42] is ITS0</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[41:36]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[35:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">vPT_Addr</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the vPT base address, bits[51:15], for the vPE.</td>
</tr>
</tbody>
</table>



Response to a vCONF read request
:   The following table shows the bit assignments when the GIC performs a read (RD) request of the vCONF information.




<table id="hxe1491907107521__table.response_to_a_vCONF_read_request">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 4. </span>GICR_VERRR bit assignments, for a vCONF read request</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e944" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e947" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d91956e950" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the read request is complete:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 vCONF read request is complete.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 vCONF read request is in progress.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request was successful, and is valid only when Busy == 0:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The GIC performed the request.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The GIC failed to perform the request.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Opcode</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 0 because an RD request was requested</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Mapped</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the vPE is mapped<span> on the local chip</span>:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vPE is not mapped

                <span> on the local chip</span>.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vPE is mapped

                <span> on the local chip</span>.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Errored</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the vPE is errored:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vPE is not errored.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vPE is errored.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[57:42]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Mapped_ITS</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>When <span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.EITS == 1</span>, returns the ITSs that the vPE is mapped on:</span>
<ul>
<li>Bit[57] is ITS31</li>
<li>Bit[56] is ITS30</li>
<li>…</li>
<li>Bit[42] is ITS16</li>
</ul> <p>When <span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.EITS == 0</span>, this field is <span class="documents-archterm">RES0</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[41:36]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[35:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">vCONF_Addr</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the vCONF base address, bits[51:15], for the vPE.</td>
</tr>
</tbody>
</table>



Response to a vSGI read request
:   The following table shows the bit assignments when the GIC performs a read (RD) request of the vSGI programming information.




<table id="hxe1491907107521__table.response_to_a_vSGI_read_request">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 5. </span>GICR_VERRR bit assignments, for a vSGI read request</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e1214" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d91956e1217" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d91956e1220" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Busy</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the read request is complete:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 vSGI read request is complete.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 vSGI read request is in progress.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request was successful, and is valid only when Busy == 0:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The GIC performed the request.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The GIC failed to perform the request.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Opcode</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 0 because an RD request was requested</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[58]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Errored</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the request has errored in the vTGT cache:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The request did not cause an error.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The request has errored in the vTGT cache. The vSGI programming might be incorrect.

               </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[57:48]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[47:40]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI_Group</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Each bit represents a vSGI and it indicates which group the vSGI belongs to:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vSGI belongs to Group 0.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vSGI belongs to Group 1.

               </dd>
</dl> <p>Bit[40] represents vSGI[0] and bit[47] represents vSGI[7].</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[39:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI_Enabled</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Each bit represents a vSGI and indicates if the vSGI is enabled:

              <dl>
<dt class="documents-dlterm">
                 0

               </dt>
<dd>
                 The vSGI is not enabled.

               </dd>
<dt class="documents-dlterm">
                 1

               </dt>
<dd>
                 The vSGI is enabled.

               </dd>
</dl> <p>Bit[32] represents vSGI[0] and bit[39] represents vSGI[7].</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[32:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">vSGI_Priority</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Each nibble represents a vSGI and it returns the priority of the vSGI. <span class="documents-g.number.bin">0b0000</span> is the lowest priority and <span class="documents-g.number.bin">0b1111</span> is the highest priority. Bits[3:0] represent vSGI[0] and bits[31:28] represent vSGI[7].</td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_VERRR is accessible only with a 64-bit access.
