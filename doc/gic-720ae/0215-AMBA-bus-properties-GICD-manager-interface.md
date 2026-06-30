# AMBA bus properties, GICD manager interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-manager-interface/AMBA-bus-properties--GICD-manager-interface>

### AMBA bus properties, GICD manager interface

The AMBA® protocols define multiple property types that indicate the capabilities of a device.

The following table lists the Distributor ACE5-Lite manager interface properties.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD ACE5-Lite manager interface properties</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d170771e70" rowspan="1">AMBA property</th>
<th class="documents-nocellnorowborder" colspan="1" id="d170771e73" rowspan="1">Manager interface</th>
<th class="documents-cell-norowborder" colspan="1" id="d170771e76" rowspan="1">ACE5-Lite issue</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Atomic_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Barrier_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cache_Stash_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Check_Type</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>False, Odd_Parity_Byte_All</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CMO_On_Read</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CMO_On_Write</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Coherency_Connection_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DeAllocation_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DVM_v8</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DVM_v8.1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DVM_v8.4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DVM_v9.2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">J</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Exclusive_Accesses</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Not used</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">InvalidateHint_Transaction</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">J</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Loopback_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Max_Transaction_Bytes</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPAM_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Support as defined by the GIC architecture</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MTE_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">NSAccess_Identifiers</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Persist_CMO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Poison</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Prefetch_Transaction</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">QoS_Accept</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read_Data_Chunking</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read_Interleaving_Disabled</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read data interleaving is accepted</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Regular_Transactions_Only</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"> <p>True<span> for GICD manager interface.</span></p> <p>When <code class="documents-parmname">ace_cc</code> == 1, the cross-chip traffic uses this interface, so Regular_Transactions_Only is false.</p> <p>When <code class="documents-parmname">ace_cc</code> == 0 and only memory traffic uses this interface, Regular_Transactions_Only is true.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RME_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True when <code class="documents-parmname">axi_rme_support</code> == 1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">J</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Shareable_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Not used</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Trace_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Unique_ID_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Untranslated_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Wakeup_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Write_Plus_CMO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">WriteEvict_Transaction</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">False</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">F</td>
</tr>
</tbody>
</table>



The manager interface does not issue fixed bursts.
