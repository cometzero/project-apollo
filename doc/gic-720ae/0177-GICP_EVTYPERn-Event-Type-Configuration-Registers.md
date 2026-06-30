# GICP_EVTYPERn, Event Type Configuration Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers>

### GICP\_EVTYPERn, Event Type Configuration Registers

These registers configure which events that event counter `n` counts. The GIC-720AE supports five counters, `n` = 0-4.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICP register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary?lang=en "The GIC-720AE Performance Monitoring Unit functions are controlled through registers that are identified with the prefix GICP.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICP\_EVTYPERn bit assignments

![GICP_EVTYPERn bit assignments](images/0177-GICP_EVTYPERn-Event-Type-Configuration-Registers-img01.svg)



<table id="ntu1469107649205__tbl.gicp_evcntr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICP_EVTYPERn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d63385e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">OVFCAP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">When set to 1, an overflow of counter <code class="documents-option">n</code> triggers a capture if <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CAPR--Counter-Shadow-Value-Capture-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CAPR--Counter-Shadow-Value-Capture-Register?lang=en" title="This register controls the counter shadow value capture mechanism.">GICP_CAPR</a>.CAPTURE is set.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30:18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EVENT_TYPE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Event tracking type:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             Count events

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             MaximumEvent

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>,

            <span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             Reserved

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">EVENT</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Event identifier. See <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.event_field_encoding_with_view" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en#ntu1469107649205__tbl.event_field_encoding_with_view">GICP_EVTYPERn.EVENT field encoding</a>.<p>All events reset to an unknown value. Registers corresponding to unimplemented counters are RES0.</p> </td>
</tr>
</tbody>
</table>



The following table shows the events that the GIC can count. The mask column indicates whether Secure events can be masked when [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").SPF = 1 and [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.").DS == 0.

In the following table, the View filter column is relevant only when the GIC configuration supports multi view, that is, when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1. The view filter is set by [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPVIEW. Software can observe the events only when the view filter matches [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPVIEW or when [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPVIEW == 0.



<table id="ntu1469107649205__tbl.event_field_encoding_with_view">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>GICP_EVTYPERn.EVENT field encoding</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d63385e363" rowspan="1">EventID</th>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e366" rowspan="1">Event</th>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e369" rowspan="1">Description</th>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e372" rowspan="1">Mask</th>
<th class="documents-nocellnorowborder" colspan="1" id="d63385e375" rowspan="1">View filter</th>
<th class="documents-cell-norowborder" colspan="1" id="d63385e379" rowspan="1">Filter</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CLK</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clock cycle</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x1</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CLK_NG</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clock cycle that prevents Q-Channel clock gating.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2</span>-<span class="documents-g.number.hex">0x3</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DN_MSG_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Downstream message to core excluding PPIs.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x5</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DN_SET_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to core SPIs, LPIs, and doorbells.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view, LPI view 1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x6</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DN_SET1OFN_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to core, which is a 1 of N interrupt.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x7</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_MSG_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream message from core.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x9</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_ACT_SPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream activate.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xA</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_REL_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream release.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_ACT_LPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream activate of LPI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_SET_COMP_PHY</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">A set followed by an activate. This event counts the set and then decrements on release.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view, LPI view 1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xD</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_DEACT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream deactivate. SPIs only.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Deactivate packet has either Group 0 or Secure Group 1 set.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xE</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_ACT_DBL</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream activate of doorbell.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP(vPE)/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x10</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_BRD</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Broadcast SGI messages. Target = source.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x11</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_TAR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Targeted SGI messages. Target = source.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x12</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_ALL</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">All SGI messages. Target = source.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x13</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_ACC</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Accepted SGI. Target = source.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x14</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_BRD_CC_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Broadcast SGI message from cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x15</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_TAR_CC_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Targeted SGI message from cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x16</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_TAR_CC_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Targeted SGI sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x17</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_CC_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Any SGI being sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x18</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SGI_CC_OUT_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response from any outgoing SGI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when the Generate SGI packet has the NS bit set to 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x20</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_NLL_LPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Incoming LPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x21</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_LL_LPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Incoming low latency LPI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x22</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_LPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Incoming LPI (or low latency).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x23</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_LPI_CMD</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Incoming LPI command</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x24</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_DID_MISS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of DeviceID cache misses.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x25</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_VID_MISS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of EventID cache misses.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x26</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_COL_MISS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of Collection cache misses.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x27</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_LAT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Latency of the ITS transaction.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x28</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS_MPFA</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of free slots during translation</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range/ITS</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x29</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CC_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2A</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CMD_CC_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI command sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CC_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI coming in from cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CMD_CC_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI command coming in from cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CC_OUT_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response to LPI sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x2E</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_CMD_CC_OUT_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response to LPI command sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x30</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_OWN_STORED</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI stored in own location. Prevents clock gating and Q-Channel clock gating.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x31</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_OOL_STORED</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI stored out of location. Prevents clock gating and Q-Channel clock gating.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x32</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_HIT_EN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI property read cache hit enabled. Uses the filter from counter 0 only.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x33</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_HIT_DIS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI property read cache hit disabled. Uses the filter from counter 0 only.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x34</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_HIT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI property read cache hit. Uses the filter from counter 0 only.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x35</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_MATCH</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI coalesced. Uses the filter from counter 0 only.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x36</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_FAS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of slots free on new LPI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x37</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_PROP_EN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enabled LPI property fetch. Uses the filter from counter 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x38</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_PROP_DIS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disabled LPI property fetch. Uses the filter from counter 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x39</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_PROP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI property fetch. Uses the filter from counter 0.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x50</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_COL_MSG</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">New message from SPI Collator.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x51</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_ENABLED</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI enabled (new SPI or register access if pending).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x52</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_DISABLED</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI disabled (new SPI that is disabled or register access if pending).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x53</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_PENDING_SET</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">New SPI pending valid.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x54</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_PENDING_CLR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI pending bit cleared.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x55</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_MATCH</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Collated edge-based SPI. Excludes collation in the SPI Collator.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x57</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_CC_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI from remote chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x58</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_CC_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI sent to remote chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x59</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_CC_OUT_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response to SPI sent to remote chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x5A</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_CC_DEACT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI deactivate message sent.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ID range/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x5B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_CC_DEACT_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Response to deactivate sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The event is masked when it corresponds to an interrupt that is either Group 0 or Secure Group 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x60</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_IN_EN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enabled interrupt written to Pending table.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x61</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_IN_DIS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disabled interrupt written to Pending table.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x62</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_PRI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Priority of interrupt written to Pending table.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x63</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_IN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt written to Pending table.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x64</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_MATCH</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt already set in Pending table.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x65</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_OUT_EN</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enabled interrupt taken out of Pending table (also covered PT_MATCH when enabled).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x66</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_OUT_DIS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disabled interrupt taken out of Pending table (also covered PT_MATCH when disabled).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x67</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PT_OUT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt taken out of Pending table (also covered PT_MATCH).</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x70</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI_CC</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI sent cross-chip.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x71</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI_CC_RESP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI cross-chip response.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x72</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI_IN_RAM</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI stored in RAM.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x73</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VLPI_BUFF_FILL</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of buffers used on vLPI arriving.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x74</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VLPI_REJECT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vLPI sent cross-chip being rejected.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x75</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI_REJECT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vSGI sent cross-chip being rejected.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x76</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VCMD_REJECT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual command sent cross-chip being rejected.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP/Chip</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x78</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RES_START</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Residency change start.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x79</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RES_COMP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Residency change end.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x80</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ACC</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Counter(<code class="documents-option">n</code> − 1) − counter(<code class="documents-option">n</code> − 2) every cycle. Prevents clock gating and Q-Channel clock gating.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x81</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">OFLOW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Overflow of counter <code class="documents-option">n</code> − 1. Overflow counters cannot count overflows of the counters that are using the OFLOW event.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x88</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DN_SET_VIRT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual set command.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP(PHY)/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x89</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_REL_VIRT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual release</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP(PHY)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8A</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_ACT_VLPI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Activate of vLPI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP(PHY)/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_ACT_VSGI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Activate of vSGI.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">TargetVP(PHY)/ID range</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x8C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">UP_SET_COMP_VIRT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">A set followed by an activate. This event counts the set and then decrements on release.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unmasked</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target(PHY)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x90</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RLT_SPI_SET</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Set to real-time SPIs.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used. For example, if using counter 4, then the GIC uses GICP_FR3 and ignores GICP_FR4.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked by group.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target/ID.<p>To filter this event, you must precisely match the target or ID, otherwise the behavior is unpredictable.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x91</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RLT_SPI_ACT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream activate for real-time SPIs.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked by group.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target/ID.<p>To filter this event, you must precisely match the target or ID, otherwise the behavior is unpredictable.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x92</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RLT_SPI_REL</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream release for real-time SPIs.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked by group.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target/ID.<p>To filter this event, you must precisely match the target or ID, otherwise the behavior is unpredictable.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x93</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RLT_SPI_DEACT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Upstream deactivate for real-time SPIs.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Not reported if filter is set.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RD view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target/ID.<p>To filter this event, you must precisely match the target or ID, otherwise the behavior is unpredictable.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x94</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RLT_SPI_PEND_CNT</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Pending real-time SPIs count at every cycle. Selecting this event prevents the Q-Channel from accepting low-power requests.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Masked by group.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target/ID range</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x95</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RLT_SPI_ACT_CNT</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Activate count for real-time SPIs at every cycle. Selecting this event prevents the Q-Channel from accepting low-power requests.<p>This event always uses the filter in <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en" title="These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.">GICP_FR3</a>, irrespective of the counter that is used.</p> </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Masked by group.</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SPI view</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Target/ID range</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICPNS == 0, then GICP\_EVTYPERn is accessible only by Secure accesses.
