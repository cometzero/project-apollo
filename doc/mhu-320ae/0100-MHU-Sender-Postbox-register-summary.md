# MHU Sender Postbox register summary

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary>

### MHU Sender Postbox register summary

The following summary table provides an overview of IMPLEMENTATION DEFINED memory-mapped MHU Sender Postbox (MHUS.PBX) registers.

For more information on registers listed in the table, click on the link associated with the register name.

For registers without a listed reset value, see the individual field resets documented on the register description pages or the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072).

<table class="documents-opcodes" id="ext_mhus_pbxsummary__regsumtable">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MHUS.PBX register summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d36762e99" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36762e101" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36762e103" rowspan="1">
    Type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36762e105" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36762e107" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d36762e109" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-BLK-ID--Postbox-Block-Identifier-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-BLK-ID--Postbox-Block-Identifier-Register?lang=en" title="Identifies the block as a Postbox.">
     PBX_BLK_ID
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
    Postbox Block Identifier Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FEAT-SPT0--Postbox-Feature-Support-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FEAT-SPT0--Postbox-Feature-Support-0-Register?lang=en" title="Returns information on supported MHU features">
     PBX_FEAT_SPT0
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
    Postbox Feature Support 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FEAT-SPT1--Postbox-Feature-Support-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FEAT-SPT1--Postbox-Feature-Support-1-Register?lang=en" title="Returns information on supported MHU features">
     PBX_FEAT_SPT1
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
    Postbox Feature Support 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-DBCH-CFG0--Postbox-Doorbell-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-DBCH-CFG0--Postbox-Doorbell-Channel-Configuration-0-Register?lang=en" title="Returns doorbell channel configuration information">
     PBX_DBCH_CFG0
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
    Postbox Doorbell Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-CFG0--Postbox-FIFO-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-CFG0--Postbox-FIFO-Channel-Configuration-0-Register?lang=en" title="Returns FIFO channel configuration information">
     PBX_FFCH_CFG0
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
    Postbox FIFO Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCH-CFG0--Postbox-Fast-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCH-CFG0--Postbox-Fast-Channel-Configuration-0-Register?lang=en" title="Returns fast channel configuration information">
     PBX_FCH_CFG0
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
    Postbox Fast Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0100
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CTRL--Postbox-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CTRL--Postbox-Control-Register?lang=en" title="This register contains control bits for the postbox">
     PBX_CTRL
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
    Postbox Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x0400
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-DBCH-INT-ST-n---Postbox-Doorbell-Channel-Interrupt-Status-n-Register--n---0---3?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-DBCH-INT-ST-n---Postbox-Doorbell-Channel-Interrupt-Status-n-Register--n---0---3?lang=en" title="Indicates whether there is an interrupt outstanding for a Doorbell Channel">
     PBX_DBCH_INT_ST&lt;n&gt;
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
    Postbox Doorbell Channel Interrupt Status n Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x0410
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-INT-ST-n---Postbox-FIFO-Channel-Interrupt-Status-n-Register--n---0---1?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-INT-ST-n---Postbox-FIFO-Channel-Interrupt-Status-n-Register--n---0---1?lang=en" title="Indicates whether there is an interrupt outstanding for the FIFO Channel.">
     PBX_FFCH_INT_ST&lt;n&gt;
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
    Postbox FIFO Channel Interrupt Status n Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-IIDR--Postbox-Implementer-Identification-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-IIDR--Postbox-Implementer-Identification-Register?lang=en" title="This field provides information on the Implementer of the MHU">
     PBX_IIDR
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
    Postbox Implementer Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-AIDR--Postbox-Architecture-Identification-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-AIDR--Postbox-Architecture-Identification-Register?lang=en" title="Provides information on the implemented MHU architecture">
     PBX_AIDR
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
    Postbox Architecture Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR4--Postbox-Peripheral-ID-4-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR4--Postbox-Peripheral-ID-4-Register?lang=en" title="Returns byte[4] of the peripheral ID for Postbox page.">
     PBX_PIDR4
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
    Postbox Peripheral ID 4 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR5--Postbox-Peripheral-ID-5-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR5--Postbox-Peripheral-ID-5-Register?lang=en" title="Returns byte[5] of the peripheral ID for Postbox page.">
     PBX_PIDR5
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
    Postbox Peripheral ID 5 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR6--Postbox-Peripheral-ID-6-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR6--Postbox-Peripheral-ID-6-Register?lang=en" title="Returns byte[6] of the peripheral ID for Postbox page.">
     PBX_PIDR6
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
    Postbox Peripheral ID 6 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR7--Postbox-Peripheral-ID-7-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR7--Postbox-Peripheral-ID-7-Register?lang=en" title="Returns byte[7] of the peripheral ID for Postbox page.">
     PBX_PIDR7
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
    Postbox Peripheral ID 7 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR0--Postbox-Peripheral-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR0--Postbox-Peripheral-ID-0-Register?lang=en" title="Returns byte[0] of the peripheral ID for Postbox page.">
     PBX_PIDR0
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
    Postbox Peripheral ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR1--Postbox-Peripheral-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR1--Postbox-Peripheral-ID-1-Register?lang=en" title="Returns byte[1] of the peripheral ID for Postbox page.">
     PBX_PIDR1
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
    Postbox Peripheral ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR2--Postbox-Peripheral-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR2--Postbox-Peripheral-ID-2-Register?lang=en" title="Returns byte[2] of the peripheral ID for Postbox page.">
     PBX_PIDR2
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
    Postbox Peripheral ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR3--Postbox-Peripheral-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-PIDR3--Postbox-Peripheral-ID-3-Register?lang=en" title="Returns byte[3] of the peripheral ID for Postbox page.">
     PBX_PIDR3
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
    Postbox Peripheral ID 3 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR0--Postbox-Component-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR0--Postbox-Component-ID-0-Register?lang=en" title="Returns byte[0] of the component ID for Postbox page.">
     PBX_CIDR0
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
    Postbox Component ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR1--Postbox-Component-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR1--Postbox-Component-ID-1-Register?lang=en" title="Returns byte[1] of the component ID for Postbox page.">
     PBX_CIDR1
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
    Postbox Component ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR2--Postbox-Component-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR2--Postbox-Component-ID-2-Register?lang=en" title="Returns byte[2] of the component ID for Postbox page.">
     PBX_CIDR2
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
    Postbox Component ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FFC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR3--Postbox-Component-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CIDR3--Postbox-Component-ID-3-Register?lang=en" title="Returns byte[3] of the component ID for Postbox page.">
     PBX_CIDR3
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
    Postbox Component ID 3 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--ST--Postbox-Doorbell-Channel-Window--n--Status-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--ST--Postbox-Doorbell-Channel-Window--n--Status-Register--n---0---127?lang=en" title="Returns doorbell channel flags">
     PDBCW&lt;n&gt;_ST
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
    Postbox Doorbell Channel Window &lt;n&gt; Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x100C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--SET--Postbox-Doorbell-Channel-Window--n--Set-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--SET--Postbox-Doorbell-Channel-Window--n--Set-Register--n---0---127?lang=en" title="Allows setting doorbell channel flags">
     PDBCW&lt;n&gt;_SET
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
    Postbox Doorbell Channel Window &lt;n&gt; Set Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-ST--Postbox-Doorbell-Channel-Window--n--Interrupt-Status-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-ST--Postbox-Doorbell-Channel-Window--n--Interrupt-Status-Register--n---0---127?lang=en" title="Returns doorbell channel interrupt status">
     PDBCW&lt;n&gt;_INT_ST
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
    Postbox Doorbell Channel Window &lt;n&gt; Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-CLR--Postbox-Doorbell-Channel-Window--n--Interrupt-Clear-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-CLR--Postbox-Doorbell-Channel-Window--n--Interrupt-Clear-Register--n---0---127?lang=en" title="Register for clearing doorbell channel interrupt status">
     PDBCW&lt;n&gt;_INT_CLR
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
    Postbox Doorbell Channel Window &lt;n&gt; Interrupt Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-EN--Postbox-Doorbell-Channel-Window--n--Interrupt-Enable-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-EN--Postbox-Doorbell-Channel-Window--n--Interrupt-Enable-Register--n---0---127?lang=en" title="Register for configuring doorbell channel interrupt enables">
     PDBCW&lt;n&gt;_INT_EN
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
    Postbox Doorbell Channel Window &lt;n&gt; Interrupt Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x101C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--CTRL--Postbox-Doorbell-Channel-Window--n--Control-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--CTRL--Postbox-Doorbell-Channel-Window--n--Control-Register--n---0---127?lang=en" title="This register contains control bits for doorbell channels">
     PDBCW&lt;n&gt;_CTRL
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
    Postbox Doorbell Channel Window &lt;n&gt; Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY64--Postbox-FIFO-Channel-Window--n--Payload-Register--64bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY64--Postbox-FIFO-Channel-Window--n--Payload-Register--64bit-access---n---0---63?lang=en" title="A 64bit access to the PFFCW&lt;n&gt;_PAY register. The bit descriptions for this register depend on whether the access is a write or a read.">
     PFFCW&lt;n&gt;_PAY64
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
    Postbox FIFO Channel Window &lt;n&gt; Payload Register (64bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY32--Postbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY32--Postbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the PFFCW&lt;n&gt;_PAY register. The bit descriptions for this register depend on whether the access is a write or a read.">
     PFFCW&lt;n&gt;_PAY32
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
    Postbox FIFO Channel Window &lt;n&gt; Payload Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2004
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY32--Postbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY32--Postbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the PFFCW&lt;n&gt;_PAY register. The bit descriptions for this register depend on whether the access is a write or a read.">
     PFFCW&lt;n&gt;_PAY32
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
    Postbox FIFO Channel Window &lt;n&gt; Payload Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en" title="Provides access to the flags of the entry of the FIFO pointed to by the write pointer.">
     PFFCW&lt;n&gt;_FLG
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
    Postbox FIFO Channel Window &lt;n&gt; Flag Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-ST--Postbox-FIFO-Channel-Window--n--Interrupt-Status-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-ST--Postbox-FIFO-Channel-Window--n--Interrupt-Status-Register--n---0---63?lang=en" title="Returns FIFO channel interrupt status">
     PFFCW&lt;n&gt;_INT_ST
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
    Postbox FIFO Channel Window &lt;n&gt; Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-CLR--Postbox-FIFO-Channel-Window--n--Interrupt-Clear-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-CLR--Postbox-FIFO-Channel-Window--n--Interrupt-Clear-Register--n---0---63?lang=en" title="Register for clearing FIFO channel interrupt status">
     PFFCW&lt;n&gt;_INT_CLR
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
    Postbox FIFO Channel Window &lt;n&gt; Interrupt Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-EN--Postbox-FIFO-Channel-Window--n--Interrupt-Enable-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-EN--Postbox-FIFO-Channel-Window--n--Interrupt-Enable-Register--n---0---63?lang=en" title="Register for configuring doorbell channel interrupt enables">
     PFFCW&lt;n&gt;_INT_EN
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
    Postbox FIFO Channel Window &lt;n&gt; Interrupt Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--CTRL--Postbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--CTRL--Postbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en" title="This register contains control bits for FIFO channels">
     PFFCW&lt;n&gt;_CTRL
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
    Postbox FIFO Channel Window &lt;n&gt; Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2024
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ST--Postbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ST--Postbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en" title="Contains status information for FIFO channel">
     PFFCW&lt;n&gt;_ST
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
    Postbox FIFO Channel Window &lt;n&gt; Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2028
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ACK-CNT--Postbox-FIFO-Channel-Window--n--Acknowledge-Counter-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ACK-CNT--Postbox-FIFO-Channel-Window--n--Acknowledge-Counter-Register--n---0---63?lang=en" title="Allows determining the number of acknowledged FIFO channel transfers">
     PFFCW&lt;n&gt;_ACK_CNT
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
    Postbox FIFO Channel Window &lt;n&gt; Acknowledge Counter Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x202C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--TIDE--Postbox-FIFO-Channel-Window--n--Tidemark-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--TIDE--Postbox-FIFO-Channel-Window--n--Tidemark-Register--n---0---63?lang=en" title="Allows configuration of the low and high tidemark thresholds for the Sender tidemark events">
     PFFCW&lt;n&gt;_TIDE
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
    Postbox FIFO Channel Window &lt;n&gt; Tidemark Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x3000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY32--Postbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY32--Postbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023?lang=en" title="Access to payload of Fast Channel &lt;n&gt;">
     PFCW&lt;n&gt;_PAY32
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
    Postbox Fast Channel Window &lt;n&gt; Payload 32bit Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (8 * n) + 0x3000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY64--Postbox-Fast-Channel-Window--n--Payload-64bit-Register--n---0---511?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY64--Postbox-Fast-Channel-Window--n--Payload-64bit-Register--n---0---511?lang=en" title="Access to payload of Fast Channel &lt;n&gt;">
     PFCW&lt;n&gt;_PAY64
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
    Postbox Fast Channel Window &lt;n&gt; Payload 64bit Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCTRL--Postbox-Feature-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCTRL--Postbox-Feature-Control-Register?lang=en" title="Controls non-architectural postbox functionality">
     PBX_FCTRL
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
    Postbox Feature Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xF010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FIFO-ERRINS--Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FIFO-ERRINS--Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register?lang=en" title="Enables ECC error insertion in the Postbox FIFO channel RAM. The bit descriptions for this register depend on whether the access is a read or a write.">
     PBX_FIFO_ERRINS
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RW
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Postbox FIFO channel RAM ECC Error Insertion Register
   </td>
  </tr>
 </tbody>
</table>
