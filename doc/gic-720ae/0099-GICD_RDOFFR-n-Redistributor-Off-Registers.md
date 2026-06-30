# GICD_RDOFFR<n>, Redistributor Off Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers>

### GICD\_RDOFFR<n>, Redistributor Off Registers

Each register allows Secure software to remove up to 64 cores from the GIC.

### Configurations

This register is available in configurations when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").RDC == 1.

### Attributes

Width
:   64-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

Software must program this register before any other GIC registers are accessed (other than reads to [GICR\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en "This register returns information about the features that this Redistributor supports.") and the ID registers) and before the GIC receives messages from any processors. Otherwise the behavior is unpredictable.

Software must ensure writes to GICD\_RDOFF<n> have completed before issuing subsequent accesses to the GIC. This can be achieved with a DSB.

### Bit descriptions

Figure 1. GICD\_RDOFFR<n> bit assignments

![GICD_RDOFFR<n> bit assignments](images/0099-GICD_RDOFFR-n-Redistributor-Off-Registers-img01.svg)



<table id="lok1505904594953__tbl.GICD_RDOFFRn">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_RDOFFR<span>&lt;n&gt;</span> bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d97033e169" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d97033e172" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d97033e175" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[63:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RD_OFF&lt;n&gt;</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Controls whether a core is removed from the GIC:

          <dl>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">m</code>] = 0

           </dt>
<dd>
             The core is not removed.

           </dd>
<dt class="documents-dlterm">
             Bit[

            <code class="documents-option">m</code>] = 1

           </dt>
<dd>
             Removes the core that is given by 64 × &lt;n&gt; +

            <code class="documents-option">m</code>. Where &lt;n&gt; represents the numeric identifier of this register, that is, 0-7.

           </dd>
</dl> <p>The bit order in the GICD_RDOFFR register is the order that the Redistributor pages appear in the default GIC address map, as defined by the order of <span>GCI</span> blocks and buses within them. These values are set by the <code class="documents-parmname">ppi_ref</code> and <code class="documents-parmname">bus</code> parameters in the configuration file.</p> <p>When software removes cores by setting some GICD_RDOFFR bits, the GICD updates other software-visible fields to match the reduced core count. These updates include:</p>
<ul>
<li>Moving <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.Last to the last Redistributor.</li>
<li>Moving the GICDA register page to the page above the last Redistributor.</li>
<li>Modifying the RAM RAS features such as scrub and error insertion, so that unused lines can never be accessed and report errors. See <a class="document-topic" document-topic-path="/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en#dsb1505904597662__section.limitations" href="https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Removing-cores-from-a-preconfigured-GIC?lang=en#dsb1505904597662__section.limitations">Limitations</a> for information about an MBIST limitation.</li>
</ul> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_RDOFFR<n> is accessible only by Secure accesses.
