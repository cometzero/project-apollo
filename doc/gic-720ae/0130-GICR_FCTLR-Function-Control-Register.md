# GICR_FCTLR, Function Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register>

### GICR\_FCTLR, Function Control Register

This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for control and physical LPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en "The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICR\_FCTLR bit assignments

![GICR_FCTLR bit assignments](images/0130-GICR_FCTLR-Function-Control-Register-img01.svg)



<table id="wdr1469455264544__tbl.gicr_fctlr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_FCTLR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d44713e137" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d44713e140" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d44713e143" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:11]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GSPV_CGO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"> Clock gate override for GSPV:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Use full clock gating in the GSPV.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Leave clock running in the GSPV. If clock gates are not implemented, then you must use this value.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ECP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Enable combined packets. This bit controls whether the Redistributor combines packets to improve the latency when it connects to <span class="documents-keyword">Arm®</span> <span class="documents-keyword">Cortex®</span>-R82 cores:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The Redistributor does not combine GIC Stream messages.

            <span> This value occurs at reset, when <code class="documents-parmname">rlt</code> == 0. <code class="documents-parmname">rlt</code> is a configuration parameter.</span>
</dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The Redistributor combines GIC Stream messages, to improve the interrupt latency.

            <span> This value occurs at reset, when <code class="documents-parmname">rlt</code> == 1. <code class="documents-parmname">rlt</code> is a configuration parameter.</span>
</dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[8:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4:2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CGO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Clock gate override. One bit for each clock gate:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Use full clock gating.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Leave clock running. If clock gates are not implemented, then you must use this value.

           </dd>
</dl> <p>The clock gate bit assignments are:</p>
<dl>
<dt class="documents-dlterm">
             Bit[4], CGO[2]

           </dt>
<dd>
             Search clock gate.

           </dd>
<dt class="documents-dlterm">
             Bit[3], CGO[1]

           </dt>
<dd>
             Downstream message clock gate.

           </dd>
<dt class="documents-dlterm">
             Bit[2], CGO[0]

           </dt>
<dd>
             Upstream message clock gate.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">QD</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Q-Channel deny:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Allow Q-Channel accesses.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Deny Q-Channel accesses.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">SIP</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"> <p>Scrub in progress:</p>
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
</dl> <p>This bit is read and written by software. When a scrub is complete, the GIC clears the bit to 0.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_FCTLR is accessible only by Secure accesses.
