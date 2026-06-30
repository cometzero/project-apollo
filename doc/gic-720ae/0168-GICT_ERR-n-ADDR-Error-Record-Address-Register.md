# GICT_ERR<n>ADDR, Error Record Address Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-ADDR--Error-Record-Address-Register>

### GICT\_ERR<n>ADDR, Error Record Address Register

This register contains the address and security status of the write. This register is present only for GICT software record 0.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64-bit

Functional group
:   See
    [GICT register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary?lang=en "The GIC-720AE trace and debug functions are controlled through registers that are identified with the prefix GICT.") for the address offset, type, and reset value of this register.

### Usage constraints

Ignores writes if [GICT\_ERR<n>STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en "This register indicates information relating to the recorded errors.").AV == 1.

All bits are RAZ/WI except when [GICT\_ERR<n>STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-STATUS--Error-Record-Primary-Status-Register?lang=en "This register indicates information relating to the recorded errors.").IERR = 0, 0x12, 0x13, or 0x14.

### Bit descriptions

Figure 1. GICT\_ERR<n>ADDR bit assignments

![GICT_ERR<n>ADDR bit assignments](images/0168-GICT_ERR-n-ADDR-Error-Record-Address-Register-img01.svg)



<table id="col1468830912655__tbl.gict_err_n_addr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_ERR&lt;n&gt;ADDR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d12864e156" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d12864e159" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d12864e162" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">NS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Non-secure attribute:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The address is Secure.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The address is Non-secure.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62:52]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[51:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PADDR</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">The error address. The <code class="documents-parmname">axis_addr_width</code> configuration parameter controls how many bits in this field are implemented, that is, from bit[0]-bit[<code class="documents-parmname">axis_addr_width</code>−1].</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_ERR<n>ADDR is accessible only by Secure accesses.
