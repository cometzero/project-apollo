# GITS_OPSR, Operation Status Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register>

### GITS\_OPSR, Operation Status Register

This register indicates cache lock status.

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

Figure 1. GITS\_OPSR bit assignments

![GITS_OPSR bit assignments](images/0159-GITS_OPSR-Operation-Status-Register-img01.svg)



<table id="uab1469452456222__tbl.gits_opsr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_OPSR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d56901e136" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d56901e139" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d56901e142" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">REQUEST_COMPLETE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Request to <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" title="This register controls cache lock.">GITS_OPR</a> completed</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">REQUEST_PASS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Request to <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" title="This register controls cache lock.">GITS_OPR</a> completed without error</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[61]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">REQUEST_IN_PROGRESS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Request to <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" title="This register controls cache lock.">GITS_OPR</a> in progress</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[60:50]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[49]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VIRTUAL</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the interrupt is virtual or physical:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             A physical interrupt is targeting the PE that GITS_OPSR.TARGET selects

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             A virtual interrupt is targeting the vPE that GITS_OPSR.TARGET selects

           </dd>
</dl> <p>Valid for trial and lock operations.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[48]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ENTRY_LOCKED</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Locked entry in cache corresponds to request (valid for trial and lock operations)</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[47:46]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[45:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">TARGET</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Target of interrupt, which is either:

          <ul>
<li>a vPE when GITS_OPSR.VIRTUAL == 1</li>
<li>a PE when GITS_OPSR.VIRTUAL == 0</li>
</ul> <p>Valid for trial and lock operations.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[15:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">ID of interrupt requested (valid for trial and lock operations)</td>
</tr>
</tbody>
</table>
