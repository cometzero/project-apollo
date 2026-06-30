# FMU_SMCR, Safety Mechanism Set Criticality Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMCR--Safety-Mechanism-Set-Criticality-Register>

### FMU\_SMCR, Safety Mechanism Set Criticality Register

This register sets the protection mechanism criticality. When the FMU receives a write access to this register then it sends an FMU\_CTRL\_ACCESS message to the fault collators that reside in the other GIC components.

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
- Do not write to FMU\_SMCR that corresponds to a powered-off block. See [Power management](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Fault-Management-Unit/Software-interaction?lang=en#clw1525115882517__section.power_management).

### Bit description

Figure 1. FMU\_SMCR bit assignments

![FMU_SMCR bit assignments](images/0199-FMU_SMCR-Safety-Mechanism-Set-Criticality-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>FMU_SMCR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d582e156" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d582e159" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d582e162" rowspan="1">Description</th>
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
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">CR</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the criticality of a <span>protection mechanism</span>:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Sets the

            <span>protection mechanism</span> as a non-critical error. As the GIC exits reset, it applies this setting to the RAM SEC errors, that is, the SM_SEC*

            <span>protection mechanism</span>s.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Sets the

            <span>protection mechanism</span> as a critical error. As the GIC exits reset, it applies this setting to all

            <span>protection mechanism</span>s except for the RAM SEC

            <span>protection mechanism</span>s.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

FMU\_SMCR is accessible only by Secure accesses.
