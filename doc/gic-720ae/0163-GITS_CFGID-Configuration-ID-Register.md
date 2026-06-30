# GITS_CFGID, Configuration ID Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-CFGID--Configuration-ID-Register>

### GITS\_CFGID, Configuration ID Register

This register returns information about the configuration of the ITS block such as its ID number.

### Configurations

This register is available in all configurations that have one or more ITS blocks.

### Attributes

Width
:   64-bit

Functional group
:   See
    [ITS control register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en "The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GITS\_CFGID bit assignments

![GITS_CFGID bit assignments](images/0163-GITS_CFGID-Configuration-ID-Register-img01.svg)



<table id="zvv1469453171183__tbl.gits_cfgid">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_CFGID bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d41492e138" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d41492e141" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d41492e144" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:40]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[39:36]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Low_Latency_LPI_Credit_Count</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of low-latency LPI credits. The <code class="documents-parmname">number_ll_int_credit</code> configuration parameter sets the value of this field.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[35:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">vPE_Bits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of bits that are used for vPE IDs.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Event_Cache_Index_Bits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of bits that are used to index the Event cache.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Device_Cache_Index_Bits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of bits that are used to index the Device cache.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Collection_Cache_Index_Bits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of bits that are used to index the Collection cache.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Cache_ECC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Translation caching has ECC protection.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Low_Latency_Support</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Lock translations in cache support.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MSI_64</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">MSI-64 Encapsulator support. The <code class="documents-parmname">msi_64</code> configuration parameter sets the value of this bit.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Target_Bits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of bits supported for targets.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LPI_Credit_Count</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Number of LPI credits − 1. The <code class="documents-parmname">number_int_credit</code> configuration parameter minus 1, sets the value of this field.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ITS_Number</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the ITS block ID.<span> The <span class="documents-g.signal.name"><span class="documents-keyword">its_id[7:0]</span></span> tie-off signal controls the ID value. Each ITS block must have a unique ID.</span></td>
</tr>
</tbody>
</table>
