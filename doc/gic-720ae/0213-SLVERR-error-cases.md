# SLVERR error cases

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-subordinate-interface/SLVERR-error-cases>

### SLVERR error cases

The GIC ignores any transactions that are not standard single-beat memory accesses to a defined register, and it responds in a protocol-compliant manner.

If the GIC receives an errant transaction, then it records the error in software error record (Record 0). If [GICT\_ERR0CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").UE =1, the GIC returns an SLVERR response to an errant transaction. These error responses are disabled by default from reset. Software can disable some error reporting such as out-of-range register or accesses to unimplemented SPI registers, by using the [GICT\_ERR0CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").DIS\_\* bits.

> ### Note
>
> The subordinate interface does not support dataless cache stash transactions so they must not target the GIC.

It is also possible when accessing SPI, PPI, or SGI registers that data corruption might occur in the memory. If the internal ECC protection detects corrupt data, then it records the error in error record 0. The values in [GICT\_ERR0CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").UE and [GICD\_FCTLR2](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en "This register controls clock gating and other non-architectural controls in the local Distributor. The register is not distributed and acts only on the local chip.").ARP control how the GIC reports the error to the system, as the following table shows.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Subordinate response signaling for ECC detection errors</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d48449e108" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en" title="This register controls how interrupts are handled.">GICT_ERR0CTLR</a>.UE</th>
<th class="documents-nocellnorowborder" colspan="1" id="d48449e117" rowspan="1"><a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en" title="This register controls clock gating and other non-architectural controls in the local Distributor. The register is not distributed and acts only on the local chip.">GICD_FCTLR2</a>.ARP</th>
<th class="documents-cell-norowborder" colspan="1" id="d48449e131" rowspan="1">ACE signal</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">None</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">1</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">0</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">rresp</span></span> signal returns SLVERR</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">X</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">1</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1"><span class="documents-g.signal.name"><span class="documents-keyword">rpoison</span></span> signal is HIGH</td>
</tr>
</tbody>
</table>



[GICD\_FCTLR2](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-FCTLR2--Function-Control-Register-2?lang=en "This register controls clock gating and other non-architectural controls in the local Distributor. The register is not distributed and acts only on the local chip.").AWP controls whether the GIC uses the wpoison signal (causing the GIC to reject the transaction and report it) or whether the GIC ignores wpoison.

The GIC never returns a DECERR response.
