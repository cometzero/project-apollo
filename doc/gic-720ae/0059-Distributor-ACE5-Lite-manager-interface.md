# Distributor ACE5-Lite manager interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface>

### Distributor ACE5-Lite manager interface

The GICD uses the AMBA® ACE5-Lite manager interface to access all pending, property, and translation tables that are allocated to the GIC. This interface is only present when LPIs are supported, or the GIC has an ACE5-Lite cross-chip interface, or both.

The interface can be configured to be 64-bit, 128-bit, 256-bit, or 512-bit wide.

For multichip configurations, if the GIC has an ACE5-Lite cross-chip interface, then it uses the GICD ACE5-Lite manager interface for cross-chip communications. The system must ensure that traffic from the GICD ACE5-Lite manager interface can reach the cross-chip ACE5-Lite subordinate interfaces of other GICDs in the system, in a free-flowing way without blocking access to memory.

If the cross-chip interface is configured to use ACE5-Lite, then the [GICD\_CCCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register?lang=en "This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.") register provides options to control the ACE5-Lite traffic between chips.

The following table shows the issuing capabilities of the Distributor ACE5-Lite manager interface.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Distributor <span>ACE5-Lite</span> manager interface issuing capabilities</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d180042e125" rowspan="2">Attribute</th>
<th class="documents-cell-norowborder" colspan="2" id="d180042e128" rowspan="1">Capability</th>
</tr>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d180042e134" rowspan="1">Read</th>
<th class="documents-cell-norowborder" colspan="1" id="d180042e137" rowspan="1">Write</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">8-bit reads to Property table (physical or virtual)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">9</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">8-bit read or write to the Pending table (physical or virtual)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Accesses to ITS tables, 64-bit or less</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>sum(<code class="documents-parmname">mpfa_count</code> of all ITSs).</span><p><code class="documents-parmname">mpfa_count</code> is a configuration parameter.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>Number of ITS</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">256-bit read of ITS command queue</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Number of ITS</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">512-bit accesses of Pending tables (physical or virtual)</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">256-bit accesses of Pending tables or Property tables</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Accesses to vPE Configuration table or vPT, 256-bit or less</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">3</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Cross-chip transactions</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Set by the <code class="documents-parmname">ace_cc_credits</code> parameter</td>
</tr>
</tbody>
</table>



Each transaction uses a unique transaction ID.

The following GIC registers are shared between Redistributors, and these registers must be set to the same value by each core that has enabled LPIs:

- GICR\_PROPBASER
- GICR\_PENDBASER, but excluding the ADDRESS field
- GICR\_VPROPBASER and GITS\_BASERn, in configurations that support GICv4.1

The ACE5-Lite manager interface cannot issue barriers or Cache Maintenance Operations (CMOs). However, it can issue shareable, ReadOnce and WriteUnique, transactions if programmed to do so.
