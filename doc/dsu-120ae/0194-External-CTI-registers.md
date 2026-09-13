# External CTI registers

Source: <https://developer.arm.com/documentation/107721/0001/Debug/External-CTI-registers>

### External CTI registers

The cluster Cross Trigger Interface (CTI) registers and core CTI registers are only accessible using memory-mapped accesses over the Debug APB interface.

The summary table provides an overview of all the cluster CTI registers and core CTI registers. For more information about a register, click on the register name in the table.

> ### Note
>
> - Registers that differ in descriptions and values, for cluster and core, are indicated in the Identical CTI core column. These registers are the CTIPIDR0-4 registers, and the CTIDEVAFF0-1 registers.
> - The cluster CTI registers are treated as RAZ/WI if the register is marked Reserved.
> - Any address that is not documented is treated as RAZ/WI.
> - The cluster CTI part number is 0x4EA.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="sda1660577308224__d108e26">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTI registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d69183e104" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69183e106" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69183e108" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69183e110" rowspan="1">
    Width
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69183e112" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d69183e114" rowspan="1">
    Identical core CTI
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICONTROL--CTI-Control-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICONTROL--CTI-Control-register?lang=en" title="Controls whether the CTI is enabled.">
     CTICONTROL
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Control register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINTACK--CTI-Output-Trigger-Acknowledge-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINTACK--CTI-Output-Trigger-Acknowledge-register?lang=en" title="Can be used to deactivate the output triggers.">
     CTIINTACK
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Output Trigger Acknowledge register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPSET--CTI-Application-Trigger-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPSET--CTI-Application-Trigger-Set-register?lang=en" title="Sets bits of the Application Trigger register.">
     CTIAPPSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Application Trigger Set register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPCLEAR--CTI-Application-Trigger-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPCLEAR--CTI-Application-Trigger-Clear-register?lang=en" title="Clears bits of the Application Trigger register.">
     CTIAPPCLEAR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Application Trigger Clear register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x01C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPPULSE--CTI-Application-Pulse-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPPULSE--CTI-Application-Pulse-register?lang=en" title="Causes event pulses to be generated on ECT channels.">
     CTIAPPPULSE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Application Pulse register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN0--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN0--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x24
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN1--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN1--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN2--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN2--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x2C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN3--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN3--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x30
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN4--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN4--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x34
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN5--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN5--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x38
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN6--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN6--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN6
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x3C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN7--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN7--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN7
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x40
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN8--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN8--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN8
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x44
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN9--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN9--CTI-Input-Trigger-to-Output-Channel-Enable-registers?lang=en" title="Enables the signaling of an event on output channels when input trigger event n is received by the CTI.">
     CTIINEN9
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Trigger to Output Channel Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xA0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN0--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN0--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xA4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN1--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN1--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xA8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN2--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN2--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xAC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN3--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN3--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xB0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN4--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN4--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xB4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN5--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN5--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xB8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN6--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN6--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN6
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN7--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN7--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN7
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN8--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN8--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN8
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN9--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN9--CTI-Input-Channel-to-Output-Trigger-Enable-registers?lang=en" title="Defines which input channels generate output trigger n.">
     CTIOUTEN9
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Input Channel to Output Trigger Enable registers
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x130
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTITRIGINSTATUS--CTI-Trigger-In-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTITRIGINSTATUS--CTI-Trigger-In-Status-register?lang=en" title="Provides the status of the trigger inputs.">
     CTITRIGINSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Trigger In Status register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x134
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTITRIGOUTSTATUS--CTI-Trigger-Out-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTITRIGOUTSTATUS--CTI-Trigger-Out-Status-register?lang=en" title="Provides the raw status of the trigger outputs after processing by trigger interface logic.">
     CTITRIGOUTSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Trigger Out Status register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x138
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICHINSTATUS--CTI-Channel-In-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICHINSTATUS--CTI-Channel-In-Status-register?lang=en" title="Provides the raw status of the ECT channel inputs to the CTI.">
     CTICHINSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Channel In Status register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x13C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICHOUTSTATUS--CTI-Channel-Out-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICHOUTSTATUS--CTI-Channel-Out-Status-register?lang=en" title="Provides the status of the ECT channel outputs from the CTI.">
     CTICHOUTSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Channel Out Status register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x140
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIGATE--CTI-Channel-Gate-Enable-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIGATE--CTI-Channel-Gate-Enable-register?lang=en" title="Determines whether events on channels propagate through the CTM to other ECT components, or from the CTM into the CTI.">
     CTIGATE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Channel Gate Enable register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x150
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVCTL--CTI-Device-Control-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVCTL--CTI-Device-Control-register?lang=en" title="Provides target-specific device controls">
     CTIDEVCTL
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device Control register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFA0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMSET--CTI-Claim-Tag-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMSET--CTI-Claim-Tag-Set-register?lang=en" title="Used by software to set CLAIM bits to 1.">
     CTICLAIMSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Claim Tag Set register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFA4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en" title="Used by software to read the values of the CLAIM bits, and to clear these bits to 0.">
     CTICLAIMCLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Claim Tag Clear register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFA8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVAFF0--CTI-Device-Affinity-register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVAFF0--CTI-Device-Affinity-register-0?lang=en" title="Copy of the low half of the PE AArch64-MPIDR_EL1 register that allows a debugger to determine which PE in a multiprocessor system the CTI component relates to.">
     CTIDEVAFF0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device Affinity register 0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No, see individual register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFAC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVAFF1--CTI-Device-Affinity-register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVAFF1--CTI-Device-Affinity-register-1?lang=en" title="Copy of the high half of the PE AArch64-MPIDR_EL1 register that allows a debugger to determine which PE in a multiprocessor system the CTI component relates to.">
     CTIDEVAFF1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device Affinity register 1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No, see individual register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFB8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAUTHSTATUS--CTI-Authentication-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAUTHSTATUS--CTI-Authentication-Status-register?lang=en" title="Provides information about the state of the authentication interface for CTI.">
     CTIAUTHSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Authentication Status register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVARCH--CTI-Device-Architecture-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVARCH--CTI-Device-Architecture-register?lang=en" title="Identifies the programmers' model architecture of the CTI component.">
     CTIDEVARCH
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device Architecture register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID2--CTI-Device-ID-register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID2--CTI-Device-ID-register-2?lang=en" title="Reserved for future information about the CTI component to the debugger.">
     CTIDEVID2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device ID register 2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID1--CTI-Device-ID-register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID1--CTI-Device-ID-register-1?lang=en" title="Reserved for future information about the CTI component to the debugger.">
     CTIDEVID1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device ID register 1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID--CTI-Device-ID-register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID--CTI-Device-ID-register-0?lang=en" title="Describes the CTI component to the debugger.">
     CTIDEVID
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device ID register 0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVTYPE--CTI-Device-Type-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVTYPE--CTI-Device-Type-register?lang=en" title="Indicates to a debugger that this component is part of a PEs cross-trigger interface.">
     CTIDEVTYPE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Device Type register
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR4--CTI-Peripheral-Identification-Register-4?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR4--CTI-Peripheral-Identification-Register-4?lang=en" title="Provides information to identify a CTI component.">
     CTIPIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Peripheral Identification Register 4
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Might be different between core and cluster CTI, see register description.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR0--CTI-Peripheral-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR0--CTI-Peripheral-Identification-Register-0?lang=en" title="Provides information to identify a CTI component.">
     CTIPIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Peripheral Identification Register 0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Might be different between core and cluster CTI, see register description.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR1--CTI-Peripheral-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR1--CTI-Peripheral-Identification-Register-1?lang=en" title="Provides information to identify a CTI component.">
     CTIPIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Peripheral Identification Register 1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Might be different between core and cluster CTI, see register description.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR2--CTI-Peripheral-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR2--CTI-Peripheral-Identification-Register-2?lang=en" title="Provides information to identify a CTI component.">
     CTIPIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Peripheral Identification Register 2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Might be different between core and cluster CTI, see register description.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR3--CTI-Peripheral-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR3--CTI-Peripheral-Identification-Register-3?lang=en" title="Provides information to identify a CTI component.">
     CTIPIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Peripheral Identification Register 3
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Might be different between core and cluster CTI, see register description.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR0--CTI-Component-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR0--CTI-Component-Identification-Register-0?lang=en" title="Provides information to identify a CTI component.">
     CTICIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Component Identification Register 0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR1--CTI-Component-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR1--CTI-Component-Identification-Register-1?lang=en" title="Provides information to identify a CTI component.">
     CTICIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Component Identification Register 1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR2--CTI-Component-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR2--CTI-Component-Identification-Register-2?lang=en" title="Provides information to identify a CTI component.">
     CTICIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI Component Identification Register 2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR3--CTI-Component-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICIDR3--CTI-Component-Identification-Register-3?lang=en" title="Provides information to identify a CTI component.">
     CTICIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI Component Identification Register 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
 </tbody>
</table>
