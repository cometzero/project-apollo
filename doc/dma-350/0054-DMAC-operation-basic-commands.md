# DMAC operation basic commands

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands>

### DMAC operation basic commands

This section contains an overview of DMA-350 operation basic commands.

### Transfer type 1D

Transfer type 1D is a one-dimensional block transfer. It transfers data from the source address to the destination address continuously in configured transfer size. This mode is the typical use-case for bulk data transfer where no data formatting is necessary during DMAC transfer. Transfer size setting range from byte to bus width in power of 2 increments. The transfer size is the same on both source and destination sides. The source and destination address are aligned with the transfer size as the lower address bits are ignored according to the TRANSIZE value. The number of transfers to copy are specified in transfer size increments. The SW can also limit the maximum burst length the DMAC can send to the bus to allow arbitrating others on the interconnect.

Figure 1. 1D transfer example

![1D transfer example](images/0054-DMAC-operation-basic-commands-img01.svg)

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   1D transfer attributes
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d39501e85" rowspan="1">
    <p>
     Parameter name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39501e89" rowspan="1">
    <p>
     Register map entry
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d39501e93" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Address
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_SRCADDR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The starting source address to transfer data from. The source address must be aligned with the transfer size.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Destination Address
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_DESADDR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The starting destination address to transfer data to. The destination address must be aligned with the transfer size.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source X-size
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_XSIZE.SRCXSIZE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The source number of transfers in the X dimension. The width of the source transfers is equal to the TRANSIZE value of the source transfers.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Destination X-size
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_XSIZE.DESXSIZE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The destination number of transfers in the X dimension. The width of the destination transfers is equal to the TRANSIZE value of the destination transfers.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Transfer size
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_CTRL.TRANSIZE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The data width that is utilized by both the source and the destination of the DMAC operation.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Priority
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_CTRL.PRIORITY
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This signal is passed on to the AXI as AxQOS and is used for arbitration between the channels.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source maximum burst size
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_SRCTRANSCFG.SRCMAXBURSTLEN
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The maximum burst length that is supported on the source side of the DMAC operation.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Destination maximum burst size
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_DESTRANSCFG.DESMAXBURSTLEN
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The maximum burst length that is supported on the destination side of the DMAC operation.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source AXI transfer properties
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_SRCTRANSCFG.SRCTRP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Source transfer properties
    </p>
    <p>
     These properties include memory type, shareability attribute, secure attribute and privilege attribute, and thus determine the values on the arprot, arcache, ardomain and arinner signals.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Destination AXI transfer properties
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_DESTRANSCFG.DESTRP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Destination transfer properties
    </p>
    <p>
     These properties include memory type, shareability attribute, secure attribute and privilege attribute, and thus determine the values on the awprot, awcache, awdomain and awinner signals.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D wrap type
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_CTRL.XTYPE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Determines how to handle some cases of 1D, when the source and the destination X-sizes are not equal.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fill value
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_FILLVAL
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The fill value for special wrap cases, when the destination X-size is larger than the source X-size, and the remainder of the address range must be filled with predefined values.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source address increment
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_XADDRINC.SRCXADDRINC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Increment used to calculate address on source side. The increment is: TRANSIZE * SRCXADDRINC
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Destination address increment
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CH&lt;x&gt;_XADDRINC.DESXADDRINC
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Increment used to calculate address on destination side. The increment is: TRANSIZE * DESXADDRINC
    </p>
   </td>
  </tr>
 </tbody>
</table>

- **[1D operation modes](/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands/1D-operation-modes?lang=en)**
   The WRAP functionality (1D wrap type) extends 1D transfers by allowing different source and destination memory sizes. This allows copying the same data multiple times to the destination location or filling an area with a default pattern.
- **[List of cases for 1D WRAP](/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands/List-of-cases-for-1D-WRAP?lang=en)**
   The 1D WRAP transfers can result in the following cases:
- **[1D transfers with increments](/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands/1D-transfers-with-increments?lang=en)**
   The 1D transfers also have increment capabilities to the source and destination addresses. It allows transferring memory ranges with gaps to other locations with different gaps. It also allows setting 0 increment to result in a peripheral like access targeting a single memory location with multiple accesses. The number of transfers is the same on both sides. Increments are based on the transfer size.
