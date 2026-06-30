# GICT_DEVID, Device Configuration register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-DEVID--Device-Configuration-register>

### GICT\_DEVID, Device Configuration register

This register returns information about the configuration of the GIC-720AE GICT such as whether an LPI or ITS is available.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICT\_DEVID bit assignments

![GICT_DEVID bit assignments](images/0174-GICT_DEVID-Device-Configuration-register-img01.svg)



<table id="col1468854647391__table.gict_devid">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_DEVID bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d70827e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d70827e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d70827e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NUM</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the index of the last error record, plus one:

          <dl>
<dt class="documents-dlterm">
             9

           </dt>
<dd>
             No LPI available.

           </dd>
<dt class="documents-dlterm">
             28-60

           </dt>
<dd>
             LPI available with one or more ITS. The number of ITSs = NUM − 28.

           </dd>
<dt class="documents-dlterm">
             64

           </dt>
<dd>
             This value occurs when the GIC has an

            <span>ACE5-Lite</span> cross-chip interface.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_DEVID is accessible only by Secure accesses.
