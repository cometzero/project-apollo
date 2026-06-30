# GICD_FCTLR3, Function Control Register 3

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR3--Function-Control-Register-3>

### GICD\_FCTLR3, Function Control Register 3

This register allows software to set some limitations on the cross-chip AXI5-Stream communications. The register is not distributed and acts only on the local chip. The GIC ignores this register for cross-chip ACE5-Lite communications, that is, when GICD\_CFGID.ACE\_CC == 1.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_FCTLR3 bit assignments

![GICD_FCTLR3 bit assignments](images/0094-GICD_FCTLR3-Function-Control-Register-3-img01.svg)



<table id="fyp1509720444139__tbl.gicd_fctlr3">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_FCTLR3 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d96719e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d96719e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d96719e142" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SCP1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">
<div class="documents-p">
            Controls whether to use separate credits for SPI and LPI commands:

           <dl>
<dt class="documents-dlterm">
              0

            </dt>
<dd>
              Unified credit

            </dd>
<dt class="documents-dlterm">
              1

            </dt>
<dd>
              Separate credit. This value occurs at reset.

            </dd>
</dl>
</div> <p>Sharing reduces the maximum number of outstanding 64-bit <span>AXI5-Stream</span> beats that are possible by two, if programmed in the sending and receiving chip.</p> <p>This bit has no effect in single-chip configurations. Any restriction limits the performance of cross-chip traffic, so if possible leave it unrestricted.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[4:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">NCP0</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"> <p>This field sets the maximum number of 64-bit <span>AXI5-Stream</span> beats between two chips. The allowable range of values for NCP0 is 6-31. The value at reset is 31.</p> <p>The maximum outgoing <span>AXI5-Stream</span> beats are 6 + NCP0 + SCP1.</p> <p>The maximum <span>AXI5-Stream</span> responses are 3 + SCP1(remote chip) + NCP0 (remote chip).</p> <p>This field has no effect in single-chip configurations. Any restriction limits the performance of cross-chip traffic, so if possible leave it unrestricted.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_FCTLR3 is accessible only by Secure accesses.
