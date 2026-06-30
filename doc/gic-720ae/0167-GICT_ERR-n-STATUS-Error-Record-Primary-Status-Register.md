# GICT_ERR<n>STATUS, Error Record Primary Status Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register>

### GICT\_ERR<n>STATUS, Error Record Primary Status Register

This register indicates information relating to the recorded errors.

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

Figure 1. GICT\_ERR<n>STATUS bit assignments

![GICT_ERR<n>STATUS bit assignments](images/0167-GICT_ERR-n-STATUS-Error-Record-Primary-Status-Register-img01.svg)



<table id="col1468595581902__table.gict_err_n_status">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERR&lt;n&gt;STATUS bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d27697e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d27697e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d27697e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">AV</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the address is valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR&lt;n&gt;ADDR</a> is not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register?lang=en" title="This register contains the address and security status of the write. This register is present only for GICT software record 0.">GICT_ERR&lt;n&gt;ADDR</a> contains an address that is associated with the highest priority error that this record stores. Present only in record 0.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">V</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if this register is valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             GICT_ERR&lt;n&gt;STATUS is not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             GICT_ERR&lt;n&gt;STATUS is valid. One or more errors are recorded.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[29]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable error bit.<p>SBZ in Correctable Error (CE) records.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ER</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates that at least one error has been reported over <span>ACE5-Lite</span>.<p>Set for record 0 only, and for accesses only to corrupted data, and bad incoming access.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">OF</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether multiple errors have been detected. This field is set to 1 when either:

          <ul>
<li>The <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.">GICT_ERR&lt;n&gt;MISC0</a>.Count field has overflowed, for records that track correctable ECC errors.</li>
<li>GICT_ERR&lt;n&gt;STATUS.V was previously 1, and a type of error other than a correctable error is recorded.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[26]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MV</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the GICT miscellaneous registers are valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.">GICT_ERR&lt;n&gt;MISC0</a> and

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" title="This register contains the data value of an uncorrectable error in the LPI RAM, TGT_LPI RAM, or ITS software information. The register is not present for other error records.">GICT_ERR&lt;n&gt;MISC1</a> are not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.">GICT_ERR&lt;n&gt;MISC0</a> and

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1?lang=en" title="This register contains the data value of an uncorrectable error in the LPI RAM, TGT_LPI RAM, or ITS software information. The register is not present for other error records.">GICT_ERR&lt;n&gt;MISC1</a> are valid.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[25:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Correctable error. Indicates errors that are correctable as shown in <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records?lang=en#xid1482248265860__table.error_handling_records" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability/Error-handling-records?lang=en#xid1482248265860__table.error_handling_records">Error handling records</a>:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             No CE recorded.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             At least one CE recorded.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:22]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[21:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UET</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Uncorrectable error type. RES0 unless UE == 1, in which case:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             UEO, uncorrectable error and restartable.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             UER, uncorrectable error and recoverable.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">IERR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Implementation-defined error code.<p>Returns information that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view">GICT_ERR&lt;n&gt;MISC0.Data field encoding</a> shows.</p> <p>This field is RO apart from record 0 and record <span>27</span> (and above).</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SERR</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Architecturally defined primary error code.<p>Returns information that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en#col1468833047122__tbl.gict_err_n_misc0_data_field_descriptions_with_view">GICT_ERR&lt;n&gt;MISC0.Data field encoding</a> shows. See the <a href="https://developer.arm.com/documentation/ihi0100/latest" target="_blank"><span><cite><span class="documents-keyword">Arm®</span> Reliability, Availability, and Serviceability (RAS) System Architecture for A-profile architecture</cite></span></a> for more information about this field.</p> <p>This field is RO apart from record 0.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERR<n>STATUS is accessible only by Secure accesses.
