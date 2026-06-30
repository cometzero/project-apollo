# GICD_SAC, Secure Access Control register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register>

### GICD\_SAC, Secure Access Control register

This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.

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

Figure 1. GICD\_SAC bit assignments

![GICD_SAC bit assignments](images/0089-GICD_SAC-Secure-Access-Control-register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_SAC bit assignments</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d56041e140" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d56041e143" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d56041e146" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d56041e149" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:10]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, returns zero</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[9:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICPVIEW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">
<div class="documents-p">
             For configurations that support multi view, that is, when

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.VIEW == 1, this field controls which view can access the GICP registers:

            <dl>
<dt class="documents-dlterm">
               0

             </dt>
<dd>
               Only view 0 can access the GICP registers. The PMU records all events. This value occurs at reset.

             </dd>
<dt class="documents-dlterm">
               1

             </dt>
<dd>
               View 0 and view 1 can access the GICP registers. The PMU records events from view 1 only.

             </dd>
<dt class="documents-dlterm">
               2

             </dt>
<dd>
               View 0 and view 2 can access the GICP registers. The PMU records events from view 2 only.

             </dd>
<dt class="documents-dlterm">
               3

             </dt>
<dd>
               View 0 and view 3 can access the GICP registers. The PMU records events from view 3 only.

             </dd>
</dl>
</div> <p>RAZ/WI when no multi view support.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, returns zero</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SPF</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Controls whether Secure PMU events are visible to Non-secure software:

           <dl>
<dt class="documents-dlterm">
              0

            </dt>
<dd>
              Secure PMU event masking is disabled. The GIC reports Secure and Non-secure PMU events to Non-secure software and Secure software. This value occurs at reset.

            </dd>
<dt class="documents-dlterm">
              1

            </dt>
<dd>
              Secure PMU event masking is enabled. The GIC reports Non-secure PMU events but it does not report Secure PMU events to Non-secure software. All PMU events are visible to Secure software.

             <p>When <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en" title="This register contains information that enables test software to determine if the GIC-720AE system is compatible.">GICD_CFGID</a>.VIEW == 1, if GICPVIEW == 0, then do not set SPF to 1.</p>
</dd>
</dl> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICPNS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Controls whether the Non-secure world can access the Secure PMU data:

           <dl>
<dt class="documents-dlterm">
              0

            </dt>
<dd>
              Secure access only to the GICP registers.

            </dd>
<dt class="documents-dlterm">
              1

            </dt>
<dd>
              Allow Non-secure access to the GICP registers.

            </dd>
</dl> <p>The <span class="documents-g.signal.name"><span class="documents-keyword">gicp_allow_ns</span></span> tie-off signal controls the reset value<span> for each chip</span>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GICTNS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Controls whether the Non-secure world can access the Secure trace data and the error insertion registers:

           <dl>
<dt class="documents-dlterm">
              0

            </dt>
<dd>
              Secure access only to the GICT registers and the error insertion registers.

            </dd>
<dt class="documents-dlterm">
              1

            </dt>
<dd>
              Allow Non-secure access to the GICT registers and the error insertion registers. The error insertion registers are

             <span><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ERRINSRn--Error-Insertion-Registers?lang=en" title="This register can insert errors into the internal RAMs. You can use this register to test your error recovery software.">GICD_ERRINSRn</a>, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ERRINSR--Error-Insertion-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-SGIs-and-PPIs-summary/GICR-ERRINSR--Error-Insertion-Register?lang=en" title="This register can inject errors into the PPI RAM. You can use this register to test your error recovery software.">GICR_ERRINSR</a>, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-D-ERRINSR--Error-Insertion-Device-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-D-ERRINSR--Error-Insertion-Device-cache-register?lang=en" title="This register can insert errors into the ITS Device cache RAM. You can use this register to test your error recovery software.">GITS_D_ERRINSR</a>, <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-V-ERRINSR--Error-Insertion-Event-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-V-ERRINSR--Error-Insertion-Event-cache-register?lang=en" title="This register can insert errors into the ITS Event cache RAM. You can use this register to test your error recovery software.">GITS_V_ERRINSR</a>, and <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-C-ERRINSR--Error-Insertion-Collection-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-C-ERRINSR--Error-Insertion-Collection-cache-register?lang=en" title="This register can insert errors into the ITS Collection cache RAM. You can use this register to test your error recovery software.">GITS_C_ERRINSR</a></span>.

            </dd>
</dl> <p>The <span class="documents-g.signal.name"><span class="documents-keyword">gict_allow_ns</span></span> tie-off signal controls the reset value<span> for each chip</span>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RW</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">-</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Reserved, RES0</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">-</td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_SAC is accessible only by Secure accesses.
