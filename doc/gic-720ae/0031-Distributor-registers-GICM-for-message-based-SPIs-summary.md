# Distributor registers (GICM) for message-based SPIs summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary>

### Distributor registers (GICM) for message-based SPIs summary

The functions for the GIC-720AE message-based SPIs are controlled through the Distributor registers identified with the prefix GICM.

The following table lists the message-based SPI registers in base offset order and provides a reference to the register description that is described in either this document or the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb). The WO registers allow 16-bit accesses.



<table id="aba1429015286126__tbl.gicm_register_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Distributor registers (GICM) for message-based SPIs summary</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e85" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e88" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e91" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e94" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e97" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d59267e101" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d59267e104" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span>- <span class="documents-g.number.hex">0x0004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-TYPER--Message-based-Type-Register?lang=en" title="This register returns information about the number of SPIs that are assigned to the frame.">GICM_TYPER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Type Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0010</span>- <span class="documents-g.number.hex">0x003C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0040</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_SETSPI_NSR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Non-secure SPI Set Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0044</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0048</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_CLRSPI_NSR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Non-secure SPI Clear Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x004C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0050</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_SETSPI_SR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Secure SPI Set Register. Only present when Security support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0054</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0058</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_CLRSPI_SR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">WO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Secure SPI Clear Register. Only present when Security support is included, otherwise Reserved.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x005C</span>- <span class="documents-g.number.hex">0x0FC8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0FCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICM--for-message-based-SPIs-summary/GICM-IIDR--Message-based-Distributor-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the message-based Distributor page.">GICM_IIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x070nn43B</span><p>The <code>nn</code> value depends on the r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Message-based Distributor Implementer Identification Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0FD0</span>- <span class="documents-g.number.hex">0xFFCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 4 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 5 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 6 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 7 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x97</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 0 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 1 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x3B</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 2 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_PIDR3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 3 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 0 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 1 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICM_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 2 register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GICM_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Component ID 3 register</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">No</td>
</tr>
</tbody>
</table>
