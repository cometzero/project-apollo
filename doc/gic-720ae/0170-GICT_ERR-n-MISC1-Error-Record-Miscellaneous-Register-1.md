# GICT_ERR<n>MISC1, Error Record Miscellaneous Register 1

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC1--Error-Record-Miscellaneous-Register-1>

### GICT\_ERR<n>MISC1, Error Record Miscellaneous Register 1

This register contains the data value of an uncorrectable error in the LPI RAM, TGT\_LPI RAM, or ITS software information. The register is not present for other error records.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

If [GICT\_ERR<n>STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en "This register indicates information relating to the recorded errors.").MV == 1, then GICT\_ERR<n>MISC1 ignores writes.

### Bit descriptions

Figure 1. GICT\_ERR<n>MISC1 bit assignments

![GICT_ERR<n>MISC1 bit assignments](images/0170-GICT_ERR-n-MISC1-Error-Record-Miscellaneous-Register-1-img01.svg)



<table id="col1468837796034__tbl.gict_err_n_misc1">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERR<span>&lt;n&gt;</span>MISC1 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d179819e149" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d179819e152" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d179819e155" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:<code class="documents-option">x</code>+1] </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[<code class="documents-option">x</code>:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">INFO</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Contains the corrupted data that is read from the RAM.<p>The value <code class="documents-option">x</code> depends on the width of the RAM, which is set during the configuration of <span class="documents-keyword">GIC-720AE</span>.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERR<n>MISC1 is accessible only by Secure accesses.
