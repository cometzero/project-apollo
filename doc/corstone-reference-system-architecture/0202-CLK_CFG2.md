# CLK_CFG2

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG2>

### CLK\_CFG2

The CLK\_CFG2 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.

Each clock control handshake comprises of a conﬁguration request register, that is CLKCFG, and a status register, that is CLKCFGSTATUS that acts as an acknowledgment. After writing to each CLKCFG ﬁeld, the software has to poll the associated CLKCFGSTATUS ﬁeld until the CLKCFGSTATUS is the same as the CLKCFG before doing any other operations. In addition, if it is the first write to the register after boot, we recommend that software polls to check that the targeted CLKCFGSTATUS field matches its associated CLKCFG value before the write occurs. The actual number of bits being implemented in the related CLKCFG and CLKCFGSTATUS signals can be less than that defined below, and is IMPLEMENTATION DEFINED. For any bit that is not implemented, the associated register bit is RAZ/WI.

See also [CLK\_CFG0](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG0?lang=en "The CLK_CFG0 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.") and [CLK\_CFG1](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG1?lang=en "The CLK_CFG1 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.").

### Configurations

This register implementation depends on the configuration of individual fields.

### Attributes

Width
:   32-bit

Power domain
:   This register resides in the PD\_AON power domain but can also reside in PD\_MGMT power domain if its states are saved and restored when entering and then leaving the lower power state, respectively.

Reset
:   This register is reset by
    nCOLDRESETAON only.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLK_CFG2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d61611e123" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61611e127" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61611e131" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61611e135" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d61611e139" rowspan="1">
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
     31:28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU3CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU3CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU3CLKCFGSTATUS
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     27:24
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU2CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU2CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU2CLKCFGSTATUS
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     23:20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU1CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU1CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU1CLKCFGSTATUS
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     19:16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU0CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU0CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU0CLKCFGSTATUS
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU3CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives NPU3CLKCFG signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU3CLKCFGRST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11:8
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU2CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives NPU2CLKCFG signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU2CLKCFGRST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU1CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives NPU1CLKCFG signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU1CLKCFGRST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     NPU0CLKCFG
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives NPU0CLKCFG signals. .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NPU0CLKCFGRST
    </p>
   </td>
  </tr>
 </tbody>
</table>
