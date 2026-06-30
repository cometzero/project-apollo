# ITS control register summary

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary>

### ITS control register summary

The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.

This page does not exist in GIC-720AE configurations that do not support LPIs.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, these GITS registers are accessible for view 0 and view 1.

For descriptions of registers that are not specific to the GIC-720AE, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).



<table id="aba1429015812979__tbl.its_control_register_summary">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>ITS control register summary</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e110" rowspan="1">Offset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e113" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e116" rowspan="1">Type</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e119" rowspan="1">Reset</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e122" rowspan="1">Width</th>
<th class="documents-nocellnorowborder" colspan="1" id="d149630e126" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d149630e129" rowspan="1">Architecture defined?</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CTLR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x80000000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0004</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-IIDR--ITS-Implementer-Identification-Register?lang=en" title="This register provides information about the implementer and revision of the ITS.">GITS_IIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x070nn43B</span><p>The <code>nn</code> value depends on the r<code class="documents-varname">x</code>p<code class="documents-varname">y</code> identifier.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Implementer Identification Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register?lang=en" title="This register returns information about the features that this ITS supports.">GITS_TYPER</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Type Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0010</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPAMIDR--MPAM-ID-Register?lang=en" title="This register returns the maximum values that the Memory Partitioning and Monitoring (MPAM) fields can be set to in GITS_PARTIDR.">GITS_MPAMIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPAM ID Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0014</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PARTIDR--PART-ID-Register?lang=en" title="This register sets the Partition ID and PMG values that the ITS uses during memory accesses.">GITS_PARTIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Part ID Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0018</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" title="This register returns the ITS affinity when the vPE table is shared with Redistributors.">GITS_MPIDR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Affinity Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x001C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0020</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en" title="This register controls many functions in the ITS such as cache invalidation, clock gating, and the scrubbing of all RAMs. The register is not distributed and only acts on the local chip.">GITS_FCTLR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Function Control Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0024</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0028</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPR--Operations-Register?lang=en" title="This register controls cache lock.">GITS_OPR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Operations Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0030</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-OPSR--Operation-Status-Register?lang=en" title="This register indicates cache lock status.">GITS_OPSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Operation Status Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0038</span>- <span class="documents-g.number.hex">0x007C</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0080</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CBASER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">I﻿TS Command Queue Descriptor.<p>See the <a href="https://developer.arm.com/documentation/102923/latest" target="_blank"><span><cite>Learn the architecture - Generic Interrupt Controller v3 and v4, LPIs</cite></span></a>.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0088</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CWRITER</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿ITS Write Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0090</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CREADR</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">﻿ITS Read Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0098</span>- <span class="documents-g.number.hex">0x00FC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0100</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_BASER0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0107000000000000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Translation Table Descriptor Register0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0108</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_BASER1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0401000000000000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Translation Table Descriptor Register1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0110</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_BASER2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITS Translation Table Descriptor Register2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Yes</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0118</span>- <span class="documents-g.number.hex">0xDFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-D-ERRINSR--Error-Insertion-Device-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-D-ERRINSR--Error-Insertion-Device-cache-register?lang=en" title="This register can insert errors into the ITS Device cache RAM. You can use this register to test your error recovery software.">GITS_D_ERRINSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Device Cache error injection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC008</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-V-ERRINSR--Error-Insertion-Event-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-V-ERRINSR--Error-Insertion-Event-cache-register?lang=en" title="This register can insert errors into the ITS Event cache RAM. You can use this register to test your error recovery software.">GITS_V_ERRINSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Event Cache error injection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC010</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-C-ERRINSR--Error-Insertion-Collection-cache-register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-C-ERRINSR--Error-Insertion-Collection-cache-register?lang=en" title="This register can insert errors into the ITS Collection cache RAM. You can use this register to test your error recovery software.">GITS_C_ERRINSR</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">64</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Collection Cache error injection</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xC018</span>- <span class="documents-g.number.hex">0xEFFC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF000</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-CFGID--Configuration-ID-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-CFGID--Configuration-ID-Register?lang=en" title="This register returns information about the configuration of the ITS block such as its ID number.">GITS_CFGID</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration dependent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>64</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Configuration ID Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF008</span>- <span class="documents-g.number.hex">0xFFCC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR4</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x44</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 4 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR5</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 5 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFD8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR6</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 6 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFDC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR7</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 7 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x94</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFE8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PIDR2--Peripheral-ID2-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-PIDR2--Peripheral-ID2-Register?lang=en" title="This register returns byte[2] of the peripheral ID. The GITS_PIDR2 register is part of the set of ITS peripheral identification registers.">GITS_PIDR2</a></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>Configuration dependent</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFEC</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_PIDR3</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x00</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Peripheral ID 3 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CIDR0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x0D</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 0 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF4</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CIDR1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xF0</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 1 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFF8</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">GITS_CIDR2</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0x05</span></td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">32</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Component ID 2 Register</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">No</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xFFFC</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">GITS_CIDR3</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RO</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><span class="documents-g.number.hex">0xB1</span></td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">32</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Component ID 3 Register</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">No</td>
</tr>
</tbody>
</table>
