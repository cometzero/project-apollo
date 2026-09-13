# Corresponding Collateral

Source: <https://developer.arm.com/documentation/ddi0487/mc/Preface/About-this-Manual/Corresponding-Collateral>

##### Corresponding Collateral

The following packages provide additional information, including machine-readable data, that is aligned to this release:

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
