# External cluster RAS registers

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Cluster-RAS-registers/External-cluster-RAS-registers>

### External cluster RAS registers

The cluster RAS registers are accessible either from memory-mapped accesses on the utility bus or from System register accesses from the cores.

The summary table provides an overview of all the cluster RAS registers in DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> - The cluster RAS registers are treated as RAZ/WI if either:
>   - The register is marked as Reserved.
>   - The register is accessed in the wrong Security state.
> - Any address that is not documented is treated as RAZ/WI.
> - The base address for the cluster RAS registers is 0x020000.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="zth1660577295040__d69e26">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS registers summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d39332e104" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39332e106" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39332e108" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39332e110" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d39332e112" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0FR--Error-Record-Feature-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0FR--Error-Record-Feature-Register?lang=en" title="Defines which of the common architecturally-defined features are implemented by the node and, of the implemented features, which are software programmable.">
     CLUSTERRAS_ERR0FR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0CTLR--Error-Record-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0CTLR--Error-Record-Control-Register?lang=en" title="The error control register contains enable bits for the node that writes to this record, which:">
     CLUSTERRAS_ERR0CTLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0STATUS--Error-Record-Primary-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0STATUS--Error-Record-Primary-Status-Register?lang=en" title="Contains status information for the error record, including:">
     CLUSTERRAS_ERR0STATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Primary Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0ADDR--Error-Record-Address-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0ADDR--Error-Record-Address-Register?lang=en" title="This register is reserved since the implementation does not provide an address with RAS errors.">
     CLUSTERRAS_ERR0ADDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Address Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC0--Error-Record-Miscellaneous-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC0--Error-Record-Miscellaneous-Register-0?lang=en" title="Miscellaneous error syndrome register. The Miscellaneous error syndrome register contains:">
     CLUSTERRAS_ERR0MISC0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Miscellaneous Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x028
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC1--Error-Record-Miscellaneous-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC1--Error-Record-Miscellaneous-Register-1?lang=en" title="Unimplemented error syndrome register.">
     CLUSTERRAS_ERR0MISC1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Miscellaneous Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC2--Error-Record-Miscellaneous-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC2--Error-Record-Miscellaneous-Register-2?lang=en" title="Unimplemented error syndrome register.">
     CLUSTERRAS_ERR0MISC2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Miscellaneous Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x038
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC3--Error-Record-Miscellaneous-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC3--Error-Record-Miscellaneous-Register-3?lang=en" title="Unimplemented error syndrome register.">
     CLUSTERRAS_ERR0MISC3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Error Record Miscellaneous Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x800
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGF--Pseudo-fault-Generation-Feature-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGF--Pseudo-fault-Generation-Feature-Register?lang=en" title="Defines which common architecturally-defined fault generation features are implemented.">
     CLUSTERRAS_ERR0PFGF
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Pseudo-fault Generation Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x808
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCTL--Pseudo-fault-Generation-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCTL--Pseudo-fault-Generation-Control-Register?lang=en" title="Enables controlled fault generation.">
     CLUSTERRAS_ERR0PFGCTL
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Pseudo-fault Generation Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x810
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCDN--Pseudo-fault-Generation-Countdown-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCDN--Pseudo-fault-Generation-Countdown-Register?lang=en" title="Generates one of the errors enabled in the corresponding ext-CLUSTERRAS_ERR0PFGCTL register.">
     CLUSTERRAS_ERR0PFGCDN
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Pseudo-fault Generation Countdown Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRGSR--Error-Group-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRGSR--Error-Group-Status-Register?lang=en" title="ERRGSR shows the status for the records in the group.">
     CLUSTERRAS_ERRGSR
    </a>
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
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRIIDR--Implementation-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRIIDR--Implementation-Identification-Register?lang=en" title="Defines the implementer of the product.">
     CLUSTERRAS_ERRIIDR
    </a>
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
    0xFA8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVAFF--Device-Affinity-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVAFF--Device-Affinity-Register?lang=en" title="ERRDEVAFF is a copy of part of AArch64-MPIDR_EL1.">
     CLUSTERRAS_ERRDEVAFF
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Affinity Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVARCH--Device-Architecture-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVARCH--Device-Architecture-Register?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRDEVARCH
    </a>
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
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVID--Device-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVID--Device-Configuration-Register?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRDEVID
    </a>
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
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR4--Peripheral-Identification-Register-4?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR4--Peripheral-Identification-Register-4?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 4
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR5--Peripheral-Identification-Register-5?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR5--Peripheral-Identification-Register-5?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 5
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR6--Peripheral-Identification-Register-6?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR6--Peripheral-Identification-Register-6?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR6
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 6
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR7--Peripheral-Identification-Register-7?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR7--Peripheral-Identification-Register-7?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR7
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 7
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR0--Peripheral-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR0--Peripheral-Identification-Register-0?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR1--Peripheral-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR1--Peripheral-Identification-Register-1?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR2--Peripheral-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR2--Peripheral-Identification-Register-2?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR3--Peripheral-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR3--Peripheral-Identification-Register-3?lang=en" title="Provides discovery information about the component.">
     CLUSTERRAS_ERRPIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR0--Component-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR0--Component-Identification-Register-0?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRCIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR1--Component-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR1--Component-Identification-Register-1?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRCIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR2--Component-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR2--Component-Identification-Register-2?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRCIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR3--Component-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR3--Component-Identification-Register-3?lang=en" title="Provides discovery information for the component.">
     CLUSTERRAS_ERRCIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Component Identification Register 3
   </td>
  </tr>
 </tbody>
</table>
