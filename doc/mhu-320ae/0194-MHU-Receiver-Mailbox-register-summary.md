# MHU Receiver Mailbox register summary

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary>

### MHU Receiver Mailbox register summary

The following summary table provides an overview of IMPLEMENTATION DEFINED memory-mapped MHU Receiver Mailbox (MHUR.MBX) registers.

For more information on registers listed in the table, click on the link associated with the register name.

For registers without a listed reset value, see the individual field resets documented on the register description pages or the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072).

<table class="documents-opcodes" id="ext_mhur_mbxsummary__regsumtable">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MHUR.MBX register summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d29686e99" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29686e101" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29686e103" rowspan="1">
    Type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29686e105" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29686e107" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d29686e109" rowspan="1">
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
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-BLK-ID--Mailbox-Block-Identifier-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-BLK-ID--Mailbox-Block-Identifier-Register?lang=en" title="Identifies the block as a Mailbox.">
     MBX_BLK_ID
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
    Mailbox Block Identifier Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FEAT-SPT0--Mailbox-Feature-Support-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FEAT-SPT0--Mailbox-Feature-Support-0-Register?lang=en" title="Returns information on supported MHU features">
     MBX_FEAT_SPT0
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
    Mailbox Feature Support 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FEAT-SPT1--Mailbox-Feature-Support-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FEAT-SPT1--Mailbox-Feature-Support-1-Register?lang=en" title="Returns information on supported MHU features">
     MBX_FEAT_SPT1
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
    Mailbox Feature Support 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DBCH-CFG0--Mailbox-Doorbell-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DBCH-CFG0--Mailbox-Doorbell-Channel-Configuration-0-Register?lang=en" title="Returns doorbell channel configuration information">
     MBX_DBCH_CFG0
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
    Mailbox Doorbell Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FFCH-CFG0--Mailbox-FIFO-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FFCH-CFG0--Mailbox-FIFO-Channel-Configuration-0-Register?lang=en" title="Returns FIFO channel configuration information">
     MBX_FFCH_CFG0
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
    Mailbox FIFO Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-CFG0--Mailbox-Fast-Channel-Configuration-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-CFG0--Mailbox-Fast-Channel-Configuration-0-Register?lang=en" title="Returns fast channel configuration information">
     MBX_FCH_CFG0
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
    Mailbox Fast Channel Configuration 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0100
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CTRL--Mailbox-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CTRL--Mailbox-Control-Register?lang=en" title="This register contains control bits for the mailbox">
     MBX_CTRL
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
    Mailbox Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0140
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-CTRL--Mailbox-Fast-Channel-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-CTRL--Mailbox-Fast-Channel-Control-Register?lang=en" title="Controls the Fast Channels in the Mailbox">
     MBX_FCH_CTRL
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
    Mailbox Fast Channel Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0144
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-EN--Mailbox-Fast-Channel-Group-Interrupt-Enable-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-EN--Mailbox-Fast-Channel-Group-Interrupt-Enable-Register?lang=en" title="Controls whether a Fast Channel Group contributes to the Mailbox Combined interrupt">
     MBX_FCG_INT_EN
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
    Mailbox Fast Channel Group Interrupt Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x0400
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DBCH-INT-ST-n---Mailbox-Doorbell-Channel-Interrupt-Status--n--Register--n---0---3?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DBCH-INT-ST-n---Mailbox-Doorbell-Channel-Interrupt-Status--n--Register--n---0---3?lang=en" title="Indicates whether there is an interrupt outstanding for the Doorbell Channel">
     MBX_DBCH_INT_ST&lt;n&gt;
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
    Mailbox Doorbell Channel Interrupt Status &lt;n&gt; Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x0410
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FFCH-INT-ST-n---Mailbox-FIFO-Channel-Interrupt-Status--n--Register--n---0---1?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FFCH-INT-ST-n---Mailbox-FIFO-Channel-Interrupt-Status--n--Register--n---0---1?lang=en" title="Indicates whether there is an interrupt outstanding for the FIFO Channel.">
     MBX_FFCH_INT_ST&lt;n&gt;
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
    Mailbox FIFO Channel Interrupt Status &lt;n&gt; Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0470
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-ST--Mailbox-Fast-Channel-Group-Interrupt-Status-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-ST--Mailbox-Fast-Channel-Group-Interrupt-Status-Register?lang=en" title="Provides the status of each Fast Channel Group Transfer interrupt">
     MBX_FCG_INT_ST
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
    Mailbox Fast Channel Group Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x0480
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-GRP-n--INT-ST--Mailbox-Fast-Channel-Group--n--Interrupt-Status-Register--n---0---31?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-GRP-n--INT-ST--Mailbox-Fast-Channel-Group--n--Interrupt-Status-Register--n---0---31?lang=en" title="Provides the status of each Fast Channel with the Fast Channel Transfer Group &lt;n&gt;">
     MBX_FCH_GRP&lt;n&gt;_INT_ST
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
    Mailbox Fast Channel Group &lt;n&gt; Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-IIDR--Mailbox-Implementer-Identification-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-IIDR--Mailbox-Implementer-Identification-Register?lang=en" title="This field provides information on the Implementer of the MHU">
     MBX_IIDR
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
    Mailbox Implementer Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-AIDR--Mailbox-Architecture-Identification-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-AIDR--Mailbox-Architecture-Identification-Register?lang=en" title="Provides information on the implemented MHU architecture">
     MBX_AIDR
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
    Mailbox Architecture Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR4--Mailbox-Peripheral-ID-4-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR4--Mailbox-Peripheral-ID-4-Register?lang=en" title="Returns byte[4] of the peripheral ID for Mailbox page.">
     MBX_PIDR4
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
    Mailbox Peripheral ID 4 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR5--Mailbox-Peripheral-ID-5-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR5--Mailbox-Peripheral-ID-5-Register?lang=en" title="Returns byte[5] of the peripheral ID for Mailbox page.">
     MBX_PIDR5
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
    Mailbox Peripheral ID 5 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FD8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR6--Mailbox-Peripheral-ID-6-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR6--Mailbox-Peripheral-ID-6-Register?lang=en" title="Returns byte[6] of the peripheral ID for Mailbox page.">
     MBX_PIDR6
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
    Mailbox Peripheral ID 6 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR7--Mailbox-Peripheral-ID-7-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR7--Mailbox-Peripheral-ID-7-Register?lang=en" title="Returns byte[7] of the peripheral ID for Mailbox page.">
     MBX_PIDR7
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
    Mailbox Peripheral ID 7 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR0--Mailbox-Peripheral-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR0--Mailbox-Peripheral-ID-0-Register?lang=en" title="Returns byte[0] of the peripheral ID for Mailbox page.">
     MBX_PIDR0
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
    Mailbox Peripheral ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR1--Mailbox-Peripheral-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR1--Mailbox-Peripheral-ID-1-Register?lang=en" title="Returns byte[1] of the peripheral ID for Mailbox page.">
     MBX_PIDR1
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
    Mailbox Peripheral ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR2--Mailbox-Peripheral-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR2--Mailbox-Peripheral-ID-2-Register?lang=en" title="Returns byte[2] of the peripheral ID for Mailbox page.">
     MBX_PIDR2
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
    Mailbox Peripheral ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR3--Mailbox-Peripheral-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR3--Mailbox-Peripheral-ID-3-Register?lang=en" title="Returns byte[3] of the peripheral ID for Mailbox page.">
     MBX_PIDR3
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
    Mailbox Peripheral ID 3 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR0--Mailbox-Component-ID-0-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR0--Mailbox-Component-ID-0-Register?lang=en" title="Returns byte[0] of the component ID for Mailbox page.">
     MBX_CIDR0
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
    Mailbox Component ID 0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR1--Mailbox-Component-ID-1-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR1--Mailbox-Component-ID-1-Register?lang=en" title="Returns byte[1] of the component ID for Mailbox page.">
     MBX_CIDR1
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
    Mailbox Component ID 1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR2--Mailbox-Component-ID-2-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR2--Mailbox-Component-ID-2-Register?lang=en" title="Returns byte[2] of the component ID for Mailbox page.">
     MBX_CIDR2
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
    Mailbox Component ID 2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0FFC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR3--Mailbox-Component-ID-3-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CIDR3--Mailbox-Component-ID-3-Register?lang=en" title="Returns byte[3] of the component ID for Mailbox page.">
     MBX_CIDR3
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
    Mailbox Component ID 3 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--ST--Mailbox-Doorbell-Channel-Window--n--Status-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--ST--Mailbox-Doorbell-Channel-Window--n--Status-Register--n---0---127?lang=en" title="Returns doorbell channel flags">
     MDBCW&lt;n&gt;_ST
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
    Mailbox Doorbell Channel Window &lt;n&gt; Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1004
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--ST-MSK--Mailbox-Doorbell-Channel-Window--n--Status-Masked-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--ST-MSK--Mailbox-Doorbell-Channel-Window--n--Status-Masked-Register--n---0---127?lang=en" title="Returns doorbell channel flags after combining with the mask">
     MDBCW&lt;n&gt;_ST_MSK
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
    Mailbox Doorbell Channel Window &lt;n&gt; Status Masked Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--CLR--Mailbox-Doorbell-Channel-Window--n--Clear-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--CLR--Mailbox-Doorbell-Channel-Window--n--Clear-Register--n---0---127?lang=en" title="Allows clearing doorbell channel flags">
     MDBCW&lt;n&gt;_CLR
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
    Mailbox Doorbell Channel Window &lt;n&gt; Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-ST--Mailbox-Doorbell-Channel-Window--n--Mask-Status-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-ST--Mailbox-Doorbell-Channel-Window--n--Mask-Status-Register--n---0---127?lang=en" title="Returns doorbell channel mask">
     MDBCW&lt;n&gt;_MSK_ST
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
    Mailbox Doorbell Channel Window &lt;n&gt; Mask Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-SET--Mailbox-Doorbell-Channel-Window--n--Mask-Set-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-SET--Mailbox-Doorbell-Channel-Window--n--Mask-Set-Register--n---0---127?lang=en" title="Allows setting doorbell channel mask">
     MDBCW&lt;n&gt;_MSK_SET
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
    Mailbox Doorbell Channel Window &lt;n&gt; Mask Set Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x1018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-CLR--Mailbox-Doorbell-Channel-Window--n--Mask-Clear-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-CLR--Mailbox-Doorbell-Channel-Window--n--Mask-Clear-Register--n---0---127?lang=en" title="Allows clearing doorbell channel mask">
     MDBCW&lt;n&gt;_MSK_CLR
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
    Mailbox Doorbell Channel Window &lt;n&gt; Mask Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (32 * n) + 0x101C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--CTRL--Mailbox-Doorbell-Channel-Window--n--Control-Register--n---0---127?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--CTRL--Mailbox-Doorbell-Channel-Window--n--Control-Register--n---0---127?lang=en" title="This register contains control bits for doorbell channels">
     MDBCW&lt;n&gt;_CTRL
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
    Mailbox Doorbell Channel Window &lt;n&gt; Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY64--Mailbox-FIFO-Channel-Window--n--Payload-Register--64bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY64--Mailbox-FIFO-Channel-Window--n--Payload-Register--64bit-access---n---0---63?lang=en" title="A 64bit access to the MFFCW&lt;n&gt;_PAY register.">
     MFFCW&lt;n&gt;_PAY64
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
    Mailbox FIFO Channel Window &lt;n&gt; Payload Register (64bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY32--Mailbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY32--Mailbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the MFFCW&lt;n&gt;_PAY register.">
     MFFCW&lt;n&gt;_PAY32
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
    Mailbox FIFO Channel Window &lt;n&gt; Payload Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2004
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY32--Mailbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY32--Mailbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the MFFCW&lt;n&gt;_PAY register.">
     MFFCW&lt;n&gt;_PAY32
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
    Mailbox FIFO Channel Window &lt;n&gt; Payload Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG64--Mailbox-FIFO-Channel-Window--n--Flag-Register--64bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG64--Mailbox-FIFO-Channel-Window--n--Flag-Register--64bit-access---n---0---63?lang=en" title="A 64bit access to the MFFCW&lt;n&gt;_FLG register.">
     MFFCW&lt;n&gt;_FLG64
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
    Mailbox FIFO Channel Window &lt;n&gt; Flag Register (64bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG32--MailboxPostbox-FIFO-Channel-Window--n--Flag-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG32--MailboxPostbox-FIFO-Channel-Window--n--Flag-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the MFFCW&lt;n&gt;_FLG register.">
     MFFCW&lt;n&gt;_FLG32
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
    MailboxPostbox FIFO Channel Window &lt;n&gt; Flag Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x200C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG32--MailboxPostbox-FIFO-Channel-Window--n--Flag-Register--32bit-access---n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG32--MailboxPostbox-FIFO-Channel-Window--n--Flag-Register--32bit-access---n---0---63?lang=en" title="A 32bit access to the MFFCW&lt;n&gt;_FLG register.">
     MFFCW&lt;n&gt;_FLG32
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
    MailboxPostbox FIFO Channel Window &lt;n&gt; Flag Register (32bit access)
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-ST--Mailbox-FIFO-Channel-Window--n--Interrupt-Status-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-ST--Mailbox-FIFO-Channel-Window--n--Interrupt-Status-Register--n---0---63?lang=en" title="Returns FIFO channel interrupt status">
     MFFCW&lt;n&gt;_INT_ST
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
    Mailbox FIFO Channel Window &lt;n&gt; Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-CLR--Mailbox-FIFO-Channel-Window--n--Interrupt-Clear-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-CLR--Mailbox-FIFO-Channel-Window--n--Interrupt-Clear-Register--n---0---63?lang=en" title="Register for clearing FIFO channel interrupt status">
     MFFCW&lt;n&gt;_INT_CLR
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
    Mailbox FIFO Channel Window &lt;n&gt; Interrupt Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-EN--Mailbox-FIFO-Channel-Window--n--Interrupt-Enable-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-EN--Mailbox-FIFO-Channel-Window--n--Interrupt-Enable-Register--n---0---63?lang=en" title="Register for configuring FIFO channel interrupt enables">
     MFFCW&lt;n&gt;_INT_EN
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
    Mailbox FIFO Channel Window &lt;n&gt; Interrupt Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--CTRL--Mailbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--CTRL--Mailbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en" title="This register contains control bits for FIFO channels">
     MFFCW&lt;n&gt;_CTRL
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
    Mailbox FIFO Channel Window &lt;n&gt; Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2024
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--ST--Mailbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--ST--Mailbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en" title="Contains status information for FIFO channel">
     MFFCW&lt;n&gt;_ST
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
    Mailbox FIFO Channel Window &lt;n&gt; Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x2028
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FIFO-POP--Mailbox-FIFO-Channel-Window--n--FIFO-POP-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FIFO-POP--Mailbox-FIFO-Channel-Window--n--FIFO-POP-Register--n---0---63?lang=en" title="Register for popping bytes from a FIFO channel when writing to it">
     MFFCW&lt;n&gt;_FIFO_POP
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
    Mailbox FIFO Channel Window &lt;n&gt; FIFO POP Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (64 * n) + 0x202C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--TIDE--Mailbox-FIFO-Channel-Window--n--Tidemark-Register--n---0---63?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--TIDE--Mailbox-FIFO-Channel-Window--n--Tidemark-Register--n---0---63?lang=en" title="Allows configuration of the low and high tidemark thresholds for the Receiver tidemark events">
     MFFCW&lt;n&gt;_TIDE
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
    Mailbox FIFO Channel Window &lt;n&gt; Tidemark Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (4 * n) + 0x3000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFCW-n--PAY32--Mailbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFCW-n--PAY32--Mailbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023?lang=en" title="Access to payload of Fast Channel &lt;n&gt;">
     MFCW&lt;n&gt;_PAY32
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
    Mailbox Fast Channel Window &lt;n&gt; Payload 32bit Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    (8 * n) + 0x3000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFCW-n--PAY64--Mailbox-Fast-Channel-Window--n--Payload-64bit-Register--n---0---511?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFCW-n--PAY64--Mailbox-Fast-Channel-Window--n--Payload-64bit-Register--n---0---511?lang=en" title="Access to payload of Fast Channel &lt;n&gt;">
     MFCW&lt;n&gt;_PAY64
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
    Mailbox Fast Channel Window &lt;n&gt; Payload 64bit Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCTRL--Mailbox-Feature-Control-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCTRL--Mailbox-Feature-Control-Register?lang=en" title="Controls non-architectural mailbox functionality">
     MBX_FCTRL
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
    Mailbox Feature Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DB-ERRINS--Mailbox-doorbell-channel-RAM-ECC-Error-Insertion-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DB-ERRINS--Mailbox-doorbell-channel-RAM-ECC-Error-Insertion-Register?lang=en" title="Enables ECC error insertion in the Mailbox doorbell channel RAM. The bit descriptions for this register depend on whether the access is a write or a read.">
     MBX_DB_ERRINS
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
    Mailbox doorbell channel RAM ECC Error Insertion Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FST-ERRINS--Mailbox-fast-channel-RAM-ECC-Error-Insertion-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FST-ERRINS--Mailbox-fast-channel-RAM-ECC-Error-Insertion-Register?lang=en" title="Enables ECC error insertion in the Mailbox Fast channel RAM. The bit descriptions for this register depend on whether the access is a write or a read.">
     MBX_FST_ERRINS
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
    Mailbox fast channel RAM ECC Error Insertion Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xF020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCFG-ERRINS--Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCFG-ERRINS--Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register?lang=en" title="Enables ECC error insertion in the Mailbox FIFO channel configuration RAM. The bit descriptions for this register depend on whether the access is a write or a read.">
     MBX_FCFG_ERRINS
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
    Mailbox FIFO channel config RAM ECC Error Insertion Register
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xF028
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FDATA-ERRINS--Mailbox-FIFO-channel-data-RAM-ECC-Error-Insertion-Register?lang=en" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FDATA-ERRINS--Mailbox-FIFO-channel-data-RAM-ECC-Error-Insertion-Register?lang=en" title="Enables ECC error insertion in the Mailbox FIFO channel data RAM. The bit descriptions for this register depend on whether the access is a write or a read.">
     MBX_FDATA_ERRINS
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
    Mailbox FIFO channel data RAM ECC Error Insertion Register
   </td>
  </tr>
 </tbody>
</table>
