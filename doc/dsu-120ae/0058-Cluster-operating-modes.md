# Cluster operating modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-operating-modes>

### Cluster operating modes

An operating mode is a component-specific configuration of the power modes. For the DynamIQ Shared Unit-120AE (DSU-120AE), the operating modes differ in the number of slices that are active, and in the amount of L3 cache RAM that is active. The cluster Power Policy Unit (PPU) provides programming access to control the operating modes and the power modes. The DSU-120AE supports several operating modes to control two groups of modes. One mode from each group can be combined together in any combination.

The cluster PPU can control how many L3 cache slices are active (powered up). The following table shows the operating modes for the L3 cache slices.

<table id="xhx1660577234644__table_wbk_1zh_q3b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Operating modes for L3 cache slices
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d83142e76" rowspan="1">
    Operating mode name
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d83142e79" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    One slice is active (powered up). This slice resides in its own power domain.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Half the total number of slices are powered up.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All slices are active (powered up).
   </td>
  </tr>
 </tbody>
</table>

The cluster PPU can also control how much of L3 cache RAMs are active (powered up) in cache slices that are active. The following table shows the operating modes for the L3 cache RAMs.

<table id="xhx1660577234644__table_bhm_qc3_q3b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Operating modes for L3 cache RAMs
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d83142e134" rowspan="1">
    Operating mode name
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d83142e137" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The L3 cache data and tag RAMs in each cache slice are powered down.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    One half of the L3 cache data and tag RAMs in each active slice are powered up.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All of the L3 cache data and tag RAMs in each active slice are powered up.
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> - In the No L3 cache Present configuration, there are only L3 cache slice operating modes.
