# High Level System Address Map

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Memory-Map-overview/High-Level-System-Address-Map>

### High Level System Address Map

Security values do not define privileged or unprivileged accessibility. These are defined by the PPC, or by the register blocks that is mapped to each area. See lower-level details of each area for details.

The System Address Map defines the following values for accessibility:

S
:   Secure Access

NS
:   Non-secure

NSC
:   Non-Secure Callable

> ### Note
>
> 1. The NSC values are defined through registers in the Secure Access Configuration registers.
> 2. IF HASCRYPTO = 0, this region is reserved and responds with bus error.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   High Level System Address Map
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
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e110" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e114" rowspan="1">
    <p>
     Address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e118" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e122" rowspan="1">
    <p>
     Region
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e126" rowspan="1">
    <p>
     Alias
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134022e131" rowspan="1">
    <p>
     IDAU Region Values
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d134022e135" rowspan="1">
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
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x00FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Instruction TCM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" title="The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:">
      CPU TCM memories
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x01000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x09FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     192MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Code Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Code Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0A000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0AFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0B000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0BFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0CFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU2 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0D000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0DFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU3 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0E000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0E001FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell NVM Code
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell Code Access to NVM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" href="/documentation/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" title="When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.">
      Has-Crypto configuration
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0E002000
     </span>
     -
     <span class="documents-g.number.hex">
      0x0FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 0
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
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
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x10000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x10FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Instruction TCM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" title="The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:">
      CPU TCM memories
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x11000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x19FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     192MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Code Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Code Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1A000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1AFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1B000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1BFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1C000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1CFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU2 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1D000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1DFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU3 ITCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1E000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1E001FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell NVM Code
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell Code Access to NVM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" href="/documentation/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" title="When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.">
      Has-Crypto configuration
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1E002000
     </span>
     -
     <span class="documents-g.number.hex">
      0x1FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 1
     </li>
     <li>
      NSC: CODENSC
     </li>
    </ul>
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
     9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x20000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x20FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     13
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Data TCM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" title="The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:">
      CPU TCM memories
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x21000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x21FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Volatile Memory
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     14
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Volatile Memory
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Volatile-Memory-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Volatile-Memory-Region?lang=en" title="CRSAS Ma1 supports up to four internal Volatile Memory (VM) Banks. While these are typically implemented as SRAMs, actual memories used are IMPLEMENTATION DEFINED.">
      Volatile Memory Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x22000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x23FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
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
     11.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x24000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x24FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x25000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x25FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x26000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x26FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU2 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x27000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x27FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU3 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x28000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x2FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 2
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     13
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x30000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x30FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Data TCM.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-TCM-memories?lang=en" title="The processors in CRSAS Ma1 are configured to implement Tightly Coupled Memories (TCM) for Instruction and Data. These memories reside in the following location from the perspective of each CPU core:">
      CPU TCM memories
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     14
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x31000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x31FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Volatile memory
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Internal Multi-bank Volatile Memory.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Volatile-Memory-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Volatile-Memory-Region?lang=en" title="CRSAS Ma1 supports up to four internal Volatile Memory (VM) Banks. While these are typically implemented as SRAMs, actual memories used are IMPLEMENTATION DEFINED.">
      Volatile Memory Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x32000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x33FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
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
     15.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x34000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x34FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x35000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x35FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x36000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x36FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU2 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x37000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x37FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU3 DTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11.4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" href="/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en" title="A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.">
      TCM subordinate interface
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x38000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x3FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 3
     </li>
     <li>
      NSC: RAMNSC
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     17
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4000FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     27
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     18
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40010000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4001FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Private CPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Private Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region?lang=en" title="Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:">
      CPU Private Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     19
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40020000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4003FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     System Control Peripheral Region
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Control Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" title="The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD_AON domain or in the PD_MGMT domain if PILEVEL = 2. There are four regions in total as follows:">
      System Control Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40040000
     </span>
     -
     <span class="documents-g.number.hex">
      0x400FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     768KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     21
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40100000
     </span>
     -
     <span class="documents-g.number.hex">
      0x47FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     127MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     22
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4800FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     23
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48010000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4801FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Private CPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Private Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region?lang=en" title="Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:">
      CPU Private Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     24
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48020000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4803FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     System Control
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Control Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" title="The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD_AON domain or in the PD_MGMT domain if PILEVEL = 2. There are four regions in total as follows:">
      System Control Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     25
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48040000
     </span>
     -
     <span class="documents-g.number.hex">
      0x480FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     768KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     26
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48100000
     </span>
     -
     <span class="documents-g.number.hex">
      0x4FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     127MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 4
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.">
      Peripheral Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     27
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5000FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     17
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50010000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5001FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Private CPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Private Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region?lang=en" title="Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:">
      CPU Private Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     29
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50020000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5003FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     System Control
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Control Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" title="The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD_AON domain or in the PD_MGMT domain if PILEVEL = 2. There are four regions in total as follows:">
      System Control Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     30
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50040000
     </span>
     -
     <span class="documents-g.number.hex">
      0x500FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     786KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50100000
     </span>
     -
     <span class="documents-g.number.hex">
      0x57FFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     127MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.">
      Peripheral Interconnect Expansion Interfaces
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5800FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     22
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     33
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58010000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5801FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Private CPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Processor Private Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region?lang=en" title="Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:">
      CPU Private Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     34
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58020000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5803FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     System Control
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Control Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en" title="The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD_AON domain or in the PD_MGMT domain if PILEVEL = 2. There are four regions in total as follows:">
      System Control Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     35
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58040000
     </span>
     -
     <span class="documents-g.number.hex">
      0x580FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     768KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripherals
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region?lang=en" title="The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:">
      Peripheral Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     36
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58100000
     </span>
     -
     <span class="documents-g.number.hex">
      0x5FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     127MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 5
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.">
      Peripheral Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     37
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x60000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x6FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 6
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     38
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x70000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x7FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 7
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     39
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x80000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x8FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: 8
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     40
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x90000000
     </span>
     -
     <span class="documents-g.number.hex">
      0x9FFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: 9
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     41
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xA0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xAFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: A
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     42
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xB0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xBFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: B
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     43
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xC0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xCFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: C
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     44
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xD0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xDFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     256MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Main Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: D
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Main Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.">
      Main Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     45
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xE00FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PPB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Exempt
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Private Peripheral Bus Region. Local to the CPU.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region?lang=en" title="Each CPU, as defined by the ARMv8-M architecture specification, hosts a local Private Peripheral Bus Region (PPB) at address E000_0000 to E00F_FFFF. This region is typically for integration with CoreSight debug and trace components that is normally local to each CPU and is not intended for general peripheral usage.">
      CPU Private Peripheral Bus Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     46
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE0100000
     </span>
     -
     <span class="documents-g.number.hex">
      0xE01FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Debug System
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     49
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: E
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Debug System Access Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Debug-System-Access-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Debug-System-Access-Region?lang=en" title="CRSAS Ma1 supports two key configuration options for the debug system:">
      Debug System Access Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     47
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE0200000
     </span>
     -
     <span class="documents-g.number.hex">
      0xEFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     254MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: NS
     </li>
     <li>
      IDAUID: E
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.">
      Peripheral Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     48
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF0000000
     </span>
     -
     <span class="documents-g.number.hex">
      0xF00FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: F
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
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
     49
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF0100000
     </span>
     -
     <span class="documents-g.number.hex">
      0xF01FFFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1MB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Debug System
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     46
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: F
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Debug System Access Region.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Debug-System-Access-Region?lang=en" href="/documentation/102803/0000/Programmers-model/Debug-System-Access-Region?lang=en" title="CRSAS Ma1 supports two key configuration options for the debug system:">
      Debug System Access Region
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     50
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF0200000
     </span>
     -
     <span class="documents-g.number.hex">
      0xFFFFFFFF
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     254MB
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Peripheral Expansion
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      Security: S
     </li>
     <li>
      IDAUID: F
     </li>
     <li>
      NSC: 0
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Manager Peripheral Expansion Interface.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" href="/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en" title="CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.">
      Peripheral Interconnect Expansion Interfaces
     </a>
     .
    </p>
   </td>
  </tr>
 </tbody>
</table>
