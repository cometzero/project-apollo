# GICR_WAKER, Power Management Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register>

### GICR\_WAKER, Power Management Control Register

This register controls whether the GIC-720AE can be powered down.

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

Figure 1. GICR\_WAKER bit assignments

![GICR_WAKER bit assignments](images/0127-GICR_WAKER-Power-Management-Control-Register-img01.svg)

In the following table, the View column is applicable only for GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_WAKER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d170194e150" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d170194e153" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d170194e156" rowspan="1">Description</th>
<th class="documents-nocellnorowborder" colspan="1" id="d170194e159" rowspan="1">Type</th>
<th class="documents-cell-norowborder" colspan="1" id="d170194e162" rowspan="1">View</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Quiescent</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">When set to 1, it indicates that the <span class="documents-keyword">GIC-720AE</span> is idle and can be powered down if necessary.<p>This bit indicates the GICs response to the Sleep bit, and it is only set to 1 when Sleep == 1.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30:3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ChildrenAsleep</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">When set to 1, it indicates that the bus between the CPU interface and this <span>GIC Cluster Interface (GCI)</span> is quiescent.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ProcessorSleep</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Controls whether the GIC must assert a wake request signal before the <span>GCI</span> delivers an interrupt to the core:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The GIC never asserts a

            <span class="documents-g.signal.name"><span class="documents-keyword">wake_request</span></span> signal and the

            <span>GCI</span> delivers the interrupt to the core.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The GIC asserts a

            <span class="documents-g.signal.name"><span class="documents-keyword">wake_request</span></span> signal if there is a pending interrupt that targets the connected core. See

            <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Power-management/Processor-core-power-management?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management/Processor-core-power-management?lang=en" title="The GIC architecture defines the programming sequence to safely power down a core that connects to the GIC-720AE.">Processor core power management</a>.

            <p>If the GIC configuration supports local PE wake, then the <span>GCI</span> has <span class="documents-g.signal.name"><span class="documents-keyword">cpu_wake_request</span></span> signals. For these configurations, when a pending interrupt targets the connected core:</p>
<ul>
<li>The <span>GCI</span> asserts the <span class="documents-g.signal.name"><span class="documents-keyword">cpu_wake_request</span></span> signal.</li>
<li>The Wake Request block asserts the <span class="documents-g.signal.name"><span class="documents-keyword">wake_request</span></span> signal.</li>
</ul>
<p>See <a class="document-topic" document-topic-path="/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface?lang=en#pqo1489160639692__section.gci_pe_wake" href="https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface?lang=en#pqo1489160639692__section.gci_pe_wake">Local PE wake</a>.</p>
</dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0, 1, 2, 3</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Sleep</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Set this bit to 1, to flush the LPI cache:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Normal operation.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> ensures that all the caches are consistent with external memory and that it is safe to power down. See

            <a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Other-power-management?lang=en" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Other-power-management?lang=en" title="The GIC-720AE can be powered up and powered down using non-architectural protocols.">Other power management</a>.

           </dd>
</dl> <p>This bit is a separate control to the power controls that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en" title="This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.">GICR_PWRR</a> provides.</p> </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">0, 1</td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_WAKER is accessible only by Secure accesses.

### Related concepts

- [Other power management](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Other-power-management?lang=en "The GIC-720AE can be powered up and powered down using non-architectural protocols.")
