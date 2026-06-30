# GICD_CCCCR, Cross-Chip Control Credit Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCCR--Cross-Chip-Control-Credit-Register>

### GICD\_CCCCR, Cross-Chip Control Credit Register

This register controls the number of outstanding AXI5-Stream transactions to a set of remote chips that are assigned to the same credit group. The GICD\_CCCGR register controls the assignment of chips to a credit group.

### Configurations

This register is available in multichip configurations when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 0 and [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").CHIPS\_UPPER == 0, that is, there are ≤ 16 chips.

RES0 when either:

- [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 1
- [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").ACE\_CC == 0 and [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").CHIPS\_UPPER ≠ 0, that is, there are > 16 chips.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_CCCCR bit assignments

![GICD_CCCCR bit assignments](images/0091-GICD_CCCCR-Cross-Chip-Control-Credit-Register-img01.svg)



<table id="dav1466083275265__tbl.gicd_ccccr">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_CCCCR bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d39758e192" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d39758e195" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d39758e198" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Group3</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of outstanding <span>AXI5-Stream</span> transactions that are available for chips that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a> assigns to group 3:

          <dl>
<dt class="documents-dlterm">
             n

           </dt>
<dd>
<code class="documents-option">n</code> outstanding

            <span>AXI5-Stream</span> transactions available.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No limit.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Group2</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of outstanding <span>AXI5-Stream</span> transactions that are available for chips that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a> assigns to group 2:

          <dl>
<dt class="documents-dlterm">
             n

           </dt>
<dd>
<code class="documents-option">n</code> outstanding

            <span>AXI5-Stream</span> transactions available.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No limit.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Group1</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of outstanding <span>AXI5-Stream</span> transactions that are available for chips that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a> assigns to group 1:

          <dl>
<dt class="documents-dlterm">
             n

           </dt>
<dd>
<code class="documents-option">n</code> outstanding

            <span>AXI5-Stream</span> transactions available.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No limit.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[7:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Group0</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">The number of outstanding <span>AXI5-Stream</span> transactions that are available for chips that <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CCCGR--Cross-Chip-Control-Group-Register?lang=en" title="This register enables software to assign each chip to 1 of 4 credit groups. A credit group sets the number of outstanding AXI5-Stream transactions that can be sent to that group of chips.">GICD_CCCGR</a> assigns to group 0:

          <dl>
<dt class="documents-dlterm">
             n

           </dt>
<dd>
<code class="documents-option">n</code> outstanding

            <span>AXI5-Stream</span> transactions available.

           </dd>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             No limit.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_CCCCR is accessible only by Secure accesses.
