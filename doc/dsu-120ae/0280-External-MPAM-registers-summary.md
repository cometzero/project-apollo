# External MPAM registers summary

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary>

### External MPAM registers summary

The cluster Memory System Resource Partitioning and Monitoring (MPAM) registers are only accessible from memory-mapped accesses on the utility bus.

The summary table provides an overview of all the cluster MPAM registers that are accessed externally (memory-mapped) from the utility bus of the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> - The cluster MPAM registers are treated as RAZ/WI if the register is marked Reserved.
> - Any address that is not documented is treated as RAZ/WI.
> - The base address for the cluster MPAM registers is 0x010000.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="mrt1733414927871__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAM registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d115394e89" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d115394e91" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d115394e93" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d115394e95" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d115394e97" rowspan="1">
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
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IDR--MPAM-Features-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IDR--MPAM-Features-Identification-Register?lang=en" title="Indicates which memory partitioning and monitoring features are present on this MSC. MPAMF_IDR_s indicates the MPAM features accessed from the Secure MPAM feature page. MPAMF_IDR_ns indicates the MPAM features accessed from the Non-secure MPAM feature page.">
     MPAMF_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Features Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IDR--MPAM-Features-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IDR--MPAM-Features-Identification-Register?lang=en" title="Indicates which memory partitioning and monitoring features are present on this MSC. MPAMF_IDR_s indicates the MPAM features accessed from the Secure MPAM feature page. MPAMF_IDR_ns indicates the MPAM features accessed from the Non-secure MPAM feature page.">
     MPAMF_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Features Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-SIDR--MPAM-Features-Secure-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-SIDR--MPAM-Features-Secure-Identification-Register?lang=en" title="The MPAMF_SIDR is a 32-bit read-only register that indicates the maximum Secure PARTID and Secure PMG on this MSC.">
     MPAMF_SIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Features Secure Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IIDR--MPAM-Implementation-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IIDR--MPAM-Implementation-Identification-Register?lang=en" title="Uniquely identifies the MSC implementation by the combination of implementer, product ID, variant and revision.">
     MPAMF_IIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Implementation Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IIDR--MPAM-Implementation-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IIDR--MPAM-Implementation-Identification-Register?lang=en" title="Uniquely identifies the MSC implementation by the combination of implementer, product ID, variant and revision.">
     MPAMF_IIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Implementation Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-AIDR--MPAM-Architecture-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-AIDR--MPAM-Architecture-Identification-Register?lang=en" title="Identifies the version of the MPAM architecture that this MSC implements.">
     MPAMF_AIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Architecture Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-AIDR--MPAM-Architecture-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-AIDR--MPAM-Architecture-Identification-Register?lang=en" title="Identifies the version of the MPAM architecture that this MSC implements.">
     MPAMF_AIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Architecture Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-CPOR-IDR--MPAM-Features-Cache-Portion-Partitioning-ID-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-CPOR-IDR--MPAM-Features-Cache-Portion-Partitioning-ID-register?lang=en" title="Indicates the number of bits in ext-MPAMCFG_CPBM for this MSC. MPAMF_CPOR_IDR_s indicates the number of bits in the Secure instance of ext-MPAMCFG_CPBM. MPAMF_CPOR_IDR_ns indicates the number of bits in the Non-secure instance of ext-MPAMCFG_CPBM.">
     MPAMF_CPOR_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Features Cache Portion Partitioning ID register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-CPOR-IDR--MPAM-Features-Cache-Portion-Partitioning-ID-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-CPOR-IDR--MPAM-Features-Cache-Portion-Partitioning-ID-register?lang=en" title="Indicates the number of bits in ext-MPAMCFG_CPBM for this MSC. MPAMF_CPOR_IDR_s indicates the number of bits in the Secure instance of ext-MPAMCFG_CPBM. MPAMF_CPOR_IDR_ns indicates the number of bits in the Non-secure instance of ext-MPAMCFG_CPBM.">
     MPAMF_CPOR_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Features Cache Portion Partitioning ID register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-MBW-IDR--MPAM-Memory-Bandwidth-Partitioning-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-MBW-IDR--MPAM-Memory-Bandwidth-Partitioning-Identification-Register?lang=en" title="Indicates which MPAM bandwidth partitioning features are present on this MSC. MPAMF_MBW_IDR_s indicates bandwidth partitioning features accessed from the Secure MPAM feature page. MPAMF_MBW_IDR_ns indicates bandwidth partitioning features accessed from the Non-secure MPAM feature page.">
     MPAMF_MBW_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Memory Bandwidth Partitioning Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-MBW-IDR--MPAM-Memory-Bandwidth-Partitioning-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-MBW-IDR--MPAM-Memory-Bandwidth-Partitioning-Identification-Register?lang=en" title="Indicates which MPAM bandwidth partitioning features are present on this MSC. MPAMF_MBW_IDR_s indicates bandwidth partitioning features accessed from the Secure MPAM feature page. MPAMF_MBW_IDR_ns indicates bandwidth partitioning features accessed from the Non-secure MPAM feature page.">
     MPAMF_MBW_IDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Memory Bandwidth Partitioning Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x00F0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ECR--MPAM-Error-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ECR--MPAM-Error-Control-Register?lang=en" title="MPAMF_ECR is a 32-bit read-write register that controls MPAM error interrupts for this MSC. MPAMF_ECR_s controls Secure MPAM error handling. MPAMF_ECR_ns controls Non-secure MPAM error handling.">
     MPAMF_ECR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Error Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x00F0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ECR--MPAM-Error-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ECR--MPAM-Error-Control-Register?lang=en" title="MPAMF_ECR is a 32-bit read-write register that controls MPAM error interrupts for this MSC. MPAMF_ECR_s controls Secure MPAM error handling. MPAMF_ECR_ns controls Non-secure MPAM error handling.">
     MPAMF_ECR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Error Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x00F8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ESR--MPAM-Error-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ESR--MPAM-Error-Status-Register?lang=en" title="Indicates MPAM error status for this MSC. MPAMF_ESR_s reports Secure MPAM errors. MPAMF_ESR_ns reports Non-secure MPAM errors.">
     MPAMF_ESR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Error Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x00F8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ESR--MPAM-Error-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ESR--MPAM-Error-Status-Register?lang=en" title="Indicates MPAM error status for this MSC. MPAMF_ESR_s reports Secure MPAM errors. MPAMF_ESR_ns reports Non-secure MPAM errors.">
     MPAMF_ESR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Error Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0100
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-PART-SEL--MPAM-Partition-Configuration-Selection-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-PART-SEL--MPAM-Partition-Configuration-Selection-Register?lang=en" title="Selects a partition ID to configure. MPAMCFG_PART_SEL_s selects a Secure PARTID to configure. MPAMCFG_PART_SEL_ns selects a Non-secure PARTID to configure.">
     MPAMCFG_PART_SEL
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Partition Configuration Selection Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0100
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-PART-SEL--MPAM-Partition-Configuration-Selection-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-PART-SEL--MPAM-Partition-Configuration-Selection-Register?lang=en" title="Selects a partition ID to configure. MPAMCFG_PART_SEL_s selects a Secure PARTID to configure. MPAMCFG_PART_SEL_ns selects a Non-secure PARTID to configure.">
     MPAMCFG_PART_SEL
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Partition Configuration Selection Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0500
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-MBW-PROP-ns--MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Non-Secure-PARTIDs?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-MBW-PROP-ns--MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Non-Secure-PARTIDs?lang=en" title="Controls the proportional stride of memory bandwidth that the PARTID selected by MPAMCFG_PART_SEL uses. MPAMCFG_MBW_PROP_ns controls the bandwidth proportional stride for the Secure PARTID selected by the Secure instance of MPAMCFG_PART_SEL. MPAMCFG_MBW_PROP_ns controls the bandwidth proportional stride for the Non-secure PARTID selected by the Non-secure instance of MPAMCFG_PART_SEL.">
     MPAMCFG_MBW_PROP_ns
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Memory Bandwidth Proportional Stride Partition Configuration for Non-Secure PARTIDs
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0500
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-MBW-PROP-s--MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Secure-PARTIDs?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-MBW-PROP-s--MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Secure-PARTIDs?lang=en" title="Controls the proportional stride of memory bandwidth that the PARTID selected by MPAMCFG_PART_SEL uses. MPAMCFG_MBW_PROP_s controls the bandwidth proportional stride for the Secure PARTID selected by the Secure instance of MPAMCFG_PART_SEL. MPAMCFG_MBW_PROP_ns controls the bandwidth proportional stride for the Non-secure PARTID selected by the Non-secure instance of MPAMCFG_PART_SEL.">
     MPAMCFG_MBW_PROP_s
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Memory Bandwidth Proportional Stride Partition Configuration for Secure PARTIDs
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x1000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-ns--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Non-secure-PARTIDs?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-ns--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Non-secure-PARTIDs?lang=en" title="The MPAMCFG_CPBM register is a read-write register that configures the cache portions that a PARTID is allowed to allocate. After setting ext-MPAMCFG_PART_SEL with a PARTID, software (usually a hypervisor) writes to the MPAMCFG_CPBM register to configure which cache portions the PARTID is allowed to allocate.">
     MPAMCFG_CPBM_ns
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    MPAM Cache Portion Bitmap Partition Configuration Register for Non-secure PARTIDs
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x1000
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-s--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Secure-PARTIDs?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-s--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Secure-PARTIDs?lang=en" title="The MPAMCFG_CPBM register is a read-write register that configures the cache portions that a PARTID is allowed to allocate. After setting ext-MPAMCFG_PART_SEL with a PARTID, software (usually a hypervisor) writes to the MPAMCFG_CPBM register to configure which cache portions the PARTID is allowed to allocate.">
     MPAMCFG_CPBM_s
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MPAM Cache Portion Bitmap Partition Configuration Register for Secure PARTIDs
   </td>
  </tr>
 </tbody>
</table>
