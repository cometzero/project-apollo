# AMBA bus properties, GICD and CC subordinate interfaces

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-subordinate-interface/AMBA-bus-properties--GICD-and-CC-subordinate-interfaces>

### AMBA bus properties, GICD and CC subordinate interfaces

The AMBA® protocols define multiple property types that indicate the capabilities of a device.

The cross-chip (CC) subordinate interface only accepts INCR or aligned WRAP transactions. Also, 64-bit atomicity is required between the CC manager interface and the destination CC subordinate interface. Therefore, for any split transactions, the address must update to correctly align the data.

The following table lists the ACE5-Lite properties for the GICD subordinate interface and the cross-chip subordinate interface.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD <span>and cross-chip </span>ACE5-Lite subordinate interface properties</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d1081e79" rowspan="1">AMBA property</th>
<th class="documents-nocellnorowborder" colspan="1" id="d1081e82" rowspan="1">Subordinate interface</th>
<th class="documents-cell-norowborder" colspan="1" id="d1081e85" rowspan="1">ACE5-Lite issue</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Atomic_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Barrier_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cache_Stash_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Basic when <code class="documents-parmname">axi_cache_stashing_support</code> == 0.<p>Full cache stash support, including dataless, when <code class="documents-parmname">axi_cache_stashing_support</code> == 1.</p> <p>Ignore and respond legally.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Check_Type</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>False, Odd_Parity_Byte_All</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CMO_On_Read</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">InvalidateHint_Transaction</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">J</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Loopback_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Max_Transaction_Bytes</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">4096</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPAM_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MTE_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">H</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">NSAccess_Identifiers</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">False</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Persist_CMO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Ignore and respond legally</td>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">No read data interleaving</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">G</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RME_Support</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True when <code class="documents-parmname">axi_rme_support</code> == 1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">J</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Shareable_Transactions</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">F</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Trace_Signals</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">True</td>
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
<td class="documents-row-nocellborder" colspan="1" rowspan="1">True</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">F</td>
</tr>
</tbody>
</table>
