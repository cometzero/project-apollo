# GCI GIC Stream Protocol interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-GIC-Stream-Protocol-interface>

### GCI GIC Stream Protocol interface

The GIC-720AE uses the GIC Stream Protocol interface to send interrupts to the core and receive notifications when the core activates interrupts.

The GIC Stream Protocol interface has a pair of 16-bit or 32-bit wide AXI5-Stream interfaces, one upstream interface, and one downstream interface. However, if the GCI supports real-time interrupts, then the data width is always 32-bit. At reset, if [GICR\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en "This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.").ECP ==1, then the GCI supports real-time interrupts.

The GIC-720AE uses some extended packets and is designed to work with the Cortex®-R82AE cores. Software can use [GICR\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en "This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.").ECP to disable these extended packets, and then the GCI uses only the packets that the GIC Stream Protocol describes.

The GIC Stream Protocol interface, also referred to as the GIC Stream interface, uses the GIC Stream protocol to pass interrupts and responses to the CPU interface inside each core.

For more information about the protocol that a GCI uses when [GICR\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en "This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.").ECP ==0, see the GIC Stream Protocol interface appendix in the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).



<table id="dji1489161066148__tbl.gic_stream_protocol_signals">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GIC Stream Protocol interface signals</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d167474e149" rowspan="1">Signal</th>
<th class="documents-cell-norowborder" colspan="1" id="d167474e152" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">iri&lt;*&gt;</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The <span class="documents-g.signal.name"><span class="documents-keyword">iri</span></span> prefix identifies the names of the downstream interface signals. These signals are sent by the GIC Stream transmitter. On this interface, the <span>GCI</span> is the transmitter and the CPU interface is the receiver.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">icc&lt;*&gt;</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The <span class="documents-g.signal.name"><span class="documents-keyword">icc</span></span> prefix identifies the names of the upstream interface signals. These signals are sent by the GIC Stream transmitter. On this interface, the CPU interface is the transmitter and the <span>GCI</span> is the receiver.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">iritdest</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The <span>GCI</span> uses this signal to direct packets to one core within the cluster.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">icctid</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The cluster uses this signal to determine which core within the cluster sent a packet.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">iritwakeup</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The <span>GCI</span> uses this signal to indicate that it wants to send a message to a CPU interface in the cluster.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">icctwakeup</span></span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The cluster uses this signal to indicate that it wants to send a message to the <span>GCI</span>.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">iri&lt;*&gt;_chk</span></span>, <span class="documents-g.signal.name"><span class="documents-keyword">icc&lt;*&gt;_chk</span></span></td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">AMBA parity <span class="documents-g.signal.name"><span class="documents-keyword">_chk</span></span> signals</td>
</tr>
</tbody>
</table>



Both the iritdest and icctid signals can support 64 cores that use packed binary encoding, as opposed to one-hot encoding. They can also be divided down using an AXI5-Stream crossbar to support clusters of an arbitrary number of cores from 1-64.

The necessary crossbar is generated as part of the render process, depending on the number of GIC Stream buses that are specified for each GCI.
