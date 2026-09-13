# AArch64 RAS registers summary

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary>

### AArch64 RAS registers summary

The IMPLEMENTATION DEFINED cluster RAS registers are accessible either from System register accesses from the cores or from memory-mapped accesses on the utility bus.

The summary table provides an overview of the IMPLEMENTATION DEFINED AArch64 cluster RAS registers in the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> For registers without a listed reset value refer to the individual field resets documented on the register description pages.

For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="zng1733414894902__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RAS registers summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e88" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e90" rowspan="1">
    Op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e92" rowspan="1">
    Op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e94" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e96" rowspan="1">
    CRm
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e98" rowspan="1">
    Op2
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e100" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d279387e102" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d279387e104" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXFR-EL1--Selected-Error-Record-Feature-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXFR-EL1--Selected-Error-Record-Feature-Register?lang=en" title="Accesses ext-CLUSTERRAS_ERR0FR when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXFR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXCTLR-EL1--Selected-Error-Record-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXCTLR-EL1--Selected-Error-Record-Control-Register?lang=en" title="Accesses ext-CLUSTERRAS_ERR0CTLR when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXCTLR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXSTATUS-EL1--Selected-Error-Record-Primary-Status-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXSTATUS-EL1--Selected-Error-Record-Primary-Status-Register?lang=en" title="Accesses ext-CLUSTERRAS_ERR0STATUS when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXSTATUS_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Primary Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGF-EL1--Selected-Pseudo-fault-Generation-Feature-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGF-EL1--Selected-Pseudo-fault-Generation-Feature-Register?lang=en" title="Accesses the ext-CLUSTERRAS_ERR0PFGF register when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXPFGF_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Pseudo-fault Generation Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCTL-EL1--Selected-Pseudo-fault-Generation-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCTL-EL1--Selected-Pseudo-fault-Generation-Control-Register?lang=en" title="Accesses the ext-CLUSTERRAS_ERR0PFGCTL register when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXPFGCTL_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Pseudo-fault Generation Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCDN-EL1--Selected-Pseudo-fault-Generation-Countdown-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCDN-EL1--Selected-Pseudo-fault-Generation-Countdown-Register?lang=en" title="Accesses the ext-CLUSTERRAS_ERR0PFGCDN register when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXPFGCDN_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Pseudo-fault Generation Countdown Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC0-EL1--Selected-Error-Record-Miscellaneous-Register-0?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC0-EL1--Selected-Error-Record-Miscellaneous-Register-0?lang=en" title="Accesses ext-CLUSTERRAS_ERR0MISC0 when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXMISC0_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Miscellaneous Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC1-EL1--Selected-Error-Record-Miscellaneous-Register-1?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC1-EL1--Selected-Error-Record-Miscellaneous-Register-1?lang=en" title="Accesses ext-CLUSTERRAS_ERR0MISC1 when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXMISC1_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Miscellaneous Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC2-EL1--Selected-Error-Record-Miscellaneous-Register-2?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC2-EL1--Selected-Error-Record-Miscellaneous-Register-2?lang=en" title="Accesses ext-CLUSTERRAS_ERR0MISC2 when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXMISC2_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Selected Error Record Miscellaneous Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC3-EL1--Selected-Error-Record-Miscellaneous-Register-3?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC3-EL1--Selected-Error-Record-Miscellaneous-Register-3?lang=en" title="Accesses ext-CLUSTERRAS_ERR0MISC3 when the value in AArch64-ERRSELR_EL1.SEL is set to 0.">
     ERXMISC3_EL1
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Selected Error Record Miscellaneous Register 3
   </td>
  </tr>
 </tbody>
</table>
