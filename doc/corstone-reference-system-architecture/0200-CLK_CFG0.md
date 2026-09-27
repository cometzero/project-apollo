# CLK_CFG0

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG0>

### CLK\_CFG0

The CLK\_CFG0 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.

Each clock control handshake comprises of a conﬁguration request register, that is CLKCFG, and a status register, that is CLKCFGSTATUS that acts as an acknowledgment. After writing to each CLKCFG ﬁeld, the software has to poll the associated CLKCFGSTATUS ﬁeld until the CLKCFGSTATUS is the same as the CLKCFG before doing any other operations. In addition, if it is the first write to the register after boot, we recommend that software polls to check that the targeted CLKCFGSTATUS field matches its associated CLKCFG value before the write occurs. The actual number of bits being implemented in the related CLKCFG and CLKCFGSTATUS signals can be less than that defined below, and is IMPLEMENTATION DEFINED. For any bit that is not implemented, the associated register bit is RAZ/WI.

See also [CLK\_CFG1](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG1?lang=en "The CLK_CFG1 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.") and [CLK\_CFG2](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG2?lang=en "The CLK_CFG2 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.").

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

### Usage constraints

This register is Secure privileged access only. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLK_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d13808e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13808e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13808e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13808e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d13808e145" rowspan="1">
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
     CPU3CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU3CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU3CLKCFGSTATUS
      </span>
     </span>
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
     CPU2CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU2CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU2CLKCFGSTATUS
      </span>
     </span>
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
     CPU1CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU1CLK
      </span>
     </span>
     .
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU1CLKCFGSTATUS
      </span>
     </span>
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
     CPU0CLKCFGSTATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Status value that reports the status of clock control for
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU0CLK
      </span>
     </span>
     .
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU0CLKCFGSTATUS
      </span>
     </span>
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
     CPU3CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU3CLKCFG
      </span>
     </span>
     signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU3CLKCFGRST
      </span>
     </span>
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
     CPU2CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU2CLKCFG
      </span>
     </span>
     signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU2CLKCFGRST
      </span>
     </span>
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
     CPU1CLKCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU1CLKCFG
      </span>
     </span>
     signals.
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU1CLKCFGRST
      </span>
     </span>
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
     CPU0CLKCFG
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration value that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU0CLKCFG
      </span>
     </span>
     signals.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU0CLKCFGRST
      </span>
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
