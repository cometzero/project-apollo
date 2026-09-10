# Interrupt operation

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Interrupt-operation>

### Interrupt operation

Each channel has its own interrupt to indicate state changes within the channel. There are DMA unit level interrupts that show unit level state changes. The SW can enable, disable, or clear the interrupts.

When both Secure and Non-secure interrupts are used, each interrupt has its handler running in the proper security world. This means that alignment is required when changing the Security state of the channels. The channel interrupt is considered Secure when the channel is configured as Secure.

The channel and unit level interrupts can be seen in the following figure.

Figure 1. DMA Unit level interrupts

![DMA Unit level interrupts](images/0102-Interrupt-operation-img01.svg)

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Non-secure DMA level interrupt signal sources
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d5294e81" rowspan="1">
    <p>
     Interrupt source
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d5294e85" rowspan="1">
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
       chintrstatus0
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Collated channel Non-secure interrupts.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_anychintr
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is a combined Non-secure interrupt, combining the other Non-secure interrupt sources and all the Non-secure channel interrupts when NSEC_CTRL.INTREN_ANYCHINTR is set to
     <code>
      1
     </code>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchidle
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when every Non-secure channel returns to IDLE state from a non-IDLE state. The interrupt is not asserted after reset.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchstopped
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when the last Non-secure channel enters stopped state.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchpaused
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when the last Non-secure channel enters paused state.
    </p>
   </td>
  </tr>
 </tbody>
</table>

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Secure DMA level interrupt signal sources
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d5294e174" rowspan="1">
    <p>
     Interrupt source
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d5294e178" rowspan="1">
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
       chintrstatus0
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Collated channel Secure interrupt flags.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_anychintr
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is a combined Secure interrupt, combining the other Secure interrupt sources and all the Secure channel interrupts when SEC_CTRL.INTREN_ANYCHINTR is set to
     <code>
      1
     </code>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchidle
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when every Secure channel returns to idle state from a non-idle state. The interrupt is not asserted after reset.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchstopped
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when the last Secure channel enters stopped state.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       intr_allchpaused
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     This interrupt is raised when the last Secure channel enters paused state.
    </p>
   </td>
  </tr>
 </tbody>
</table>

The irq\_sec\_viol\_err interrupt signal is provided to notify the Secure entity that a security violation has occurred with register access to the DMA. The irq\_sec\_viol\_err interrupt signal does not exist when SECEXT\_PRESENT is set to `0`.
