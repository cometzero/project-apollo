# GICD_CCCTLR, Cross-Chip Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCTLR--Cross-Chip-Control-Register>

### GICD\_CCCTLR, Cross-Chip Control Register

This register controls the features in the GICD that relate to an ACE5-Lite cross-chip interface. The register is not distributed and acts only on the local socket.

### Configurations

This register is available in multichip configurations when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 1.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_CCCTLR bit assignments

![GICD_CCCTLR bit assignments](images/0095-GICD_CCCTLR-Cross-Chip-Control-Register-img01.svg)



<table id="axm1475056570302__tbl.gicd_ccctlr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_CCCTLR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d85190e143" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d85190e146" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d85190e149" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:12]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[11:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CC_CREDIT</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of credits that are available:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0xFF</span>
</dt>
<dd>
             255 credits or

            <code class="documents-parmname">ace_cc_credits</code> credits are available. The cross-chip interface uses the lower value.

           </dd>
<dt class="documents-dlterm">
             …

           </dt>
<dd>
             …

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x02</span>
</dt>
<dd>
             2 credits or

            <code class="documents-parmname">ace_cc_credits</code> credits are available. The cross-chip interface uses the lower value.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x01</span>
</dt>
<dd>
             1 credit or

            <code class="documents-parmname">ace_cc_credits</code> credits are available. The cross-chip interface uses the lower value.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x00</span>
</dt>
<dd>
             The number of credits available is

            <code class="documents-parmname">ace_cc_credits</code>. The

            <code class="documents-parmname">ace_cc_credits</code> value is set during the GIC configuration stage.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CC_SHARED</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Controls whether transactions are shareable:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             All transactions use shared IDs.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Unordered, always use unique IDs.

            <p>The cross-chip CRC scheme does not protect the <span class="documents-g.signal.name"><span class="documents-keyword">bid_m</span></span> signal. If the chip-chip interconnect does not support parity or perform some other check on the <span class="documents-g.signal.name"><span class="documents-keyword">bid_m</span></span> signal, then we strongly recommend that CC_SHARED is set to 1.</p>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CC_BUFF</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Controls whether transactions are bufferable:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Transactions are bufferable.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Transactions are Non-bufferable.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CC_MOD</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Controls whether transactions are bufferable:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Normal

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Device

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_CCCTLR is accessible only by Secure accesses.
