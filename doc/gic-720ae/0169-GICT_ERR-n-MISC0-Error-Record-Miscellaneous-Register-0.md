# GICT_ERR<n>MISC0, Error Record Miscellaneous Register 0

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0>

### GICT\_ERR<n>MISC0, Error Record Miscellaneous Register 0

This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

None

### Bit descriptions

Figure 1. GICT\_ERR<n>MISC0 bit assignments

![GICT_ERR<n>MISC0 bit assignments](images/0169-GICT_ERR-n-MISC0-Error-Record-Miscellaneous-Register-0-img01.svg)



<table id="col1468833047122__table.gict_err_n_misc0">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERR&lt;n&gt;MISC0 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d30441e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d30441e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d30441e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:42]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[41]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Rounding error.<p>The rounding error counter is under-reporting.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[40]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Overflow</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sticky overflow bit:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Counter has not overflowed.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Counter has overflowed.

           </dd>
</dl> <p>If the corrected fault handling interrupt is enabled, then the <span class="documents-keyword">GIC-720AE</span> generates a fault handling interrupt.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[39:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Count</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Error count.<p>Is present for all error records containing RAM errors. Incremented for each corrected error or uncorrectable error that does not match the recorded syndrome.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Data</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Information that is associated with the error. A description of each error code is given in one of the following tables:

          <ul>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Software-error-record-0?lang=en#nbm1482319804137__table.record_0_software_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Software-error-record-0?lang=en#nbm1482319804137__table.record_0_software_errors">Software errors, record 0</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en#mra1489160759372__table.record_1_and_2_spi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en#mra1489160759372__table.record_1_and_2_spi_ram_errors">SPI RAM errors, records 1-2</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SGI-RAM-error-records-3-4?lang=en#czg1489160994574__table.records_3_and_4_sgi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SGI-RAM-error-records-3-4?lang=en#czg1489160994574__table.records_3_and_4_sgi_ram_errors">SGI RAM errors, records 3-4</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-SPI-RAM-error-records-5-6?lang=en#brh1534679637587__table.records_5-6_tgt_spi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-SPI-RAM-error-records-5-6?lang=en#brh1534679637587__table.records_5-6_tgt_spi_ram_errors">TGT_SPI RAM errors, records 5-6</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PPI-RAM-error-records-7-8?lang=en#ppx1482507307078__table.records_7_and_8_ppi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PPI-RAM-error-records-7-8?lang=en#ppx1482507307078__table.records_7_and_8_ppi_ram_errors">PPI RAM errors, records 7-8</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/LPI-RAM-error-records-9-10?lang=en#dtd1482508432357__table.records_9_and_10_lpi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/LPI-RAM-error-records-9-10?lang=en#dtd1482508432357__table.records_9_and_10_lpi_ram_errors">LPI RAM errors, records 9-10</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PTS-RAM-error-records-11-12?lang=en#fjn1496833174190__table.records_11-12_pts_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PTS-RAM-error-records-11-12?lang=en#fjn1496833174190__table.records_11-12_pts_ram_errors">PTS RAM errors, records 11-12</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-LPI-RAM-error-records-13-14?lang=en#mdz1497256651764__table.records_13-14_tgt_lpi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-LPI-RAM-error-records-13-14?lang=en#mdz1497256651764__table.records_13-14_tgt_lpi_ram_errors">TGT_LPI RAM errors, records 13-14</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VICM-RAM-error-records-15-16?lang=en#bjt1497276588218__table.records_15-16_vicm_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VICM-RAM-error-records-15-16?lang=en#bjt1497276588218__table.records_15-16_vicm_ram_errors">VICM RAM errors, records 15-16</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VSPA-RAM-error-records-17-18?lang=en#jpz1497276791418__table.records_17-18_vspa_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VSPA-RAM-error-records-17-18?lang=en#jpz1497276791418__table.records_17-18_vspa_ram_errors">VSPA RAM errors, records 17-18</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VSTR-RAM-error-records-19-20?lang=en#pwn1497348955332__table.records_19-20_vtgt_vstr_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VSTR-RAM-error-records-19-20?lang=en#pwn1497348955332__table.records_19-20_vtgt_vstr_ram_errors">VTGT_VSTR RAM errors, records 19-20</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VRES-RAM-error-records-21-22?lang=en#iod1497352096402__table.records_21-22_vtgt_vres_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VRES-RAM-error-records-21-22?lang=en#iod1497352096402__table.records_21-22_vtgt_vres_ram_errors">VTGT_VRES RAM errors, records 21-22</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-SRCH-RAM-error-records-23-24?lang=en#pnr1497426941852__table.records_23-24_vtgt_srch_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-SRCH-RAM-error-records-23-24?lang=en#pnr1497426941852__table.records_23-24_vtgt_srch_ram_errors">VTGT_SRCH RAM errors, records 23-24</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-RAM-error-records-25-26?lang=en#yee1483441026913__table.records_11_and_12_its_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-RAM-error-records-25-26?lang=en#yee1483441026913__table.records_11_and_12_its_ram_errors">ITS RAM errors, records 25-26</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-command-and-translation-error-records-27-?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-command-and-translation-error-records-27-?lang=en" title="The ITS command and translation error records 27+ record uncorrectable command and translation errors from each configured ITS.">ITS command and translation error records 27+</a></li>
<li><a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/CC-RAM-error-records-62-63?lang=en#dav1448825529578__table.records_62-63_cc_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/CC-RAM-error-records-62-63?lang=en#dav1448825529578__table.records_62-63_cc_ram_errors">CC RAM errors, records 62-63</a></li>
</ul> </td>
</tr>
</tbody>
</table>



The following table shows the Data field encoding for each error record and syndrome.



<table id="col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>GICT_ERR&lt;n&gt;MISC0.Data field encoding</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d30441e349" rowspan="1">Record</th>
<th class="documents-nocellnorowborder" colspan="1" id="d30441e352" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS</a>.IERR (syndrome)</th>
<th class="documents-nocellnorowborder" colspan="1" id="d30441e361" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en" title="This register indicates information relating to the recorded errors.">GICT_ERR&lt;n&gt;STATUS</a> <span>.SERR</span></th>
<th class="documents-cell-norowborder" colspan="1" id="d30441e372" rowspan="1">Value and description of GICT_ERR&lt;n&gt;MISC0.Data (other bits RES0)<p>Always packed from 0 (lowest = 0)</p> </th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span>, SYN_ACE_BAD<p>Illegal <span>ACE5-Lite</span> subordinate access.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AccessRnW, bit[12]<p>AccessSparse, bit[11]</p> <p>AccessSize, bits[10:8]</p> <p>AccessLength, bits[7:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1</span>, SYN_PPI_PWRDWN<p>Attempt to access a powered down Redistributor.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Redistributor, bits[24:16]<p>Core, bits[8:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2</span>, SYN_PPI_PWRCHANGE<p>Attempt to power down Redistributor rejected.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Redistributor, bits[24:16]<p>Core, bits[8:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x4</span>, SYN_PROPBASE_ACC<p>Attempt to reprogram PROPBASE registers to a value that is not accepted because another value is already in use.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x5</span>, SYN_PENDBASE_ACC<p>Attempt to reprogram PENDBASE registers to a value that is not accepted because another value is already in use.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x7</span>, SYN_WAKER_CHANGE<p>Attempt to change <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER</a> abandoned due to handshake rules.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8</span>, SYN_SLEEP_FAIL<p>Attempt to put GIC to sleep failed because cores are not fully asleep.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x9</span>, SYN_PGE_ON_QUIESCE<p>Core put to sleep before its Group enables were cleared.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x10</span>, SYN_SGI_NO_TGT<p>SGI sent with no valid destinations.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x11</span>, SYN_SGI_CORRUPTED<p>SGI corrupted without effect.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Core, bits[8:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span>, SYN_GICR_CORRUPTED<p>Data was read from GICR register space that encountered an uncorrectable error.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR0ADDR</a> is populated</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x13</span>, SYN_GICD_CORRUPTED<p>Data was read from GICD register space that encountered an uncorrectable error.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR0ADDR</a> is populated</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x14</span>, SYN_ITS_OFF<p>Data was read from an ITS that is powered down.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR0ADDR</a> is populated</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x18</span>, SYN_SPI_BLOCK.<p>Attempt to access an SPI block that is not implemented.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Block, bits[4:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x19</span>, SYN_SPI_OOR<p>Attempt to access a non-implemented SPI using (SET|CLR)SPI.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID, bits[9:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1A</span>, SYN_SPI_NO_DEST_TGT<p>An SPI has no legal target destinations.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID, bits[9:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1B</span>, SYN_SPI_NO_DEST_1OFN<p>A 1 of N SPI cannot be delivered due to bad <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en" title="This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.">GICR_CTLR</a>.DPG&lt;0|1NS|1S&gt; or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register?lang=en" title="This register specifies which class of 1 of N interrupt the CPU accepts.">GICR_CLASSR</a> programming.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID, bits[9:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1C</span>, SYN_COL_OOR<p>A collator message is received for a non-implemented SPI, or is larger than the number of owned SPIs in a multichip configuration.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID, bits[9:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1D</span>, SYN_DEACT_IN<p>A <code>Deactivate</code> command to a nonexistent SPI, or with incorrect groups set. <code>Deactivate</code> commands to <span>LPI and </span>nonexistent PPI are not reported.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1E</span>, SYN_SPI_CHIP_OFFLINE<p>An attempt was made to send an SPI to an offline chip.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID, bits[9:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x25</span>, SYN_VSGI_OFFLINE<p>Pending vSGI to a vPEID mapped to an offline chip.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip [log<sub>2</sub>(chips)−1:0]<p>ID (multi-hot) [15:0]</p> <p>vPEID[log<sub>2</sub>(vpes)−1:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x30</span>, SYN_VSGI_UNMAPPED<p>Pending vSGI to a vPEID that is not mapped.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID (multi-hot) [15:0]<p>vPEID[log<sub>2</sub>(vpes)−1:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x33</span>, SYN_VSGI_LOST<p>Pending vSGI to a vPEID that has inconsistent mapping information across multiple chips.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID (multi-hot) [15:0]<p>vPEID [log<sub>2</sub>(vpes)−1:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x34</span>, SYN_VPT_READ_FAIL<p>An attempt was made to read the vPE configuration from the virtual Pending table, with an error received with the read response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x35</span>, SYN_VPT_WRITE_FAIL<p>An attempt was made to write the vPE configuration to the virtual Pending table, with an error received with the write response.</p> <p>The vICM reports bad write responses on the chip where the access occurs, rather than the chip that contains the ITS that generated the command or interrupt.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x39</span>, SYN_VPE_CFG_PTR_FAIL<p>An attempt was made to access an indirect vPE Configuration table with an invalid level 2 pointer.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3A</span>, SYN_VPE_CFG_TOP_READ_FAIL<p>An attempt was made to read the level 1 of an indirect vPE Configuration table, with an error received with the read response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3B</span>, SYN_VPE_CFG_LEAF_READ_FAIL<p>An attempt was made to read the level 2 of an indirect vPE Configuration table or any vPE Configuration read when the table is not indirect, with an error received with the read response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3C</span>, SYN_VPE_CFG_WRITE_FAIL<p>An attempt was made to write the level 2 of an indirect vPE Configuration table or any vPE Configuration write when the table is not indirect, with an error received with the read response.</p> <p>The vICM reports bad write responses on the chip where the access occurs, rather than the chip that contains the ITS that generated the command or interrupt.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3D</span>, SYN_VPE_CFG_OVERFLOW<p>A vPE Configuration table access was aborted due to table entry overflow in the address space.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">vPEID [log<sub>2</sub>(vpes)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x40</span>, SYN_LPI_PROP_READ_FAIL<p>An attempt was made to read properties for a single interrupt where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x41</span>, SYN_PT_PROP_READ_FAIL<p>An attempt was made to read properties for a block of interrupts where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x42</span>, SYN_PT_COARSE_MAP_READ_FAIL<p>An attempt was made to read the coarse map for a target where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x43</span>, SYN_PT_COARSE_MAP_WRITE_FAIL<p>An attempt was made to write the coarse map for a target with an error received with the write response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span>, SYN_PT_TABLE_READ_FAIL<p>An attempt was made to read a block of interrupts from a Pending table, where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x45</span>, SYN_PT_TABLE_WRITE_FAIL<p>An attempt was made to write-back a block of interrupts from a Pending table with an error received with the write response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x46</span>, SYN_PT_SUB_TABLE_READ_FAIL<p>An attempt was made to read a subblock of interrupts from a Pending table, where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x47</span>, SYN_PT_TABLE_WRITE_FAIL_BYTE<p>An attempt was made to write-back a subblock of interrupts from a Pending table, with an error received with the write response.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x48</span>, SYN_DBL_PROP_READ_FAIL<p>An attempt was made to read properties for a single doorbell, where an error response was received with the data.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Virtual, bit[30]<p>Target, bits[29:16]</p> <p>ID, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x50</span>, SYN_VPROPBASER_DATA<p>An attempt was made to program additional GICR_VPROPBASER.Valid bits with data mismatching <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VCFGBASER--vICM-Final-vPE-CFG-Attribute-Register?lang=en" title="This register returns the access attributes of the vPE Configuration table.">GICR_VCFGBASER</a>.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x52</span>, SYN_VERRR_BUSY<p>An attempt was made to access <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" title="This register can set and clear the error bit for a vPE in the vICM RAM. You can use the register to find vPEs with an error in the vICM and obtain vPE information from the vTGT cache and the vICM.">GICR_VERRR</a> while the register is busy from a previous operation.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x53</span>, SYN_VERRR_ALLOC<p>An attempt was made to access <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" title="This register can set and clear the error bit for a vPE in the vICM RAM. You can use the register to find vPEs with an error in the vICM and obtain vPE information from the vTGT cache and the vICM.">GICR_VERRR</a> while there is no vPE Configuration table allocation.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x54</span>, SYN_VERRR_VPE_OOR<p>A request was made to <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VERRR--vICM-vPE-Error-Register?lang=en" title="This register can set and clear the error bit for a vPE in the vICM RAM. You can use the register to find vPEs with an error in the vICM and obtain vPE information from the vTGT cache and the vICM.">GICR_VERRR</a> with a vPEID that is out of range.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x56</span>, SYN_VSGIR_ALLOC<p>An attempt was made to access GICR_VSGIR while there is no vPE Configuration table allocation.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x57</span>, SYN_VSGIR_VPE_OOR<p>A request was made to GICR_VSGIR with a vPEID that is out of range.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x58</span>, SYN_VINV_BUSY<p>An attempt was made to access <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" title="This register can invalidate the vICM RAM in selected chips.">GICR_VINVCHIPR</a> while the register is busy from a previous operation.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x59</span>, SYN_VINV_ALLOC<p>An attempt was made to access <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en" title="This register can invalidate the vICM RAM in selected chips.">GICR_VINVCHIPR</a> while there is no vPE Configuration table allocation.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU [log<sub>2</sub>(cpus)−1:0]</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x60</span>, SYN_ACE_CC_BAD<p>Illegal cross-chip <span>ACE5-Lite</span> subordinate access.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Access chip, [15:4]<p>Access opcode, [3:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x70</span>, SYN_ITS_REG_INV_BUSY<p>An attempt was made to invalidate an interrupt while register busy.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU, [log<sub>2</sub>(cores) − 1:0]<p>Data, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Software error (0)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x71</span>, SYN_ITS_REG_INV_OOR<p>An attempt was made to invalidate an OOR interrupt.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">CPU, [log<sub>2</sub>(cores) − 1:0]<p>Data, bits[15:0]</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable SPI RAM errors (1)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en#mra1489160759372__table.record_1_and_2_spi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SPI-RAM-error-records-1-2?lang=en#mra1489160759372__table.record_1_and_2_spi_ram_errors">SPI RAM errors, records 1-2</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable SPI RAM errors (2)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable SGI RAM errors (3)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SGI-RAM-error-records-3-4?lang=en#czg1489160994574__table.records_3_and_4_sgi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/SGI-RAM-error-records-3-4?lang=en#czg1489160994574__table.records_3_and_4_sgi_ram_errors">SGI RAM errors, records 3-4</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable SGI RAM errors (4)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable TGT_SPI cache errors (5)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-SPI-RAM-error-records-5-6?lang=en#brh1534679637587__table.records_5-6_tgt_spi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-SPI-RAM-error-records-5-6?lang=en#brh1534679637587__table.records_5-6_tgt_spi_ram_errors">TGT_SPI RAM errors, records 5-6</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable TGT_SPI cache errors (6)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable PPI RAM errors (7)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PPI-RAM-error-records-7-8?lang=en#ppx1482507307078__table.records_7_and_8_ppi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PPI-RAM-error-records-7-8?lang=en#ppx1482507307078__table.records_7_and_8_ppi_ram_errors">PPI RAM errors, records 7-8</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable PPI RAM errors (8)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable LPI RAM errors (9)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/LPI-RAM-error-records-9-10?lang=en#dtd1482508432357__table.records_9_and_10_lpi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/LPI-RAM-error-records-9-10?lang=en#dtd1482508432357__table.records_9_and_10_lpi_ram_errors">LPI RAM errors, records 9-10</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable LPI RAM errors (10)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable PTS RAM error (11)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PTS-RAM-error-records-11-12?lang=en#fjn1496833174190__table.records_11-12_pts_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/PTS-RAM-error-records-11-12?lang=en#fjn1496833174190__table.records_11-12_pts_ram_errors">PTS RAM errors, records 11-12</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable PTS RAM error (12)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable TGT_LPI RAM error (13)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-LPI-RAM-error-records-13-14?lang=en#mdz1497256651764__table.records_13-14_tgt_lpi_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/TGT-LPI-RAM-error-records-13-14?lang=en#mdz1497256651764__table.records_13-14_tgt_lpi_ram_errors">TGT_LPI RAM errors, records 13-14</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable TGT_LPI RAM error (14)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable VICM RAM error (15)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VICM-RAM-error-records-15-16?lang=en#bjt1497276588218__table.records_15-16_vicm_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VICM-RAM-error-records-15-16?lang=en#bjt1497276588218__table.records_15-16_vicm_ram_errors">VICM RAM errors, records 15-16</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable VICM RAM error (16)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable VSPA RAM error (17)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VSPA-RAM-error-records-17-18?lang=en#jpz1497276791418__table.records_17-18_vspa_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VSPA-RAM-error-records-17-18?lang=en#jpz1497276791418__table.records_17-18_vspa_ram_errors">VSPA RAM errors, records 17-18</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable VSPA RAM error (18)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable VTGT_VSTR RAM error (19)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VSTR-RAM-error-records-19-20?lang=en#pwn1497348955332__table.records_19-20_vtgt_vstr_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VSTR-RAM-error-records-19-20?lang=en#pwn1497348955332__table.records_19-20_vtgt_vstr_ram_errors">VTGT_VSTR RAM errors, records 19-20</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable VTGT_VSTR RAM error (20)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable VTGT_VRES RAM error (21)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VRES-RAM-error-records-21-22?lang=en#iod1497352096402__table.records_21-22_vtgt_vres_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-VRES-RAM-error-records-21-22?lang=en#iod1497352096402__table.records_21-22_vtgt_vres_ram_errors">VTGT_VRES RAM errors, records 21-22</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable VTGT_VRES RAM error (22)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable VTGT_SRCH RAM error (23)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-SRCH-RAM-error-records-23-24?lang=en#pnr1497426941852__table.records_23-24_vtgt_srch_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/VTGT-SRCH-RAM-error-records-23-24?lang=en#pnr1497426941852__table.records_23-24_vtgt_srch_ram_errors">VTGT_SRCH RAM errors, records 23-24</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable VTGT_SRCH RAM error (24)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable error from ITS RAM (25)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-RAM-error-records-25-26?lang=en#yee1483441026913__table.records_11_and_12_its_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-RAM-error-records-25-26?lang=en#yee1483441026913__table.records_11_and_12_its_ram_errors">ITS RAM errors, records 25-26</a></td>
</tr>
<tr>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable error from ITS RAM (26)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Command or translation error in ITS (27+)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             Architectural

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             Non-architectural

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ITS 24-bit syndrome. See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-command-and-translation-error-records-27-?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/ITS-command-and-translation-error-records-27-?lang=en" title="The ITS command and translation error records 27+ record uncorrectable command and translation errors from each configured ITS.">ITS command and translation error records 27+</a>.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Correctable error from CC RAM (62)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2">
<dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             A real error

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             An injected error

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="2"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="2">See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/CC-RAM-error-records-62-63?lang=en#dav1448825529578__table.records_62-63_cc_ram_errors" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/CC-RAM-error-records-62-63?lang=en#dav1448825529578__table.records_62-63_cc_ram_errors">CC RAM errors, records 62-63</a></td>
</tr>
<tr>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Uncorrectable error from CC RAM (63)</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERR<n>MISC0 is accessible only by Secure accesses.
