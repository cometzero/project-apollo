# FMU_SMERR, Safety Mechanism Inject Error register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMERR--Safety-Mechanism-Inject-Error-register>

### FMU\_SMERR, Safety Mechanism Inject Error register

This register injects one error into the specified protection mechanism inside a GIC block. Writes to this register cause an FMU\_CTRL\_ACCESS message to be sent with err\_insert=1.

By using this register, the system integrator must check a single protection mechanism from each block at Cold reset, to insert an error and check that the error wire and AXI5-Stream packet reporting to the FMU occurs. When a block type can have multiple instances such as an ITS or GCI, then the system integrator must check all instances of those blocks.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.") for the address offset, type, and reset value of this register.

### Usage constraints

- After a write to this register, poll [FMU\_STATUS](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-STATUS--FMU-Status-Register?lang=en "This register monitors whether there are any outstanding AXI5-Stream messages waiting for responses.").BUSY to ensure that the effect of the write is complete.
- Do not write to FMU\_SMERR and inject an error that corresponds to a powered-off block. See [Power management](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Software-interaction?lang=en#clw1525115882517__section.power_management).

### Bit descriptions

Figure 1. FMU\_SMERR bit assignments

![FMU_SMERR bit assignments](images/0198-FMU_SMERR-Safety-Mechanism-Inject-Error-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_SMERR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d178266e176" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d178266e179" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d178266e182" rowspan="1">Description</th>
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
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span>Protection mechanism</span> identifier.<p>See <a class="document-topic" document-topic-path="/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" href="https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Protection-mechanism-IDs?lang=en" title="The GIC assigns an ID for each protection mechanism in a functional block. For each protection mechanism ID we provide a description and the recommended recovery process.">Protection mechanism IDs</a> for the valid <span>protection mechanism</span> ID encodings for each BLKTYPE.</p> <p>Software can use the SMID=255 value to request a resend of errors from a specific block.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_SMERR is accessible only by Secure accesses.
