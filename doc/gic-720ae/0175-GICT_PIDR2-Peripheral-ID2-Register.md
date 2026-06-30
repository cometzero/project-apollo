# GICT_PIDR2, Peripheral ID2 Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-PIDR2--Peripheral-ID2-Register>

### GICT\_PIDR2, Peripheral ID2 Register

This register returns byte[2] of the peripheral ID. The GICT\_PIDR2 register is part of the set of trace and debug peripheral identification registers.

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

Figure 1. GICT\_PIDR2 bit assignments

![GICT_PIDR2 bit assignments](images/0175-GICT_PIDR2-Peripheral-ID2-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICT_PIDR2 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d97526e130" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d97526e133" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d97526e136" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ArchRev</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Identifies the version of the GIC architecture with which the trace and debug block complies:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x3</span>
</dt>
<dd>
             GICv3

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x4</span>
</dt>
<dd>
             GICv4

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">JEDEC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates that a JEDEC-assigned JEP106 identity code is used.</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[2:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">DES_1</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Bits[6:4] of the JEP106 identity code. Bits[3:0] of the JEP106 identity code are assigned to GICT_PIDR1[7:4].</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GICT\_PIDR2 is accessible only by Secure accesses.
