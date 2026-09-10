# Revisions

Source: <https://developer.arm.com/documentation/102482/0000/Revisions>

### Revisions

This appendix describes the technical changes between released issues of this document.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Issue 0000-01
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d33316e68" rowspan="1">
    <p>
     Change
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d33316e72" rowspan="1">
    <p>
     Location
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     First release
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     -
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
   Differences between issue 0000-01 and 0000-02
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d33316e109" rowspan="1">
    <p>
     Change
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d33316e113" rowspan="1">
    <p>
     Location
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Master has been changed to manager and slave to subordinate
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Throughout the document
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AXI bandwidth utilization
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization?lang=en" href="/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization?lang=en" title="This section provides a definition of terms used and optimization requirements.">
      AXI bandwidth utilization
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cross Trigger Interface
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/Control-and-status-interface/Cross-Trigger-Interface?lang=en" href="/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Cross-Trigger-Interface?lang=en" title="The DMAC provides a Cross Trigger Interface (CTI) that allows pausing and resuming all channels at once. The CTI is required in a system where a processor is halted for debug purposes and the debugger must save the actual memory contents so the DMAC can also be paused to avoid corrupting the current state of the system.">
      Cross Trigger Interface
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Command execution status reporting
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-operation/DMA-Channel-lifecycle/Command-execution-status-reporting?lang=en" href="/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle/Command-execution-status-reporting?lang=en" title="The software can read the contents of X, Y size, and address registers after the DMA command execution.">
      Command execution status reporting
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Added Warm reset power state
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-power-P-Channel?lang=en" href="/documentation/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-power-P-Channel?lang=en" title="The power P-Channel interface is used to request power quiescence from the DMAC. A power controller drives the request while the DMAC either accepts or denies the request based on its current internal state. The DMAC can also request power for an activity over the pactive signal.">
      LPI power P-Channel
     </a>
     and
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management/Power-P-Channel?lang=en" href="/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management/Power-P-Channel?lang=en" title="The DMA-350 is using one full LPI P-Channel for power management. The purpose of this feature is to enable lower power states (removing power) to reduce power consumption while not in active use. The power P-Channel is used to control the power state of the DMAC logic.">
      Power P-Channel
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Content in Programming considerations
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Programming-considerations?lang=en" href="/documentation/102482/0000/Programmers-model/Programming-considerations?lang=en" title="The DMA channels can be configured to transfer several data elements from one location to another. There are multiple settings for every command that define the way the DMAC sends the transfers to the bus interface.">
      Programming considerations
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Differences between issue 0000-02 and 0000-03
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d33316e241" rowspan="1">
    <p>
     Change
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d33316e245" rowspan="1">
    <p>
     Location
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Name of relevant configuration added
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMA-350-overview/Configurable-options?lang=en" href="/documentation/102482/0000/DMA-350-overview/Configurable-options?lang=en" title="The DMA-350 can be configured with the following options to meet specific design requirements:">
      Configurable options
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Rewrite of section
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization?lang=en" href="/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization?lang=en" title="This section provides a definition of terms used and optimization requirements.">
      AXI bandwidth utilization
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Addition of sections
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-start-address?lang=en" href="/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-start-address?lang=en" title="Assuming the following settings:">
      Example of an unaligned start address
     </a>
     and
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-start-address?lang=en" href="/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-start-address?lang=en" title="Assuming the following settings:">
      Example of an unaligned start address
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Change to Non-secure and Secure DMA level interrupt signal sources
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-operation/Interrupt-operation?lang=en" href="/documentation/102482/0000/DMAC-operation/Interrupt-operation?lang=en" title="Each channel has its own interrupt to indicate state changes within the channel. There are DMA unit level interrupts that show unit level state changes. The SW can enable, disable, or clear the interrupts.">
      Interrupt operation
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Additional information added and change to figure
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Programming-considerations?lang=en" href="/documentation/102482/0000/Programmers-model/Programming-considerations?lang=en" title="The DMA channels can be configured to transfer several data elements from one location to another. There are multiple settings for every command that define the way the DMAC sends the transfers to the bus interface.">
      Programming considerations
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Memory map table updated
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Memory-map?lang=en" href="/documentation/102482/0000/Programmers-model/Memory-map?lang=en" title="The memory map includes the maximum number of implemented blocks.">
      Memory map
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Description of channels rewritten
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CHSEC0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CHSEC0?lang=en" title="The Secure Configuration Channel Security Mapping register is used to define the security attribute of each channel from Channel 0 to NUM_CHANNELS - 1.">
      SCFG_CHSEC0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Description of channels rewritten
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHINTRSTATUS0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHINTRSTATUS0?lang=en" title="The Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Secure channel from Channel 0 to NUM_CHANNELS - 1.">
      SEC_CHINTRSTATUS0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Description of channels rewritten
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHINTRSTATUS0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHINTRSTATUS0?lang=en" title="The Non-Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Non-secure channel from Channel 0 to NUM_CHANNELS - 1.">
      NSEC_CHINTRSTATUS0
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
   </span>
   Differences between issue 0000-03 and 0000-04
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d33316e423" rowspan="1">
    <p>
     Change
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d33316e427" rowspan="1">
    <p>
     Location
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Removed typo
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-Trigger-Interface?lang=en" href="/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-Trigger-Interface?lang=en" title="The stream interface usage has some restrictions on the trigger input interface as the block-based transfers might behave improperly when converting them to stream output transfers.">
      Interworking with Trigger Interface
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
