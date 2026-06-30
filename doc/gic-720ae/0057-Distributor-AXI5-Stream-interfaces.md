# Distributor AXI5-Stream interfaces

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-AXI5-Stream-interfaces>

### Distributor AXI5-Stream interfaces

The GIC-720AE uses AXI5-Stream interfaces to communicate between blocks.

These interfaces are:

- Fully credited
- ic<xy>tready. Where xy can be cd, dc, pd, dp, id, di, rd, dr, or dw.

Irrespective of the interconnect that is used, packets must not be reordered between endpoints, for example, between the Distributor and a single Redistributor block. Packets must never be interleaved.

The number of credits, or the outstanding transaction capability, is fixed across all the AXI5-Stream interfaces with the following exceptions:

- The number of outstanding LPIs from each ITS to the GICD can be set using the `number_int_credit` (1-16) and `number_ll_int_credit` (0-4) configuration parameters, for transactions that have been locked in the ITS caches using the [GITS\_OPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en "This register controls cache lock.") register.
- The total number of LPIs and vLPIs transfers that can be outstanding from one chip to another chip, can be set from 1-8 with the `lpi_cc_tokens` configuration parameter.
- The total number of SGIs that can be in transit from one chip to another chip, can be set from 1-8 with the `sgi_cc_tokens` configuration parameter.
- The total number of vSGIs that can be in transit from one chip to another chip, can be set from 1-8 with the `vsgi_cc_tokens` configuration parameter.
- The [GICD\_FCTLR3](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3?lang=en "This register allows software to set some limitations on the cross-chip AXI5-Stream communications. The register is not distributed and acts only on the local chip. The GIC ignores this register for cross-chip ACE5-Lite communications, that is, when GICD_CFGID.ACE_CC == 1.") can set an overall limit on the number of transactions for the cross-chip AXI5-Stream interfaces. If the cross-chip interface is configured to use ACE5-Lite, then software can use [GICD\_CCCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en "This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.") to limit the number of transactions.

For information about AXI5-Stream signals, see the [AMBA® AXI-Stream Protocol Specification](https://developer.arm.com/documentation/ihi0051/b).

The following table lists the AXI5-Stream input interfaces.



<table id="yfi1534667673252__tab.axi_stream_input_interface_descriptions">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>AXI5-Stream input interface descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e207" rowspan="1">Bus</th>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e210" rowspan="1">Destination</th>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e213" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d14119e216" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">ic&lt;xy&gt;tid</span></span></th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICID</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS to Distributor</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">16-bit or 64-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ITS number</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICPD</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Redistributor to Distributor</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>16-bit, 32-bit, or 64-bit</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Redistributor number</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICCD</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI Collator to Distributor</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">16-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">SPI Collator number</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ICRD</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Remote chip to Distributor</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">64-bit</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">0</td>
</tr>
</tbody>
</table>



The following table lists the AXI5-Stream output interfaces.



<table id="yfi1534667673252__tab.axi_stream_output_interface_descriptions">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>AXI5-Stream output interface descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e306" rowspan="1">Bus</th>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e309" rowspan="1">Destination</th>
<th class="documents-nocellnorowborder" colspan="1" id="d14119e312" rowspan="1">Width</th>
<th class="documents-cell-norowborder" colspan="1" id="d14119e315" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">ic&lt;xy&gt;tdest</span></span></th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICDI</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor to ITS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">16-bit or 64-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">ITS number</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICDP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor to Redistributor</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">16-bit, 32-bit, or 64-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Redistributor number</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICDC</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor to SPI Collator</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">16-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">SPI Collator number</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ICDR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Distributor to remote chip</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64-bit</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Programmed value</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ICDW</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Distributor to Wake Request block</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">16-bit</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">-</td>
</tr>
</tbody>
</table>



Each bus has an associated ic<xy>twakeup signal that requests wakeup through the qactive signals when the Distributor, or destination block, is hierarchically clock gated through the Q-Channel. The ic<xy>twakeup input signal must be driven from a cleanly registered version of ic<xy>tvalid, to prevent spurious wake ups from any signal glitches.

For information about the Distributor Q-Channels, see [Distributor Q-Channels](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-Q-Channels?lang=en "There is a single Q-Channel for clock gating the GIC-720AE Distributor. The Q-Channel interface denies access when the Distributor is busy processing interrupts.").
