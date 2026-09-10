# Software trigger protocol

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-trigger-protocol>

### Software trigger protocol

The wait status fields (STAT\_\*WAIT) indicate when the DMA channel can accept a software trigger. Software triggers cannot be initiated when the wait status field is zero.

### Software trigger input protocol

The intended trigger input type must be set in the \*SWTRIGINTYPE field. The trigger input request is initiated by writing 1 into the \*SWTRIGINREQ field. This can be done with the same register Write-Access as the one that sets the type or with a consequent Write-Access.

When the request is initiated, the associated STAT\_\*TRIGINWAIT flag is cleared to indicate that the processing of the request has been begun. The \*SWTRIGINTYPE field becomes read-only to keep the trigger input type stable throughout the trigger event.

When the trigger request is completed, the \*SWTRIGINREQ field is cleared and \*SWTRIGINTYPE field changes to be read/write again.

### Software trigger output protocol

The STAT\_TRIGOUTACKWAIT field indicates that a trigger output request is active and the software might send an acknowledge to it by writing 1 into SWTRIGOUTACK field.

The STAT\_TRIGOUTACKWAIT status field is cleared when the acknowledge is accepted.
