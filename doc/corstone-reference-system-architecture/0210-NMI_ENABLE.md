# NMI_ENABLE

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/NMI-ENABLE>

### NMI\_ENABLE

The NMI\_ENABLE register provides controls to enable or disable the internally or externally generated Non-Maskable Interrupt sources from generating an NMI interrupt on each CPU core. This allows a CPU to take control of all internal NMI interrupt sources or allow all CPUs to see the same NMI interrupts.

### Configurations

This register implementation depends on the configuration of individual fields.

### Attributes

Width
:   32-bit

Power domain
:   The NMI\_ENABLE register resides in the PD\_AON power domain but can also reside in PD\_MGMT power domain when PILEVEL = 2 if its states are saved and restored when entering and then leaving the lower power state, respectively.

Reset
:   This register is reset by
    nWARMRESETAON and its reset value is defined by the configuration options.

### Usage constraints

This register is Secure privileged access only. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   NMI_ENABLE bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d38924e107" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38924e111" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38924e115" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38924e119" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d38924e123" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31:20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000
     </span>
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
     CPU3_EXPNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 3 Externally Sourced NMI Enable. This determines if the input
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU3EXPNMI
      </span>
     </span>
     can raise NMI interrupt on CPU 3:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU3EXPNMIENABLERST
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
     CPU2_EXPNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 2 Externally Sourced NMI Enable. This determines if the input
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU2EXPNMI
      </span>
     </span>
     can raise NMI interrupt on CPU 2:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU2EXPNMIENABLERST
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
     CPU1_EXPNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 Externally Sourced NMI Enable. This determines if the input
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU1EXPNMI
      </span>
     </span>
     can raise NMI interrupt on CPU 1:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU1EXPNMIENABLERST
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
     CPU0_EXPNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 0 Externally Sourced NMI Enable. This determines if the input,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU0EXPNMI
      </span>
     </span>
     can raise NMI interrupt on CPU 0:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU0EXPNMIENABLERST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000
     </span>
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
     CPU3_INTNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 3 Internally Sourced NMI Enable. This determines if the subsystem internally generated NMI interrupt sources can raise NMI interrupt on CPU 3:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU3INTNMIENABLERST
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
     CPU2_INTNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 2 Internally Sourced NMI Enable. This determines if the subsystem internally generated NMI interrupt sources can raise NMI interrupt on CPU 2:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU2INTNMIENABLERST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1_INTNMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 Internally Sourced NMI Enable. This determines if the subsystem internally generated NMI interrupt sources can raise NMI interrupt on CPU 1:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
    <p>
     This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU1INTNMIENABLERST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CPU0_INTNMI_ENABLE
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CPU 0 Internally Sourced NMI Enable. This determines if the subsystem internally generated NMI interrupt sources can raise NMI interrupt on CPU 0:
    </p>
    <ul>
     <li>
      <p>
       HIGH, allowed.
      </p>
     </li>
     <li>
      <p>
       LOW, is masked and not allowed.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CPU0INTNMIENABLERST
    </p>
   </td>
  </tr>
 </tbody>
</table>
