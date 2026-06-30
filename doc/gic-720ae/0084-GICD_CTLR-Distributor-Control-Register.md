# GICD_CTLR, Distributor Control Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register>

### GICD\_CTLR, Distributor Control Register

This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, this register is banked for each of the views.

See the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb) for the different architectural views of the GICD\_CTLR register.

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

Figure 1. GICD\_CTLR bit assignments

![GICD_CTLR bit assignments](images/0084-GICD_CTLR-Distributor-Control-Register-img01.svg)



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_CTLR bit descriptions</span>
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
<th class="documents-nocellnorowborder" colspan="1" id="d94653e160" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d94653e163" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d94653e166" rowspan="1">Description</th>
<th class="documents-nocellnorowborder" colspan="1" id="d94653e169" rowspan="1">Type</th>
<th class="documents-cell-norowborder" colspan="1" id="d94653e172" rowspan="1">Reset</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RWP</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Register Write Pending:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No register write in progress.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Register write in progress.

           </dd>
</dl> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">E1NWF</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enable 1 of N Wakeup Functionality</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Disable Security status:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds</span></span> signal was LOW when the GIC exited reset. Therefore, the Distributor supports 2 Security states and Non-secure accesses cannot access and modify registers that control Group 0 interrupts.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds</span></span> signal was HIGH when the GIC exited reset. Therefore, the Distributor only supports a single Security state and Non-secure accesses can access and modify registers that control Group 0 interrupts.

           </dd>
</dl> <p>See <a class="document-topic" document-topic-path="/102666/0201/Operation-of-GIC-720AE/Interrupt-groups-and-security?lang=en" href="https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Interrupt-groups-and-security?lang=en" title="The GIC-720AE configures the interrupts that it receives into one of three groups. Each group determines the security status of an interrupt and how it is routed.">Interrupt groups and security</a> for more information.</p> </td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">gicd_ctlr_ds</span></span> signal</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ARE_NS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity Routing Enable, Non-secure state. This bit is RES0 when GICD_CTLR.DS == 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ARE_S</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Affinity Routing Enable, Secure state. However, if GICD_CTLR.DS == 1, this bit is ARE and applies to the single security state.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RO</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EnableGrp1S</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enable Secure Group 1 interrupts. This bit is RES0 when GICD_CTLR.DS == 1.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">EnableGrp1NS</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Enable Non-secure Group 1 interrupts. However, if GICD_CTLR.DS == 1, enable Group 1 interrupts.</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">EnableGrp0</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Enable Group 0 interrupts</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RW</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">0</td>
</tr>
</tbody>
</table>
