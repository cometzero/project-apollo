# GICR_PWRR, Power Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register>

### GICR\_PWRR, Power Register

This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.

Software can use this register to isolate the GIC Cluster Interface (GCI).

If software saves and restores the GICD state, then it must also use [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep to flush out the LPI caches to memory. See [Power management](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management?lang=en "The GIC-720AE can be powered down by the system power controller. The GIC also supports the power controller powering down the cores that the GIC services. The GICR_WAKER and the GICR_PWRR registers provide bits to control functions that are associated with power management.") for more information.

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

Figure 1. GICR\_PWRR bit assignments

![GICR_PWRR bit assignments](images/0131-GICR_PWRR-Power-Register-img01.svg)



<table id="dya1469457447054__tbl.gicr_pwrr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_PWRR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d126626e167" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d126626e170" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d126626e173" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d126626e176" rowspan="1">Type</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDG</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGroup. <span>This field indicates the number of the <span>GIC Cluster Interface (GCI)</span> of this Redistributor.</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGroupOffset. This field indicates the identifier of the current core within the <span><span>GCI</span></span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGPO</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGroupPoweredOff. This bit indicates:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
<span><span>GCI</span></span> is powered up and can be accessed.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             It is safe to power down the

            <span><span>GCI</span></span>.

           </dd>
</dl> <p>This bit changes state when the first or last PE on the <span><span>GCI</span></span> changes state.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGPD</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDGroupPowerDown. This bit indicates the intentional power state of the <span><span>GCI</span></span>:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Intend to power up.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Intend to power down.

           </dd>
</dl> <p>This bit changes state when the first or last PE on the <span><span>GCI</span></span> changes state.</p> <p>The <span><span>GCI</span></span> has reached its intentional power state when RDGPD = RDGPO.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">RO</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDAG</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RDApplyGroup. Setting this bit to 1 applies the RDPD value to all Redistributors on the same <span><span>GCI</span></span>.<p>If the RDPD value cannot be applied to all cores in the group, then the GIC ignores this request.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">WO</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RDPD</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RDPowerDown:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Redistributor is powered up and can be accessed.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The core permits the Redistributor to be powered down.

           </dd>
</dl> <p>Writes to 1 are ignored if <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en" title="This register controls whether the GIC-720AE can be powered down.">GICR_WAKER</a>.ProcessorSleep != 1.</p> <p>Writes are ignored if RDGPD != RDGPO and changing to not match RDGPD.</p> <p>If all other cores in the Redistributor group have RDPD == 1, then setting this bit to 1 also sets RDGPD = 1.</p> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">RW</td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_PWRR is accessible only by Secure accesses.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, this register is accessible only for view 0.

### Related reference

- [Redistributor power management](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management/Redistributor-power-management?lang=en "At reset, the Redistributors are considered to be powered down. To power up the Redistributors, software must use the GICR_PWRR register.")
