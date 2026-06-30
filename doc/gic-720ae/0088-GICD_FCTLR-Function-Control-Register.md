# GICD_FCTLR, Function Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR--Function-Control-Register>

### GICD\_FCTLR, Function Control Register

This register controls non-architectural functionality such as the scrubbing of all RAMs in the local Distributor. The register is not distributed and acts only on the local chip.

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

Figure 1. GICD\_FCTLR bit assignments

![GICD_FCTLR bit assignments](images/0088-GICD_FCTLR-Function-Control-Register-img01.svg)



<table id="zua1505377137047__tbl.gicd_fctlr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_FCTLR bit assignments</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d35707e135" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d35707e138" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d35707e141" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:27]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[26]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">POS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Point of serialization. Secure access only.<p>When an interrupt is sent remotely and POS is set, it ensures that writes to GICD_SETSPI and GICD_CLRSPI propagate to remote chips before <span>ACE5-Lite</span> sends a response. Applies only to edge-triggered interrupts.</p>
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Store locally and propagate when possible.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Propagate access to POS.

           </dd>
</dl> <p>Resets to <span class="documents-g.number.bin">0b0</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[25:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CLPL</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Cross-chip LPI limit. Secure access only.<p>This field enables you to reduce the number of cross-chip LPI transactions that can be outstanding to each chip:</p>
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <code class="documents-parmname">lpi_cc_tokens</code> configuration parameter sets the maximum number of cross-chip LPI transactions that can be outstanding to each chip.

           </dd>
<dt class="documents-dlterm">
             1-15

           </dt>
<dd>
             The maximum number of cross-chip LPI transactions that can be outstanding to each chip. If you set a value that is greater than

            <code class="documents-parmname">lpi_cc_tokens</code>, then the GIC behaves as if CLPL == 0.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19:18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">NSACR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Non-secure access control. Values are as described in the GICD_NSACR register. This is the value that is used if an SPI has an error.<p>Secure access only. Resets to <span class="documents-g.number.bin">0b00</span>.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, returns <span class="documents-g.number.bin">0b000</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SIP</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Scrub in progress.<p>When read:</p>
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No scrub in progress.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Scrub in progress.

           </dd>
</dl> <p>When written:</p>
<dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Abort the scrub.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Start a scrub.

           </dd>
</dl> <p>When a scrub is complete, the GIC clears the bit to 0.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 0, some bits are accessible only by Secure accesses. If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, then GICD\_FCTLR is accessible only by Secure accesses from view 0.
