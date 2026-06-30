# GICD_ICERRRn, Interrupt Clear Error Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICERRRn--Interrupt-Clear-Error-Registers>

### GICD\_ICERRRn, Interrupt Clear Error Registers

These registers can clear the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD\_ICERRR1-GICD\_ICERRR30.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

The Distributor provides up to 30 registers to support 960 SPIs. If you configure the GIC-720AE to use fewer than 960 SPIs, it reduces the number of registers accordingly. For locations where interrupts are not implemented, the register is RAZ/WI.

### Bit descriptions

Figure 1. GICD\_ICERRRn bit assignments

![GICD_ICERRRn bit assignments](images/0104-GICD_ICERRRn-Interrupt-Clear-Error-Registers-img01.svg)



<table id="aba1434704574926__tbl.gicd_ierrr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_ICERRRn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d36e138" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d36e141" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d36e144" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Status</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Indicates whether an SPI is in an error state:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             If read, the SPI is not in an error state and programming is valid. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             If read, the SPI is in an error state and programming is not valid. Writing 1 clears the error.

           </dd>
</dl> <p>Non-secure software can access this register, only if Secure software has previously used the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRn--Interrupt-Clear-Group-Error-registers?lang=en" title="These registers can clear the error status of the GICD_IGROUPRn, GICD_IGRPMODRn, and GICD_NSACRn registers of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD_ICGERR1-GICD_ICGERR30.">GICD_ICGERRn</a> or <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICGERRnE--Interrupt-Clear-Group-Error-registers-Extended?lang=en" title="These registers can clear the error status of the GICD_IGROUPRnE, GICD_IGRPMODRnE, and GICD_NSACRnE registers of an SPI, or it returns the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has up to 32 registers, GICD_ICGERR0E-GICD_ICGERR31E.">GICD_ICGERRnE</a> to clear the group information, and it has reprogrammed the group.</p> <p>The SPI that a bit refers to, depends on its bit position and the base address offset of the GICD_ICERRR<code class="documents-option">n</code>, that is, SPI = 32×<code class="documents-option">n</code> + bit[number].</p> </td>
</tr>
</tbody>
</table>
