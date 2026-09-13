# Interface protection

Source: <https://developer.arm.com/documentation/107721/0001/Technical-overview/Interfaces/Interface-protection>

### Interface protection

The DSU-120AE protects all the external interfaces to the cluster, except the non-safety related debug logic.

Interface protection is always present when Dual-Core Lock-Step (DCLS) is enabled, and is not present when DCLS is not configured.

Each signal that interface protection affects, has an associated check signal. This check signal has the identical signal name with "CHK" appended to the end of it. For input signals, the value of the signal (<signal>) is constantly compared to its corresponding CHK signal (<signal>CHK) to ensure that they agree. When these input signals differ, an interface protection fault is raised through the Fault Management Unit (FMU). For output signals, again a check signal is provided, but the comparison between the signals must be done at system-level. The protection mechanism that is specific to the underlying architecture of the relevant external interface determines the valid value of the associated check signal.

The following table describes the mechanisms, and their underlying architectures, that protect each of the supported external interfaces of the DSU-120AE cluster.

<table id="uij1666274954808__table_w3508ab1c11b1b9_w3509ab1c11b1_w3510ab1c11_w3511ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   <span class="documents-keyword">
    DSU-120AE
   </span>
   interfaces and their protection mechanisms
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d44868e87" rowspan="1">
    Interface
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d44868e90" rowspan="1">
    Protection mechanism
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d44868e93" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CHI0, CHI1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Odd-parity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <cite>
     <span>
      <cite>
       <span>
        <a href="https://developer.arm.com/documentation/ihi0022/latest/" target="_blank">
         <span class="documents-keyword">
          AMBA&reg;
         </span>
         AXI Protocol Specification
        </a>
       </span>
      </cite>
     </span>
    </cite>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP (ACE5-Lite)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Odd-parity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <cite>
     <span>
      <cite>
       <span>
        <a href="https://developer.arm.com/documentation/ihi0022/latest/" target="_blank">
         <span class="documents-keyword">
          AMBA&reg;
         </span>
         AXI Protocol Specification
        </a>
       </span>
      </cite>
     </span>
    </cite>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Peripheral port (AXI4)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Odd-parity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <cite>
     <span>
      <cite>
       <span>
        <a href="https://developer.arm.com/documentation/ihi0022/latest/" target="_blank">
         <span class="documents-keyword">
          AMBA&reg;
         </span>
         AXI Protocol Specification
        </a>
       </span>
      </cite>
     </span>
    </cite>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    GIC (AXI4 Stream)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Odd-parity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <cite>
     <span>
      <cite>
       <span>
        <a href="https://developer.arm.com/documentation/ihi0022/latest/" target="_blank">
         <span class="documents-keyword">
          AMBA&reg;
         </span>
         AXI Protocol Specification
        </a>
       </span>
      </cite>
     </span>
    </cite>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    P/Q Channels
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LPI redundancy (inverse polarity)
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <cite>
     <span>
      <a href="https://developer.arm.com/documentation/ihi0068/latest/" target="_blank">
       <span class="documents-keyword">
        AMBA&reg;
       </span>
       Low Power Interface Specification
      </a>
     </span>
    </cite>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Interrupts and events
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Duplicated with inverse polarity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Duplicate signal that is provided as reference on inverse polarity.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Configuration
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Duplicated with inverse polarity
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Duplicate signal that is provided as reference on inverse polarity.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Clocks
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Duplicated with in-phase clock-check
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    In-phase check clock that is provided on
    <span>
     <span class="documents-keyword">
      redundant
     </span>
    </span>
    clock tree. Primary clock is sourced to the primary logic; while the check clock is sourced to the corresponding
    <span>
     <span class="documents-keyword">
      redundant
     </span>
    </span>
    logic.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Resets
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Duplicated with in-phase reset-check
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    In-phase check reset that is provided for all resets. Reset checker with
    <span>
     <span class="documents-keyword">
      redundant
     </span>
    </span>
    checking provides stable resolved resets.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Distributed Time Interface
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Odd-Parity on Status field
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Status field of distributed scaled timer is protected by odd-parity. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    only protects the bits that are in-use in the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    .
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ATB, APB
    <span class="documents-keyword">
     Requester
    </span>
    (APBCD)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Not protected
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Not protected
   </td>
  </tr>
 </tbody>
</table>
