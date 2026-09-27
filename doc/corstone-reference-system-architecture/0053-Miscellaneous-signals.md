# Miscellaneous signals

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Miscellaneous-signals>

### Miscellaneous signals

The following are other signals available for CRSAS Ma1.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Other miscellaneous top-level signals
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d76762e66" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76762e70" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76762e74" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76762e78" rowspan="1">
    <p>
     Sync to
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76762e82" rowspan="1">
    <p>
     Power domain
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d76762e87" rowspan="1">
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
       LOCKNSVTOR&lt;n&gt;
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Disables writes to the CPU&lt;n&gt; VTOR_NS register. For more information on this register, see
     <cite>
      Arm&reg;v8-M Architecture Reference Manual
     </cite>
     .
    </p>
    <p>
     When HIGH, this input prevents changes to the Non-secure vector table base address register of CPU&lt;n&gt;.
    </p>
    <p>
     If not used, tie to LOW, tying this signal HIGH causes loss of vector table control.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       LOCKNSMPU&lt;n&gt;
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This input disables writes to CPU&lt;n&gt; registers that are associated with the Secure Memory Protection Unit (MPU) region from software or from a debug agent connected to the processor.
    </p>
    <ul>
     <li>
      <p>
       MPU_CTRL
      </p>
     </li>
     <li>
      <p>
       MPU_RNR
      </p>
     </li>
     <li>
      <p>
       MPU_RBAR
      </p>
     </li>
     <li>
      <p>
       MPU_RLAR
      </p>
     </li>
     <li>
      <p>
       MPU_RBAR_An
      </p>
     </li>
     <li>
      <p>
       MPU_RLAR_An
      </p>
     </li>
    </ul>
    <p>
     For more information on these registers, see
     <cite>
      Arm&reg;v8-M Architecture Reference Manual
     </cite>
     .
    </p>
    <p>
     When HIGH, this input prevents changes to the memory regions which have been programmed in the secure MPU. All writes to these registers are ignored.
    </p>
    <p>
     If not used, tie to LOW, tying this signal HIGH causes loss of Secure Memory Protection Unit (MPU) control.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLR
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_MGMT
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     When HIGH, clears the register fields CPUWAIT.CPU&lt;n&gt;WAIT. This allows an external entity to release a processor that is already waited by CPUWAIT to start execution. Once set to &lsquo;1&rsquo;, this signal must be held at &lsquo;1&rsquo; until
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLRRESP
      </span>
     </span>
     is &lsquo;1&rsquo;.
    </p>
    <p>
     Note while this is clocked using
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     this input can optionally be implemented as an asynchronous input.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLRRESP
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_MGMT
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This signal provides a response to the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLR
      </span>
     </span>
     request. When
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLR
      </span>
     </span>
     is &lsquo;1&rsquo; and CPUWAIT.CPU&lt;n&gt;WAIT is &lsquo;0&rsquo;, this signal is set to &lsquo;1&rsquo; until
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;WAITCLR
      </span>
     </span>
     request goes &lsquo;0&rsquo;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSWDRSTREQSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure watchdog reset request status. This output is &lsquo;1&rsquo; when the Non-secure Watchdog is raising a reset request and RESET_MASK.NSWDRSTREQEN is &lsquo;1&rsquo;. Once set to HIGH, it does not return to low unless a reset occurs clearing this status.
    </p>
    <p>
     This output is optional, but must exist when COLDRESET_MODE = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SWDRSTREQSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Secure watchdog reset request status. This output is &lsquo;1&rsquo; when the Secure Watchdog is raising a reset request. Once set to HIGH, it does not return to low unless a reset occurs clearing this status.
    </p>
    <p>
     This output is optional, but must exist when COLDRESET_MODE = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SSWDRSTREQSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Secure Privileged
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     watchdog reset request status. This output is &lsquo;1&rsquo; when the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     Watchdog is raising a reset request. Once set to HIGH, it does not return to low unless a reset occurs clearing this status.
    </p>
    <p>
     This output is optional, but must exist when COLDRESET_MODE = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       RESETREQSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Hardware Reset Request status. This output is set to &lsquo;1&rsquo; if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       RESETREQ
      </span>
     </span>
     input is &lsquo;1&rsquo;. Once set to HIGH, it must not be cleared unless the system is reset.
    </p>
    <p>
     This output is optional, but must exist when COLDRESET_MODE = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SWRSTREQSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Software Reset Request Status. This output is &lsquo;1&rsquo; when SWRESET.SWRESETREQ is set to &lsquo;1&rsquo;. Once set to HIGH, it must not be cleared unless the system is reset while restores the register field to &lsquo;0&rsquo;.
    </p>
    <p>
     This output is optional, but must exist when COLDRESET_MODE = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;LOCKUP
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Processor Lockup Status. There is one bit per Processor. Each bit indicates if the associated CPU&lt;n&gt; has lockup. This signal is an output directly from CPU&lt;n&gt;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;HALTED
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Processor Halted Status. There is one bit per Processor. Each bit indicates if the associated CPU&lt;n&gt; has halted. This signal is an output directly from CPU&lt;n&gt;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;EDBGRQ
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON, PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     External request for CPU&lt;n&gt; to enter halt mode. This signal is an input directly to CPU&lt;n&gt; and also to EWIC&lt;n&gt;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;DBGRESTART
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Request for CPU&lt;n&gt; to perform synchronized exit from halt mode. Forms a handshake with
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;DBGRESTARTED
      </span>
     </span>
     . This signal is an input directly to CPU&lt;n&gt;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;DBGRESTARTED
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_CPU &lt;n&gt;
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Acknowledges
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;DBGRESTART
      </span>
     </span>
     . This signal is an output directly from CPU&lt;n&gt;.
    </p>
   </td>
  </tr>
 </tbody>
</table>
