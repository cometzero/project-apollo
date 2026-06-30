# MHU FMU register summary

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary>

### MHU FMU register summary

The following summary table provides an overview of IMPLEMENTATION DEFINED memory-mapped MHU FMU Register Block registers.

For more information on registers listed in the table, click on the link associated with the register name.

Some registers do not have a listed reset value, as they are either write-only or this depends on the particular block or protection mechanism being accessed.

<table class="documents-opcodes" id="ext_mhu_fmu_register_blocksummary__regsumtable">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MHU FMU Register Block register summary
  </span>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d84431e92" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84431e94" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84431e96" rowspan="1">
    Type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84431e98" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84431e100" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d84431e102" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x000 + (64 * n)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register--n---0---5?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register--n---0---5?lang=en" title="Defines which of the common architecturally-defined features are implemented by the node and, of the implemented features, which are software programmable.">
     FMU_ERR&lt;n&gt;FR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record &lt;n&gt; Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x008 + (64 * n)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---5?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---5?lang=en" title="The error control register contains enable bits for the node that writes to this record.">
     FMU_ERR&lt;n&gt;CTLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record &lt;n&gt; Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x010 + (64 * n)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---5?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---5?lang=en" title="Contains status information for error record &lt;n&gt;.">
     FMU_ERR&lt;n&gt;STATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record &lt;n&gt; Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRGSR--Error-Group-Status-Register?lang=en" title="Shows the status for the records in the group.">
     FMU_ERRGSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Group Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRIIDR--Implementation-Identification-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRIIDR--Implementation-Identification-Register?lang=en" title="Defines the implementer of the component.">
     FMU_ERRIIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Implementation Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMEN--Safety-Mechanism-Enable-Register?lang=en" title="Enables or disables particular protection mechanisms for a specified MHU block.">
     FMU_SMEN
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF04
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMERR--Safety-Mechanism-Error-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMERR--Safety-Mechanism-Error-Register?lang=en" title="Inserts an error into the specified Safety Mechanism inside an MHU block.">
     FMU_SMERR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Error Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF08
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMCR--Safety-Mechanism-Set-Criticality-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMCR--Safety-Mechanism-Set-Criticality-Register?lang=en" title="Sets the Protection Mechanism criticality.">
     FMU_SMCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Set Criticality Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF0C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register?lang=en" title="Performs a page write and page read back access for the PAGEID. The write data used is taken from FMU_SMWDATA and the read back of the written data goes into FMU_SMRDATA.">
     FMU_SMWR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Page Write Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Page-Write-Data-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Page-Write-Data-Register?lang=en" title="Provides the Protection Mechanism page write data when FMU_SMWR is written.">
     FMU_SMWDATA
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Page Write Data Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF14
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMRD--Safety-Mechanism-Page-Read-Register?lang=en" title="Performs a page read access for the PAGEID. The read data is returned in FMU_SMRDATA.">
     FMU_SMRD
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Page Read Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF18
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Page-Read-Data-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Page-Read-Data-Register?lang=en" title="Returns the Protection Mechanism page read data when FMU_SMRD or FMU_SMWR is written.">
     FMU_SMRDATA
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Safety Mechanism Page Read Data Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF1C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en" title="Monitors whether there are outstanding FMU accesses waiting for responses.">
     FMU_STATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    FMU Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-KEY--FMU-Key-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-KEY--FMU-Key-Register?lang=en" title="Used to receiver the unlock key that is required for writes to FMU registers to be successful. This mechanism does not affect ability to perform FMU reads.">
     FMU_KEY
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    FMU Key Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF24
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-TIMEOUT--FMU-Timeout-Duration-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-TIMEOUT--FMU-Timeout-Duration-Register?lang=en" title="Defines the duration of the timeout period before TIMEOUT is reported in FMU_STATUS">
     FMU_TIMEOUT
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    FMU Timeout Duration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRUPDATE--FMU-Error-Update-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRUPDATE--FMU-Error-Update-Register?lang=en" title="Forces the record pair FMU_ERR&lt;n&gt;STATUS (indices n and n+1) to be updated with all error state reported through this record pair.">
     FMU_ERRUPDATE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    FMU Error Update Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF2C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-FCTLR--FMU-Feature-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-FCTLR--FMU-Feature-Control-Register?lang=en" title="Controls additional clock gating functionality.">
     FMU_FCTLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    FMU Feature Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRDEVARCH--Device-Architecture-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRDEVARCH--Device-Architecture-Register?lang=en" title="Provides discovery information for the component.">
     FMU_ERRDEVARCH
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Architecture Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRDEVID--Device-Configuration-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-ERRDEVID--Device-Configuration-Register?lang=en" title="Provides discovery information for the component.">
     FMU_ERRDEVID
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR4--MHU-FMU-Peripheral-ID-4-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR4--MHU-FMU-Peripheral-ID-4-Register?lang=en" title="Returns byte[4] of the peripheral ID for MHU FMU page.">
     FMU_PIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 4 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR5--MHU-FMU-Peripheral-ID-5-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR5--MHU-FMU-Peripheral-ID-5-Register?lang=en" title="Returns byte[5] of the peripheral ID for MHU FMU page.">
     FMU_PIDR5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 5 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR6--MHU-FMU-Peripheral-ID-6-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR6--MHU-FMU-Peripheral-ID-6-Register?lang=en" title="Returns byte[6] of the peripheral ID for MHU FMU page.">
     FMU_PIDR6
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 6 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR7--MHU-FMU-Peripheral-ID-7-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR7--MHU-FMU-Peripheral-ID-7-Register?lang=en" title="Returns byte[7] of the peripheral ID for MHU FMU page.">
     FMU_PIDR7
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 7 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR0--MHU-FMU-Peripheral-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR0--MHU-FMU-Peripheral-ID-0-Register?lang=en" title="Returns byte[0] of the peripheral ID for MHU FMU page.">
     FMU_PIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR1--MHU-FMU-Peripheral-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR1--MHU-FMU-Peripheral-ID-1-Register?lang=en" title="Returns byte[1] of the peripheral ID for MHU FMU page.">
     FMU_PIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR2--MHU-FMU-Peripheral-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR2--MHU-FMU-Peripheral-ID-2-Register?lang=en" title="Returns byte[2] of the peripheral ID for MHU FMU page.">
     FMU_PIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR3--MHU-FMU-Peripheral-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR3--MHU-FMU-Peripheral-ID-3-Register?lang=en" title="Returns byte[3] of the peripheral ID for MHU FMU page.">
     FMU_PIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Peripheral ID 3 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR0--MHU-FMU-Component-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR0--MHU-FMU-Component-ID-0-Register?lang=en" title="Returns byte[0] of the component ID for MHU FMU page.">
     FMU_CIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Component ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR1--MHU-FMU-Component-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR1--MHU-FMU-Component-ID-1-Register?lang=en" title="Returns byte[1] of the component ID for MHU FMU page.">
     FMU_CIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Component ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR2--MHU-FMU-Component-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR2--MHU-FMU-Component-ID-2-Register?lang=en" title="Returns byte[2] of the component ID for MHU FMU page.">
     FMU_CIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MHU FMU Component ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR3--MHU-FMU-Component-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR3--MHU-FMU-Component-ID-3-Register?lang=en" title="Returns byte[3] of the component ID for MHU FMU page.">
     FMU_CIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RO
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MHU FMU Component ID 3 Register
   </td>
  </tr>
 </tbody>
</table>
