# GICR_CLASSR, Class Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CLASSR--Class-Register>

### GICR\_CLASSR, Class Register

This register specifies which class of 1 of N interrupt the CPU accepts.

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

Figure 1. GICR\_CLASSR bit assignments

![GICR_CLASSR bit assignments](images/0132-GICR_CLASSR-Class-Register-img01.svg)



<table id="ypm1469460392687__tbl.gicr_classr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICR_CLASSR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d71071e133" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71071e136" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d71071e139" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ/WI    </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Class</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Interrupt class:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Class 0

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Class 1

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICR\_CLASSR is accessible only by Secure accesses.

### Related reference

- [SPI routing and 1 of N selection](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/SPIs/SPI-routing-and-1-of-N-selection?lang=en "If GICD_TYPER.No1N==0, then the GIC-720AE supports 1 of N selection of SPI interrupts. You can program an SPI to target several cores, and the GIC-720AE can select which cores receive an SPI.")

### Related information

- [GICD\_ICLARn, Interrupt Class Registers](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers?lang=en "These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD_ICLAR2-GICD_ICLAR61.")
