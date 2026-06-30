# Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Technical Reference Manual

Source: <https://developer.arm.com/documentation/102666/0201>

## Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Technical Reference Manual

### Revision: r2p1

### Release Information



<table>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th colspan="1" rowspan="1">Issue</th>
<th colspan="1" rowspan="1">Date</th>
<th colspan="1" rowspan="1">Confidentiality</th>
<th colspan="1" rowspan="1">Change</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="1" rowspan="1">0000-01</td>
<td colspan="1" rowspan="1">4 August 2023</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">First early access release for r0p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0001-02</td>
<td colspan="1" rowspan="1">18 September 2023</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">First early access release for r0p1</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0100-03</td>
<td colspan="1" rowspan="1">3 November 2023</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">First early access release for r1p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0001-04</td>
<td colspan="1" rowspan="1">19 December 2023</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">Second early access release for r0p1</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0200-05</td>
<td colspan="1" rowspan="1">29 February 2024</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">First early access release for r2p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0001-06</td>
<td colspan="1" rowspan="1">12 April 2024</td>
<td colspan="1" rowspan="1">Confidential</td>
<td colspan="1" rowspan="1">Third early access release for r0p1</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0100-07</td>
<td colspan="1" rowspan="1">23 May 2024</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">Second early access release for r1p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0200-08</td>
<td colspan="1" rowspan="1">19 July 2024</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">Second early access release for r2p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0100-09</td>
<td colspan="1" rowspan="1">31 December 2024</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">Third early access release for r1p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0200-10</td>
<td colspan="1" rowspan="1">28 February 2025</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">Third early access release for r2p0</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0201-11</td>
<td colspan="1" rowspan="1">10 April 2025</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">First early access release for r2p1</td>
</tr>
<tr>
<td colspan="1" rowspan="1">0201-12</td>
<td colspan="1" rowspan="1">30 January 2026</td>
<td colspan="1" rowspan="1">Non-Confidential</td>
<td colspan="1" rowspan="1">First REL release for r2p1</td>
</tr>
</tbody>
</table>



This document is protected by copyright and other related rights and the use or implementation of the information contained in this document may be protected by one or more patents or pending patent applications. No part of this document may be reproduced in any form by any means without the express prior written permission of Arm Limited ("Arm"). No license, express or implied, by estoppel or otherwise to any intellectual property rights is granted by this document unless specifically stated.

Your access to the information in this document is conditional upon your acceptance that you will not use or permit others to use the information for the purposes of determining whether the subject matter of this document infringes any third party patents.

The content of this document is informational only. Any solutions presented herein are subject to changing conditions, information, scope, and data. This document was produced using reasonable efforts based on information available as of the date of issue of this document. The scope of information in this document may exceed that which Arm is required to provide, and such additional information is merely intended to further assist the recipient and does not represent Arm’s view of the scope of its obligations. You acknowledge and agree that you possess the necessary expertise in system security and functional safety and that you shall be solely responsible for compliance with all legal, regulatory, safety and security related requirements concerning your products, notwithstanding any information or support that may be provided by Arm herein. In addition, you are responsible for any applications which are used in conjunction with any Arm technology described in this document, and to minimize risks, adequate design and operating safeguards should be provided for by you.

This document may include technical inaccuracies or typographical errors. THIS DOCUMENT IS PROVIDED "AS IS". ARM PROVIDES NO REPRESENTATIONS AND NO WARRANTIES, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE WITH RESPECT TO THE DOCUMENT. For the avoidance of doubt, Arm makes no representation with respect to, and has undertaken no analysis to identify or understand the scope and content of, any patents, copyrights, trade secrets, trademarks, or other rights.

TO THE EXTENT NOT PROHIBITED BY LAW, IN NO EVENT WILL ARM BE LIABLE FOR ANY DAMAGES, INCLUDING WITHOUT LIMITATION ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, PUNITIVE, OR CONSEQUENTIAL DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT OF ANY USE OF THIS DOCUMENT, EVEN IF ARM HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

Reference by Arm to any third party’s products or services within this document is not an express or implied approval or endorsement of the use thereof.

This document consists solely of commercial items. You shall be responsible for ensuring that any permitted use, duplication, or disclosure of this document complies fully with any relevant export laws and regulations to assure that this document or any portion thereof is not exported, directly or indirectly, in violation of such export laws. Use of the word “partner” in reference to Arm’s customers is not intended to create or refer to any partnership relationship with any other company. Arm may make changes to this document at any time and without notice.

This document may be translated into other languages for convenience, and you agree that if there is any conflict between the English version of this document and any translation, the terms of the English version of this document shall prevail.

The validity, construction and performance of this notice shall be governed by English Law.

The Arm corporate logo and words marked with ® or ™ are registered trademarks or trademarks of Arm Limited (or its affiliates) in the US and/or elsewhere. Please follow Arm’s trademark usage guidelines at <https://www.arm.com/company/policies/trademarks>. All rights reserved. Other brands and names mentioned in this document may be the trademarks of their respective owners.

Arm Limited. Company 02557590 registered in England.

110 Fulbourn Road, Cambridge, England CB1 9NJ.

PRE-1121-V1.0

### Confidentiality Status

This document is Non-Confidential. The right to use, copy and disclose this document may be subject to license restrictions in accordance with the terms of the agreement entered into by Arm and the party that Arm delivered this document to.

Unrestricted Access is an Arm internal classification.

### Product Status

The information in this document is Final, that is for a developed product.

### Feedback

Arm welcomes feedback on this product and its documentation. To provide feedback on the product, create a ticket on <https://support.developer.arm.com>.

To provide feedback on the document, fill the following survey: <https://developer.arm.com/documentation-feedback-survey>.

### Inclusive language commitment

Arm values inclusive communities. Arm recognizes that we and our industry have used language that can be offensive. Arm strives to lead the industry and create change.

We believe that this document contains no offensive language. To report offensive language in this document, email [terms@arm.com](mailto:terms@arm.com).
