# Non-secure Access Configuration Register Block

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block>

###

The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 0x4008\_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.

All registers reside in the PD\_SYS power domain and are reset by nWARMRESETSYS.

The following table lists the registers within this unit. Details of each register are described in the following subsections.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Non-secure Access Configuration Register Block register map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d81441e79" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81441e83" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81441e87" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81441e91" rowspan="1">
    <p>
     Reset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81441e95" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d81441e100" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x000
     </span>
     -
     <span class="documents-g.number.hex">
      0x08C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x090
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINNSPPPC0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Unprivileged Access Peripheral Protection Control 0 on Main Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPC0?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPC0?lang=en" title="Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each peripheral on the Main Interconnect that it controls through a PPC is only allowed Non-secure Privileged Access or is allowed Non-secure Unprivileged access as well.">
      MAINNSPPPC0
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x094
     </span>
     -
     <span class="documents-g.number.hex">
      0x09C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0A0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINNSPPPCEXP0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 0 Non-secure Unprivileged Access Peripheral Protection Control on Main Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to con&filig;gure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.">
      MAINNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0A4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINNSPPPCEXP1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 1 Non-secure Unprivileged Access Peripheral Protection Control on Main Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to con&filig;gure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.">
      MAINNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0A8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINNSPPPCEXP2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 2 Non-secure Unprivileged Access Peripheral Protection Control on Main Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to con&filig;gure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.">
      MAINNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0AC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINNSPPPCEXP3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 3 Non-secure Unprivileged Access Peripheral Protection Control on Main Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to con&filig;gure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.">
      MAINNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0B0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPC0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Unprivileged Access Peripheral Protection Control 0 on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en" title="Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPC0
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0B4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPC1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Unprivileged Access Peripheral Protection Control 1 on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en" title="Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Non-secure privileged access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPC1
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0B8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPUNSPORPL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU&lt;m&gt; PORPLRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Access NPU Privilege level reset state control, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en" title="The NPU power on reset Non-secure access privileged level reset control registers allow software to configure if each NPU resets to privileged or unprivileged state.">
      NPUNSPORPL
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0BC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPCEXP0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 0 Non-secure Unprivileged Access Peripheral Protection Control on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2, and 3 allow software to con&filig;gure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only allowed Non-secure privileged Access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPCEXP1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 1 Non-secure Unprivileged Access Peripheral Protection Control on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2, and 3 allow software to con&filig;gure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only allowed Non-secure privileged Access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPCEXP2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 2 Non-secure Unprivileged Access Peripheral Protection Control on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2, and 3 allow software to con&filig;gure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only allowed Non-secure privileged Access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0CC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHNSPPPCEXP3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Expansion 3 Non-secure Unprivileged Access Peripheral Protection Control on Peripheral Interconnect, see
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en" title="The Expansion Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2, and 3 allow software to con&filig;gure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only allowed Non-secure privileged Access or is allowed Non-secure unprivileged access as well.">
      PERIPHNSPPPCEXP{0-3}
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0D0
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xFCC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0004
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 4
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD4
     </span>
     -
     <span class="documents-g.number.hex">
      0xFDC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0053
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_003B
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 2
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFEC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 3
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_000D
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00F0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0005
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 2
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFFC
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CIDR3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B1
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Component ID 3
    </p>
   </td>
  </tr>
 </tbody>
</table>

- **[MAINNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPC0?lang=en)**
   Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each peripheral on the Main Interconnect that it controls through a PPC is only allowed Non-secure Privileged Access or is allowed Non-secure Unprivileged access as well.
- **[MAINNSPPPCEXP{0-3}](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3-?lang=en)**
   The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to conﬁgure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.
- **[PERIPHNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en)**
   Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well.
- **[PERIPHNSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en)**
   Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Non-secure privileged access or is allowed Non-secure unprivileged access as well.
- **[NPUNSPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en)**
   The NPU power on reset Non-secure access privileged level reset control registers allow software to configure if each NPU resets to privileged or unprivileged state.
- **[PERIPHNSPPPCEXP{0-3}](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPCEXP-0-3-?lang=en)**
   The Expansion Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2, and 3 allow software to conﬁgure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only allowed Non-secure privileged Access or is allowed Non-secure unprivileged access as well.
