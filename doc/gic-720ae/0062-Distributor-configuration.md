# Distributor configuration

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-configuration>

### Distributor configuration

You can configure several options that relate to the operation of the Distributor block.



<table id="njp1534667745639__tbl.configurable_options_for_the_distributor">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Configurable options for the Distributor</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d5822e62" rowspan="1">Feature</th>
<th class="documents-cell-norowborder" colspan="1" id="d5822e65" rowspan="1">Range of options</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of chips</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-64</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity level that is used for chip selection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity0 width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-4</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity1 width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity2 width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity3 width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0<span>-4</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of GIC Cluster Interfaces (GCIs)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>0-256</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The <span>GCI</span>s that support real-time interrupts</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI support</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI cache depth, or cache entries ÷ 2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">8, 16, 32, 64, 128, 256, 512</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of LPI cache banks</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1, 2, 4</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of ITS blocks<span> on the chip</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-<span>32</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of credits for transferring LPIs between chips</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of credits for transferring SGIs between chips</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of credits for transferring vSGIs between chips</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICv4.1 support</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICv4.2 support, ﻿non-maskable interrupts (NMIs)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of vPEs supported, 2<sup>&lt;value&gt;</sup></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2-14</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of<span> standard</span> SPI signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">32-<span>1984</span>, in blocks of 32.<span> The 1984 SPIs<span> minus any real-time SPIs,</span> can be spread across 32 SPI Collators. To support 1984 SPIs, the cores must support the GICv3.1 extensions, otherwise the maximum is 960 SPIs.</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of real-time SPI signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">32-960, in blocks of 32.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Number of SPI Collators</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-32</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Remove cores from a preconfigured GIC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Options include:

          <ul>
<li>No support for reducing the number of cores.</li>
<li>Secure software can reduce the number of cores.</li>
<li>The <span class="documents-g.signal.name"><span class="documents-keyword">gicd_pe_off</span></span> tie-off signal can reduce the number of cores.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Local chip addressing</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<ul>
<li>Unified cross-chip addressing. All Distributors use the same addressing scheme.</li>
<li>Local cross-chip addressing. Each Distributor has its own addressing scheme.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RAM I/O support</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Enables I/O to be present and routed to each RAM in a subblock. These I/O have no inherent functionality inside the design. You can use the I/O to control elements within your RAM models.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Remove support for 1 of N SPIs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for the following <span>AXI5-Stream</span> interfaces:

          <ul>
<li><span class="documents-keyword">GICD</span> ↔ <span>GCI</span></li>
<li><span class="documents-keyword">GICD</span> ↔ ITS</li>
<li><span class="documents-keyword">GICD</span> ↔ SPI Collator</li>
<li><span class="documents-keyword">GICD</span> → Wake Request</li>
</ul> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Options include:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             None

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             AMBA parity

           </dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             CRC

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
             AMBA parity and CRC

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for <span class="documents-g.signal.name"><span class="documents-keyword">spi</span></span> signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for <span class="documents-g.signal.name"><span class="documents-keyword">rlt_spi</span></span> signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MBIST protection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Q-Channel protection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">P-Channel protection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>APB5</span> protection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for input tie-off signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for non-AMBA output signals</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Protection for PMU sample and request signals</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">True, False</td>
</tr>
</tbody>
</table>



For more information, see the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual.
