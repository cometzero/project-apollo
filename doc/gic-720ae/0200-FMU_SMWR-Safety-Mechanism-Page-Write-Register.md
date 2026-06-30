# FMU_SMWR, Safety Mechanism Page Write Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWR--Safety-Mechanism-Page-Write-Register>

### FMU\_SMWR, Safety Mechanism Page Write Register

This register performs a page write access that is then followed by a page read access. When the FMU receives a write access to this register then it sends an FMU\_PAGE\_ACCESS message to the fault collators that reside in the other GIC components.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

- Before software writes to this register, it must write to [FMU\_SMWDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en "This register contains the data that is written during a page write access.").
- After a write to this register, poll [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").BUSY to ensure that the effect of the write is complete.
- Do not write to FMU\_SMWR that corresponds to a powered-off block. See [Power management](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Software-interaction?lang=en#clw1525115882517__section.power_management).

### Bit description

Figure 1. FMU\_SMWR bit assignments

![FMU_SMWR bit assignments](images/0200-FMU_SMWR-Safety-Mechanism-Page-Write-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_SMWR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d10409e163" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d10409e166" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d10409e169" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30:28]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">BLKTYPE</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Block type identifier:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             GICD

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Wake Request

           </dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             SPI Collator

           </dd>
<dt class="documents-dlterm">
             3

           </dt>
<dd>
<span>GIC Cluster Interface (GCI)</span>
</dd>
<dt class="documents-dlterm">
             4

           </dt>
<dd>
             ITS

           </dd>
<dt class="documents-dlterm">
             5

           </dt>
<dd>
             FMU

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[27:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">BLKID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Block identifier. The permitted values are:

          <ul>
<li>0 when BLKTYPE == 0, 1, or 5.</li>
<li>0-<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" title="This register defines which of the common architecturally defined features are implemented and, of the implemented features, which are software programmable. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR4FR</a>.MBID when BLKTYPE == 2.</li>
<li>0-<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" title="This register defines which of the common architecturally defined features are implemented and, of the implemented features, which are software programmable. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR6FR</a>.MBID when BLKTYPE == 3. The BLKID that is used to access a <span>GCI</span> does not change, even if processors are removed from a pre-configured GIC. See <a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en" title="The GIC can be configured to either enable Secure software or a tie-off signal to remove cores from a GIC configuration. This feature enables you to use a single GIC configuration in multiple products that contain a different number of cores.">Removing cores from a preconfigured GIC</a>.</li>
<li>0-<a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-ERR-n-FR--Error-Record--n--Feature-Register?lang=en" title="This register defines which of the common architecturally defined features are implemented and, of the implemented features, which are software programmable. GIC-720AE supports 12 error records, n = 0-11.">FMU_ERR8FR</a>.MBID when BLKTYPE == 4.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SMID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Safety Mechanism identifier.<p>See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" title="The GIC assigns an ID for each protection mechanism in a functional block. For each protection mechanism ID we provide a description and the recommended recovery process.">Protection mechanism IDs</a> for the valid <span>protection mechanism</span> ID encodings for each BLKTYPE.</p> <p>Software can use the SMID=255 value to request a resend of errors from a specific block.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">PAGEID</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">The ID of the page to write to. The number of pages that are available depends on the <span>protection mechanism</span>:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Available for all

            <span>protection mechanism</span>s.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Available for:

            <ul>
<li><span>AXI5-Stream</span> protection</li>
<li><span>AXI5-Stream</span> cross-chip protection</li>
<li><span>ACE5-Lite</span> cross-chip protection</li>
<li>interrupt protection</li>
<li>CPU interface (CPUIF) protection.</li>
</ul>
</dd>
<dt class="documents-dlterm">
             2

           </dt>
<dd>
             Available for:

            <ul>
<li><span>AXI5-Stream</span> protection</li>
<li>interrupt protection</li>
<li>CPUIF protection.</li>
</ul>
</dd>
<dt class="documents-dlterm">
             3

            <span>-4</span>
</dt>
<dd>
             Available for CPUIF protection.

           </dd>
<dt class="documents-dlterm">
<span>5</span>-255

           </dt>
<dd>
             Reserved.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_SMWR is accessible only by Secure accesses.
