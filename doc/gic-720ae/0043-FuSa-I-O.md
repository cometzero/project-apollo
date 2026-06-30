# FuSa I/O

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/FuSa-I-O>

### FuSa I/O

The GIC-720AE has extra signals for FuSa fault detection and control.

The following table lists the protection mechanism that GIC-720AE uses for each AMBA® interface or signal type.



<table id="dav1462550727557__tbl.amba_interface_fusa_ports">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>AMBA interface FuSa ports</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d153921e78" rowspan="1">Interface type</th>
<th class="documents-cell-norowborder" colspan="1" id="d153921e81" rowspan="1"><span>Protection mechanism</span></th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>APB5</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>AXI5-Stream</span> interfaces between internal GIC blocks</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity, or CRC, or both</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cross-chip (<span>AXI5-Stream</span> or <span>ACE5-Lite</span>)</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity, or CRC, or both</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>AXI5-Stream</span> external interfaces:

          <ul>
<li>CPU interface</li>
<li>MSI delivery interface</li>
</ul> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity added to all external <span>ACE5-Lite</span> interfaces, including cross-chip when configured to use <span>ACE5-Lite</span> instead of <span>AXI5-Stream</span>.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Q-Channel</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">P-Channel</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">AMBA parity</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Clock input signal</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Duplicated <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signal</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reset input signal</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Duplicated <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signal</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-AMBA input signal</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Odd parity <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signal</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Non-AMBA output signal</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Odd parity <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signal</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Interrupt signal, for SPI and PPI inputs and outputs</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Odd parity <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signals</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">External error interfaces</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Odd parity <span class="documents-g.signal.name"><span class="documents-keyword">*_chk</span></span> signals</td>
</tr>
</tbody>
</table>



See the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual for more information about the signals.
