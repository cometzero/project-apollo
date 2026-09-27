# Clock configuration interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Clock-configuration-interface>

### Clock configuration interface

CRSAS Ma1 provides a set of control and status signals for some of the clocks to configure generators or dividers that might exist in the expansion system.

Each set of control and status signal and even individual bits of this interface can be unimplemented or disabled. This, and how they are used are IMPLEMENTATION DEFINED, but if a set exists, then the default value of each signal at reset must be set to a value to allow the input clock to run at a default clock rate to allow the system to at least boot without software configurating these sets of registers. The reset value can be configured.

All signals in this interface reside in the PD\_AON power domain, are synchronous to AONCLK and are on the nCOLDRESETAON reset domain.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Clock configuration interface signals
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d128221e73" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128221e77" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128221e81" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d128221e85" rowspan="1">
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
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLKCFG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These control outputs provide a set of four-bit outputs that allows the system to configure an external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
     . These output signals are driven by the register fields CLK_CFG0.CPU&lt;n&gt;CLKCFG.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLKCFGSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These sets of four-bit input signals are used to read the status of any external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
     . The values on this interface can be read by the register fields CLK_CFG0.CPU&lt;n&gt;CLKCFGSTATUS.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLKCFG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This control output provides four-bit outputs that allows the system to configure an external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     . This output is driven by the register fields CLK_CFG1.SYSCLKCFG.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLKCFGSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This four-bit input signal is used to read the status of any external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     . The values on this interface can be read by the register fields CLK_CFG1.SYSCLKCFGSTATUS.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLKCFG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This control output provides a four-bit output that allows the system to configure an external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLK
      </span>
     </span>
     . This output is driven by the register fields CLK_CFG1.AONCLKCFG.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLKCFGSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This four-bit status output is used to read the status of any external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLK
      </span>
     </span>
     . The values on this interface can be read by the register fields CLK_CFG1.AONCLKCFGSTATUS.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU&lt;m&gt;CLKCFG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These control outputs provide a set of four-bit outputs that allows the system to configure an external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU&lt;m&gt;CLK
      </span>
     </span>
     . These outputs are driven by the register fields CLK_CFG2.NPU&lt;m&gt;CLKCFG.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU&lt;m&gt;CLKCFGSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     These sets of four-bit status inputs are used to read the status of any external clock generation logic that drives
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU&lt;m&gt;CLK
      </span>
     </span>
     . The values on this interface can be read by the register fields CLK_CFG2.NPU&lt;m&gt;CLKCFGSTATUS.
    </p>
    <p>
     Any unimplemented bits result in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
 </tbody>
</table>
