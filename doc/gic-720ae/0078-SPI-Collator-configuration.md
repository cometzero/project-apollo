# SPI Collator configuration

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-configuration>

### SPI Collator configuration

You can configure several options that relate to the operation of an SPI Collator block.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Configurable options for <span>an</span> SPI Collator</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d181258e68" rowspan="1">Feature</th>
<th class="documents-cell-norowborder" colspan="1" id="d181258e71" rowspan="1">Range of options</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of<span> standard</span> SPI wires<span>. The total number of SPIs on all SPI Collators must be ≤1984<span> minus &lt;number of real-time SPIs&gt;</span>.</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>1-1024, in multiples of 32.</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of SPI Collators.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-32</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_INV is a wide vector of one bit for each SPI, indicating whether to invert the interrupt. This parameter is a build-time option.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_SYNC is a wide vector of one bit for each SPI, indicating whether to synchronize the interrupt. This parameter is a build-time option.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_R_INV is a single bit, indicating whether to invert the return path for any <span class="documents-g.signal.name"><span class="documents-keyword">spi_r</span></span> signals where SPI_INV[n] == 1. This parameter is a build-time option. See <a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-wires?lang=en" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-wires?lang=en" title="The SPI Collator wires can be extended to create other functions.">SPI Collator wires</a>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Base address tie-off signal support.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <code class="documents-parmname">SPI_BASE</code> build-time option sets the ID of the starting SPI_ID for this SPI Collator.

            <code class="documents-parmname">SPI_BASE</code> can be set to 0-1983.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span class="documents-g.signal.name"><span class="documents-keyword">spi_base[10:0]</span></span> signal sets the ID of the starting SPI_ID for this SPI Collator.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPI_PROT_RESET_DISABLED is a wide vector of one bit for each SPI, indicating whether to disable the interrupt protection for that SPI. The GIC detects the settings as it exits reset. This parameter is a build-time option.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SPI_PROT_RESET_PERMONLY is a wide vector of one bit for each SPI, indicating whether the interrupt protection detects permanent faults only for that SPI. The GIC detects the settings as it exits reset. If False, the SPI protection detects permanent and transient faults. This parameter is a build-time option.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">True, False</td>
</tr>
</tbody>
</table>



For more information, see the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual.
