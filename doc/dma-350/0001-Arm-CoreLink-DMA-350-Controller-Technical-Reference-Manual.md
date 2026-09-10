# Arm® CoreLink™ DMA-350 Controller Technical Reference Manual

Source: <https://developer.arm.com/documentation/102482/0000>

## Arm® CoreLink™ DMA-350 Controller Technical Reference Manual

### Revision: r0p0

### Release information

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th colspan="1" rowspan="1">
    Issue
   </th>
   <th colspan="1" rowspan="1">
    Date
   </th>
   <th colspan="1" rowspan="1">
    Confidentiality
   </th>
   <th colspan="1" rowspan="1">
    Change
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td colspan="1" rowspan="1">
    0000-01
   </td>
   <td colspan="1" rowspan="1">
    6 July 2021
   </td>
   <td colspan="1" rowspan="1">
    Confidential
   </td>
   <td colspan="1" rowspan="1">
    Initial release
   </td>
  </tr>
  <tr>
   <td colspan="1" rowspan="1">
    0000-02
   </td>
   <td colspan="1" rowspan="1">
    14 January 2022
   </td>
   <td colspan="1" rowspan="1">
    Non-Confidential
   </td>
   <td colspan="1" rowspan="1">
    EAC for r0p0
   </td>
  </tr>
  <tr>
   <td colspan="1" rowspan="1">
    0000-03
   </td>
   <td colspan="1" rowspan="1">
    15 December 2022
   </td>
   <td colspan="1" rowspan="1">
    Non-Confidential
   </td>
   <td colspan="1" rowspan="1">
    REL for r0p0
   </td>
  </tr>
  <tr>
   <td colspan="1" rowspan="1">
    0000-04
   </td>
   <td colspan="1" rowspan="1">
    18 January 2023
   </td>
   <td colspan="1" rowspan="1">
    Non-Confidential
   </td>
   <td colspan="1" rowspan="1">
    Second release of REL for r0p0
   </td>
  </tr>
 </tbody>
</table>

This document is protected by copyright and other related rights and the practice or implementation of the information contained in this document may be protected by one or more patents or pending patent applications. No part of this document may be reproduced in any form by any means without the express prior written permission of Arm. No license, express or implied, by estoppel or otherwise to any intellectual property rights is granted by this document unless specifically stated.

Your access to the information in this document is conditional upon your acceptance that you will not use or permit others to use the information for the purposes of determining whether implementations infringe any third party patents.

THIS DOCUMENT IS PROVIDED “AS IS”. ARM PROVIDES NO REPRESENTATIONS AND NO WARRANTIES, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE WITH RESPECT TO THE DOCUMENT. For the avoidance of doubt, Arm makes no representation with respect to, and has undertaken no analysis to identify or understand the scope and content of, patents, copyrights, trade secrets, or other rights.

This document may include technical inaccuracies or typographical errors.

TO THE EXTENT NOT PROHIBITED BY LAW, IN NO EVENT WILL ARM BE LIABLE FOR ANY DAMAGES, INCLUDING WITHOUT LIMITATION ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, PUNITIVE, OR CONSEQUENTIAL DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT OF ANY USE OF THIS DOCUMENT, EVEN IF ARM HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

This document consists solely of commercial items. You shall be responsible for ensuring that any use, duplication or disclosure of this document complies fully with any relevant export laws and regulations to assure that this document or any portion thereof is not exported, directly or indirectly, in violation of such export laws. Use of the word “partner” in reference to Arm’s customers is not intended to create or refer to any partnership relationship with any other company. Arm may make changes to this document at any time and without notice.

This document may be translated into other languages for convenience, and you agree that if there is any conflict between the English version of this document and any translation, the terms of the English version of the Agreement shall prevail.

The Arm corporate logo and words marked with ® or ™ are registered trademarks or trademarks of Arm Limited (or its affiliates) in the US and/or elsewhere. All rights reserved. Other brands and names mentioned in this document may be the trademarks of their respective owners. Please follow Arm’s trademark usage guidelines at <https://www.arm.com/company/policies/trademarks>.

Copyright © 2021–2023 Arm Limited (or its affiliates). All rights reserved.

Arm Limited. Company 02557590 registered in England.

110 Fulbourn Road, Cambridge, England CB1 9NJ.

(LES-PRE-20349|version 21.0)

### Confidentiality Status

This document is Non-Confidential. The right to use, copy and disclose this document may be subject to license restrictions in accordance with the terms of the agreement entered into by Arm and the party that Arm delivered this document to.

Unrestricted Access is an Arm internal classification.

### Product Status

The information in this document is Final, that is for a developed product.

### Feedback

Arm® welcomes feedback on this product and its documentation. To provide feedback on the product, create a ticket on <https://support.developer.arm.com>

To provide feedback on the document, fill the following survey: <https://developer.arm.com/documentation-feedback-survey>.

### Inclusive language commitment

Arm values inclusive communities. Arm recognizes that we and our industry have used language that can be offensive. Arm strives to lead the industry and create change.

Previous issues of this document included language that can be offensive. We have replaced this language. See [Revisions](/documentation/102482/0000/Revisions?lang=en "This appendix describes the technical changes between released issues of this document.").

To report offensive language in this document, email [terms@arm.com](mailto:terms@arm.com).
