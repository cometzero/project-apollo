# Arm® Architecture Reference Manual for A-profile architecture

Source: <https://developer.arm.com/documentation/ddi0487/mc>

## Arm® Architecture Reference Manual for A-profile architecture

<table>
 <tbody>
  <tr>
   <td>
    Document number:
   </td>
   <td>
    ARM DDI 0487
   </td>
  </tr>
  <tr>
   <td>
    Document quality:
   </td>
   <td>
    EAC
   </td>
  </tr>
  <tr>
   <td>
    Document version:
   </td>
   <td>
    M.c
   </td>
  </tr>
  <tr>
   <td>
    Document confidentiality:
   </td>
   <td>
    Non-confidential
   </td>
  </tr>
 </tbody>
</table>

> For a list of the known issues in the latest version of the Arm® Architecture Reference Manual, see [Arm Architecture Reference Manual for A-profile Architecture: Known issues](https://developer.arm.com/documentation/102105/latest/). This known issues document is updated monthly.
>
> This manual is released in PDF format. Download the PDF version using the **Downloads** tab on the left.
>
> This HTML version is currently an early access preview, provided for convenience only. In the event of any differences between the PDF and HTML versions, the PDF version shall be considered the authoritative reference.
>
> [The Architecture Speaks chatbot](https://developer.arm.com/architecture/the-architecture-speaks/) aims to answer questions about the Arm Architecture Reference Manual and point users to sources within it that justify the answers.
>
> The following packages provide additional information, including machine-readable data, that is aligned with this release:

<table>
 <colgroup>
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
 </colgroup>
 <thead>
  <tr>
   <th>
    Name
   </th>
   <th>
    Architecture version
   </th>
   <th>
    Architecture quality
   </th>
   <th>
    Package version
   </th>
   <th>
    Package format
   </th>
   <th>
    Description &amp; Links
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>
    Machine-Readable Descriptions for Features, Registers, and Instructions.
   </td>
   <td>
    up to Armv9.6
   </td>
   <td>
    EAC
   </td>
   <td>
    2026-06
   </td>
   <td>
    XML &amp; HTML
   </td>
   <td>
    <p>
     The following packages provide machine-readable descriptions for Armv8.9-A and Armv9.6-A content:
    </p>
    <ul>
     <li>
      <p>
       <a href="https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-Features/AARCHMRS/AARCHMRS_A_profile-2026-06_mc.tar.gz">
        Features
       </a>
      </p>
     </li>
     <li>
      <p>
       <a href="https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-Arm-Architecture-System-Registers/SysReg/SysReg_xml_A_profile-2026-06_mc.tar.gz">
        Registers
       </a>
      </p>
     </li>
     <li>
      <p>
       <a href="https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-A64-ISA/ISA_A64/ISA_A64_xml_A_profile-2026-06_mc.tar.gz">
        Instructions (A64)
       </a>
      </p>
     </li>
     <li>
      <p>
       <a href="https://developer.arm.com/-/cdn-downloads/permalink/Exploration-Tools-AArch32-ISA/ISA_AArch32/ISA_AArch32_xml_A_profile-2026-06_mc.tar.gz">
        Instructions (A32/T32)
       </a>
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    Architecture Specification Language (ASL) Definition
   </td>
   <td>
    N/A
   </td>
   <td>
    N/A
   </td>
   <td>
    00eac1
   </td>
   <td>
    PDF
   </td>
   <td>
    <p>
     <em>
      Architecture Specification Language
     </em>
     (ASL) is used to specify System registers and instruction descriptions in the
     <em>
      Arm
      <sup>
       &reg;
      </sup>
      Architecture Reference Manual for A-profile architecture
     </em>
     and in the other collateral listed in this table. The following PDFs provide information on ASL:
    </p>
    <ul>
     <li>
      <p>
       ASL Reference (DDI 0626) version 00eac1, the formal language definition for ASL.
      </p>
     </li>
     <li>
      <p>
       ASL Reader&rsquo;s Guide (111069) version A.a, an informal guide to reading ASL code.
      </p>
     </li>
    </ul>
    <p>
     See
     <a href="https://developer.arm.com/Architectures/Architecture%20Specification%20Language">
      Architecture Specification Language
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td>
    Architecture Specification Language (ASL) Ecosystem
   </td>
   <td>
    N/A
   </td>
   <td>
    N/A
   </td>
   <td>
    00eac1
   </td>
   <td>
    Source files &amp; tools
   </td>
   <td>
    <p>
     <em>
      ASLRef
     </em>
     is the reference definition ecosystem for ASL, and is available in a publicly accessible repository that contains all of:
    </p>
    <ul>
     <li>
      <p>
       Source code for Arm&rsquo;s reference implementation of ASL.
      </p>
     </li>
     <li>
      <p>
       Tests that illustrate the ASL language, including those that also appear in ASL Reference (DDI 0626), the formal language definition for ASL.
      </p>
     </li>
     <li>
      <p>
       The source files used to produce ASL Reference (DDI 0626).
      </p>
     </li>
    </ul>
    <p>
     The ASLRef version corresponding to this release is
     <a href="https://github.com/herd/herdtools7/tree/ASLRefEAC1/asllib">
      <em>
       ASLRef EAC1 release
      </em>
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td>
    cat Language Definition
   </td>
   <td>
    N/A
   </td>
   <td>
    N/A
   </td>
   <td>
    Latest
   </td>
   <td>
    PDF
   </td>
   <td>
    <p>
     <em>
      cat
     </em>
     is a domain specific language used to specify the Arm memory model. The following PDF provides information on cat:
    </p>
    <ul>
     <li>
      <a href="http://www0.cs.ucl.ac.uk/staff/j.alglave/papers/syntax-and-semantics-of-cat.pdf">
       Syntax and semantics of the weak consistency model specification language cat
      </a>
      .
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    cat file (Machine-Readable, Executable and Formal Concurrency Model Description).
   </td>
   <td>
    N/A
   </td>
   <td>
    EAC
   </td>
   <td>
    Latest
   </td>
   <td>
    Source files
   </td>
   <td>
    <p>
     <em>
      cat file
     </em>
     (Machine-Readable, Executable, and Formal Concurrency Model Description).
    </p>
    <ul>
     <li>
      <a href="https://github.com/herd/herdtools7/blob/ArmARM-M.c/herd/libdir/aarch64.cat">
       aarch64.cat
      </a>
      contains the definitions and ordering rules that correspond to the section
      <a class="document-topic" document-topic-path="/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model?lang=en#beifddeh" href="/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model?lang=en#beifddeh">
       Ordering requirements defined by the formal concurrency model
      </a>
      .
     </li>
    </ul>
    <p>
     The herdtools7 version corresponding to this release is
     <a href="https://github.com/herd/herdtools7/releases/tag/ArmARM-M.c">
      <em>
       ArmARM-M.c
      </em>
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td>
    Concurrency Model Ecosystem
   </td>
   <td>
    N/A
   </td>
   <td>
    EAC
   </td>
   <td>
    Latest
   </td>
   <td>
    Source files &amp; tools
   </td>
   <td>
    <p>
     <em>
      herdtools7
     </em>
     is a tool suite used to develop, simulate, and test the Arm Concurrency Model, among others. It is available in a publicly accessible repository that contains all of:
    </p>
    <ul>
     <li>
      <p>
       The source code for herd7, the concurrency model simulation tool.
      </p>
     </li>
     <li>
      <p>
       The source code for litmus7, a tool that generates hardware-executable binaries from litmus tests.
      </p>
     </li>
     <li>
      <p>
       The source code for diy7/diyone7, tools that generate litmus tests.
      </p>
     </li>
     <li>
      <p>
       A collection of litmus tests illustrating the ordering requirements defined in the section
       <a class="document-topic" document-topic-path="/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model?lang=en#beifddeh" href="/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model?lang=en#beifddeh">
        Ordering requirements defined by the formal concurrency model
       </a>
       .
      </p>
     </li>
    </ul>
    <p>
     The herdtools7 version corresponding to this release is
     <a href="https://github.com/herd/herdtools7/releases/tag/ArmARM-M.c">
      <em>
       ArmARM-M.c
      </em>
     </a>
     .
    </p>
    <p>
     See also:
    </p>
    <ul>
     <li>
      <a href="https://developer.arm.com/herd7">
       herd7 Tool
      </a>
      .
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>

##### Release information

The following releases of this document have been made.

<table>
 <colgroup>
  <col/>
  <col/>
  <col/>
 </colgroup>
 <thead>
  <tr>
   <th>
    Date
   </th>
   <th>
    Version
   </th>
   <th>
    Changes
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>
    30/Jun/2026
   </td>
   <td>
    M.c
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv9.6 EAC release, incorporating FEAT_HINTE
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    06/Apr/2026
   </td>
   <td>
    M.b
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv9.6 EAC release, incorporating ASL1 and withdrawing FEAT_SEBEP
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    17/Dec/2025
   </td>
   <td>
    M.a.a
   </td>
   <td>
    <ul>
     <li>
      Non-Confidential Armv9.6 EAC release with event links fix. No other content changes.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    01/Dec/2025
   </td>
   <td>
    M.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv9.6 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    30/Apr/2025
   </td>
   <td>
    L.b
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv9.5 EAC release with the MPAM PE content rewritten as rules
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    30/Nov/2024
   </td>
   <td>
    L.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv9.5 EAC release and separation of the RAS System Architecture into Arm&reg; Reliability, Availability, and Serviceability (RAS) System Architecture, for A-profile architecture (ARM IHI 0100)
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    20/Mar/2024
   </td>
   <td>
    K.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.9 and Armv9.4 EAC release, incorporating MPAM and SME
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    21/Apr/2023
   </td>
   <td>
    J.a
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv8.8 and Armv9.3 EAC release incorporating MEC, RAS, and RME
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    19/Aug/2022
   </td>
   <td>
    I.a
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv8.8 and Armv9.3 EAC release incorporating BRBE, ETE, and TRBE
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    04/Feb/2022
   </td>
   <td>
    H.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.8 and Armv9.3 EAC release, incorporating SVE
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    22/Jul/2021
   </td>
   <td>
    G.b
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv8.7 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    22/Jan/2021
   </td>
   <td>
    G.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.7 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    17/Jul/2020
   </td>
   <td>
    F.c
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.6 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    31/Mar/2020
   </td>
   <td>
    F.b
   </td>
   <td>
    <ul>
     <li>
      Non-Confidential Armv8.5 EAC, initial Armv8.6 Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    20/Feb/2020
   </td>
   <td>
    F.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.6 Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    05/Jul/2019
   </td>
   <td>
    E.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.5 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    29/Apr/2019
   </td>
   <td>
    D.b
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential Armv8.4 EAC release incorporating accessibility changes
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    31/Oct/2018
   </td>
   <td>
    D.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.4 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    20/Dec/2017
   </td>
   <td>
    C.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.3 EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    26/Sep/2017
   </td>
   <td>
    B.b
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.2 EAC release, incorporating SPE
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    31/Mar/2017
   </td>
   <td>
    B.a
   </td>
   <td>
    <ul>
     <li>
      Initial Non-Confidential Armv8.1 EAC, v8.2 Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    30/Sep/2016
   </td>
   <td>
    A.k
   </td>
   <td>
    <ul>
     <li>
      Updated Non-Confidential EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    03/Jun/2016
   </td>
   <td>
    A.j
   </td>
   <td>
    <ul>
     <li>
      Non-Confidential EAC release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    28/Jan/2016
   </td>
   <td>
    A.i
   </td>
   <td>
    <ul>
     <li>
      Ninth Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    30/Sep/2015
   </td>
   <td>
    A.h
   </td>
   <td>
    <ul>
     <li>
      Eighth Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    10/Jul/2015
   </td>
   <td>
    A.g
   </td>
   <td>
    <ul>
     <li>
      Seventh Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    25/Mar/2015
   </td>
   <td>
    A.f
   </td>
   <td>
    <ul>
     <li>
      Sixth Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    17/Dec/2014
   </td>
   <td>
    A.e
   </td>
   <td>
    <ul>
     <li>
      Fifth Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    09/Oct/2014
   </td>
   <td>
    A.d
   </td>
   <td>
    <ul>
     <li>
      Fourth Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    18/Jul/2014
   </td>
   <td>
    A.c
   </td>
   <td>
    <ul>
     <li>
      Third Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    24/Dec/2013
   </td>
   <td>
    A.b
   </td>
   <td>
    <ul>
     <li>
      Second Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    04/Sep/2013
   </td>
   <td>
    A.a
   </td>
   <td>
    <ul>
     <li>
      Non-Confidential Beta release
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    12/Jun/2013
   </td>
   <td>
    A.a-2
   </td>
   <td>
    <ul>
     <li>
      Second confidential Beta draft of first issue, limited circulation
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    30/Apr/2013
   </td>
   <td>
    A.a-1
   </td>
   <td>
    <ul>
     <li>
      Confidential Beta draft of first issue, limited circulation
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>

##### Non-Confidential Proprietary Notice

This document is protected by copyright and other related rights and the use or implementation of the information contained in this document may be protected by one or more patents or pending patent applications. No part of this document may be reproduced in any form by any means without the express prior written permission of Arm Limited (“Arm”). **No license, express or implied, by estoppel or otherwise to any intellectual property rights is granted by this document unless specifically stated.**

Your access to the information in this document is conditional upon your acceptance that you will not use or permit others to use the information for the purposes of determining whether the subject matter of this document infringes any third party patents.

The content of this document is informational only. Any solutions presented herein are subject to changing conditions, information, scope, and data.  This document was produced using reasonable efforts based on information available as of the date of issue of this document.  The scope of information in this document may exceed that which Arm is required to provide, and such additional information is merely intended to further assist the recipient and does not represent Arm’s view of the scope of its obligations.  You acknowledge and agree that you possess the necessary expertise in system security and functional safety and that you shall be solely responsible for compliance with all legal, regulatory, safety and security related requirements concerning your products, notwithstanding any information or support that may be provided by Arm herein. In addition, you are responsible for any applications which are used in conjunction with any Arm technology described in this document, and to minimize risks, adequate design and operating safeguards should be provided for by you.

This document may include technical inaccuracies or typographical errors. THIS DOCUMENT IS PROVIDED “AS IS”. ARM PROVIDES NO REPRESENTATIONS AND NO WARRANTIES, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE WITH RESPECT TO THE DOCUMENT. For the avoidance of doubt, Arm makes no representation with respect to, and has undertaken no analysis to identify or understand the scope and content of, any patents, copyrights, trade secrets, trademarks, or other rights.

TO THE EXTENT NOT PROHIBITED BY LAW, IN NO EVENT WILL ARM BE LIABLE FOR ANY DAMAGES, INCLUDING WITHOUT LIMITATION ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, PUNITIVE, OR CONSEQUENTIAL DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT OF ANY USE OF THIS DOCUMENT, EVEN IF ARM HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

Reference by Arm to any third party’s products or services within this document is not an express or implied approval or endorsement of the use thereof.

This document consists solely of commercial items. You shall be responsible for ensuring that any permitted use, duplication, or disclosure of this document complies fully with any relevant export laws and regulations to assure that this document or any portion thereof is not exported, directly or indirectly, in violation of such export laws. Use of the word “partner” in reference to Arm’s customers is not intended to create or refer to any partnership relationship with any other company. Arm may make changes to this document at any time and without notice.

This document may be translated into other languages for convenience, and you agree that if there is any conflict between the English version of this document and any translation, the terms of the English version of this document shall prevail.

The validity, construction and performance of this notice shall be governed by English Law.

The Arm corporate logo and words marked with ® or ™ are registered trademarks or trademarks of Arm Limited (or its affiliates) in the US and/or elsewhere. Please follow Arm’s trademark usage guidelines at <https://www.arm.com/company/policies/trademarks>. All rights reserved. Other brands and names mentioned in this document may be the trademarks of their respective owners.

Copyright © 2013-2026 Arm Limited or its affiliates. All rights reserved.

Arm Limited. Company 02557590 registered in England.

110 Fulbourn Road, Cambridge, England CB1 9NJ.

PRE-20349

8 March 2024

##### Confidentiality Status

This document is Non-Confidential. The right to use, copy and disclose this document may be subject to license restrictions in accordance with the terms of the agreement entered into by Arm and the party that Arm delivered this document to.

##### Product Status

The information in this document is final, that is for a developed product.

The information in this manual is at EAC quality, which means that all features of the specification are described in the manual.

##### Web Address

<https://www.arm.com>
