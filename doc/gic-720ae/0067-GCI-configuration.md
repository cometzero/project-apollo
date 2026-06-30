# GCI configuration

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-configuration>

### GCI configuration

You can configure several options that relate to the operation of the GCI.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Configurable options for the <span>GCI</span></span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d166827e69" rowspan="1">Feature</th>
<th class="documents-cell-norowborder" colspan="1" id="d166827e72" rowspan="1">Range of options</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of cores that attach to this <span>GCI</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1-<span>64</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">The number of PPIs for each core. To support more than 16 PPIs, the core must support the GICv3.1 extensions.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">16, 32, 48</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Support for real-time interrupts, including the prioritization of real-time PPI and SGI interrupts.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ECC support for the RAM. See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Reliability--Accessibility--and-Serviceability?lang=en" title="The GIC-720AE uses a range of RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and Scrub, software and bus error reporting.">Reliability, Accessibility, and Serviceability</a> for more information.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Data bus width for the <span>GCI</span> processor AXI5-Stream interface.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">16, 32<span> for a standard <span>GCI</span>.</span><p>32 for a real-time <span>GCI</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">AXI5-Stream data bus width.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">16, 32, 64<span> for a standard <span>GCI</span>.</span><p>64 for a real-time <span>GCI</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GIC Stream bus structure.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Flexible buses and domains</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for CPU interface signals.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Protection for <span class="documents-g.signal.name"><span class="documents-keyword">cpu_active</span></span> signals.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">True, False</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Protection for <span class="documents-g.signal.name"><span class="documents-keyword">ppi</span></span> signals.</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">True, False</td>
</tr>
</tbody>
</table>



For more information, see the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual.
