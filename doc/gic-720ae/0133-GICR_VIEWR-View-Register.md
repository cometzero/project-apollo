# GICR_VIEWR, View Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register>

### GICR\_VIEWR, View Register

This register controls the view that this Redistributor belongs to.

### Configurations

This register is available in configurations that support multi view, that is, when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Redistributor registers for control and physical LPIs summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary?lang=en "The functions for the GIC-720AE physical LPIs are controlled through the Redistributor registers identified with the prefix GICR. These registers start from the base address of the Redistributor.") for the address offset, type, and reset value of this register.

### Usage constraints

If [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").RDC == 0, software must write to this register to assign each PE into a view, before it writes to any other registers and before it receives messages from any PE. Otherwise the behavior is unpredictable.

If
[GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").RDC == 1, software must:

1. Write to [GICD\_RDOFFR<n>](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC."), if the removal of some cores is necessary.
2. Write to [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor."), if changes to the affinity values are necessary.
3. Write to GICR\_VIEWR to assign PEs to a view. Software must complete the writes to GICR\_VIEWR registers, before it writes to any other registers and before it receives messages from any PE. Otherwise the behavior is unpredictable.

### Bit descriptions

Figure 1. GICR\_VIEWR bit assignments

![GICR_VIEWR bit assignments](images/0133-GICR_VIEWR-View-Register-img01.svg)



<table id="uxk1515416451404__tbl.gicr_viewr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_VIEWR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d154937e195" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d154937e198" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d154937e201" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[1:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">View</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Controls which view this Redistributor is assigned to:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             This Redistributor is assigned to view 0.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             This Redistributor is assigned to view 1.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             This Redistributor is assigned to view 2.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             This Redistributor is assigned to view 3.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_VIEWR is accessible only by Secure accesses from view 0.
