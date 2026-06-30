# GITS_OPR, Operations Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register>

### GITS\_OPR, Operations Register

This register controls cache lock.

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

Figure 1. GITS\_OPR bit assignments

![GITS_OPR bit assignments](images/0158-GITS_OPR-Operations-Register-img01.svg)



<table id="njp1469447471343__tbl.gits_opr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_OPR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d118174e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d118174e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d118174e142" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">LOCK_TYPE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Lock type supported:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Track

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Trial

           </dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             ITS lock

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
             ITS unlock

           </dd>
<dt class="documents-dlterm">
             4

           </dt>
<dd>
             Track abort

           </dd>
<dt class="documents-dlterm">
             8

           </dt>
<dd>
             ITS unlock all

           </dd>
<dt class="documents-dlterm">
             5‑7, 9‑15

           </dt>
<dd>
             Reserved

           </dd>
</dl>
<blockquote title="Note info">
<h3 class="documents-underline">Note</h3>
<ul>
<li>If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" title="This register indicates cache lock status.">GITS_OPSR</a>.REQUEST_IN_PROGRESS == 1 and software attempts a new access (other than Track abort (4) during a Track), then the behavior is unpredictable.</li>
<li>Invalidating the Event cache by using <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" title="This register controls many functions in the ITS such as cache invalidation, clock gating, and the scrubbing of all RAMs. The register is not distributed and only acts on the local chip.">GITS_FCTLR</a>.IEC unlocks all the locked entries. However, if a GITS_OPR lock request occurs while an invalidation is in progress (<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" title="This register controls many functions in the ITS such as cache invalidation, clock gating, and the scrubbing of all RAMs. The register is not distributed and only acts on the local chip.">GITS_FCTLR</a>.IEC == 1), then it is unpredictable whether the entries remain locked when the invalidation completes. This unpredictable behavior might cause <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" title="This register indicates cache lock status.">GITS_OPSR</a> to return an incorrect status.</li>
</ul>
</blockquote> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59:56]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[55:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DEVICE_ID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the DeviceID. The number of bits that are implemented in this field is configuration dependent. To determine the width of this field, software can read <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" title="This register returns information about the features that this ITS supports.">GITS_TYPER</a>.DevBits.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RES0</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[19:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">EVENT_ID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the EventID. The number of bits that are implemented in this field is configuration dependent. To determine the width of this field, software can read <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" title="This register returns information about the features that this ITS supports.">GITS_TYPER</a>.IDBits.</td>
</tr>
</tbody>
</table>
