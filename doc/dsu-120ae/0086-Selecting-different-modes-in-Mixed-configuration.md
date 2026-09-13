# Selecting different modes in Mixed-configuration

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Selecting-different-modes-in-Mixed-configuration-->

### Selecting different modes in Mixed-configuration

In Mixed-configuration, the three different modes, namely Lock-mode, Split-mode, and Hybrid-mode are selected at cluster reset time using pins. The CORESLDEFAULT and CLUSTERSLDEFAULT signals are used to select the mode, and they only take effect when the nRESET pin is deasserted. The mode selected is shown in the CLUSTERAE\_CLUSTERSLCTLR and CLUSTERAE\_CORESLCTLR registers which are read only.

Updates to the CORESLDEFAULT and CLUSTERSLDEFAULT signals take effect when the related cluster or core logic exits reset.

The following table shows for the mapping between the Mixed-configuration modes and the register programming.

<table id="nbu1672845614036__table_zr5_xtn_fwb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Permitted
   <span>
    Mixed-configuration
   </span>
   mode selection
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d36e89" rowspan="1">
    <span>
     Mixed-configuration
    </span>
    mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d36e94" rowspan="1">
    CLUSTERSLDEFAULT and CLUSTERAE_CLUSTERSLCTLR
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d36e97" rowspan="1">
    CORESLDEFAULT and CLUSTERAE_CORESLCTLR
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Split-mode
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Split
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Split
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Lock-mode
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Lock
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Lock
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Hybrid-mode
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Lock
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Split
   </td>
  </tr>
 </tbody>
</table>
