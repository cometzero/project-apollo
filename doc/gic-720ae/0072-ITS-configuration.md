# ITS configuration

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-configuration>

### ITS configuration

You can configure several options that relate to the operation of the ITS block.



<table id="aba1444211890894__tbl.configurable_options_for_the_its">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Configurable options for the ITS</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d55086e62" rowspan="1">Feature</th>
<th class="documents-cell-norowborder" colspan="1" id="d55086e65" rowspan="1">Range of options</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DeviceID width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">3-<span>24</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EventID width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-<span>20</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CollectionID width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2-14</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Inclusion of a bypass port.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MSI-64 support, which controls whether the DeviceID is sent using the <span class="documents-g.signal.name"><span class="documents-keyword">awuser</span></span> signals or on bits[63:32] that are written to GITS_TRANSLATER. See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/ITS/MSI-64?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/ITS/MSI-64?lang=en" title="The MSI-64 Encapsulator can be used to combine the DeviceID into single memory access writes to the GITS_TRANSLATER register in the ITS.">MSI-64</a>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Include an ACE5-Lite subordinate interface for writes to GITS_TRANSLATER (or for bypass).</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>True, </span>False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Include an AXI5-Stream port for transferring <span class="documents-q">“writes”</span> to GITS_TRANSLATER. Other devices can use this port to avoid using address-mapped transactions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of credits for supporting transfer of LPIs using locked translations to the Distributor.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0-4</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of credits for supporting transfer of LPIs using non-locked translations to the Distributor.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-16</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span> subordinate interface address width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">20-<span>52</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span> subordinate interface data width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">64, 128, 256<span>, 512, 1024</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span> subordinate interface read ID width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-32</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span> subordinate interface write ID width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-32</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>ACE5-Lite</span> loop signal width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-8</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>AXI5-Stream</span> data width</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">16, 64</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ECC support for the caches.<p>For more information, see <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" title="The GIC-720AE uses a range of RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and Scrub, software and bus error reporting.">Reliability, Accessibility, and Serviceability</a>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Collection cache depth, or cache entries ÷ 2.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2, 4, 8, 16, 32, 64, 128, 256, 512</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Device cache depth, or cache entries ÷ 2.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2, 4, 8, 16, 32, 64, 128<span>, 256, 512</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Event cache depth, or cache entries ÷ 2. The number of Device and EventID pairs that an ITS caches.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Domain name.<p>For more information, see <a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/Hierarchy?lang=en#qfk1534670745537__fig.gic_top_level_structure_options" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Hierarchy?lang=en#qfk1534670745537__fig.gic_top_level_structure_options">GIC top-level structure options</a>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Any legal domain identifier</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">AMBA parity protection for the optional direct ports.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">AMBA parity protection for all ITS <span>ACE5-Lite</span> interfaces.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">True, False</td>
</tr>
</tbody>
</table>



For more information, see the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual.
