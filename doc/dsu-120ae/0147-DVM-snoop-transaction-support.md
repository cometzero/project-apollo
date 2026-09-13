# DVM snoop transaction support

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/DVM-snoop-transaction-support>

### DVM snoop transaction support

The Accelerator Coherency Port (ACP) of the DynamIQ Shared Unit-120AE (DSU-120AE) supports Distributed Virtual Messages (DVM) snoop transactions. DVM snoop transactions are only sent from the ACP port to the ACP manager.

DVM snoop transactions can be used with a System Memory Management Unit (SMMU) to manage external coherent memory table walks and memory table updates.

The ACP supports the following DVM transaction features:

- Issue of both DVM Operations and DVM Sync transaction on the AC channel.
- Receiving of DVM Complete on the AR channel.

Only the following DVMOp transaction types are issued by the ACP subordinate port:

- TLB Invalidate
- Synchronization

The maximum number of outstanding DVMOp transactions that can be processed are:

- 1 DVMOp Sync transaction
- 4 DVMOp non-Sync transactions

To control the broadcast of DVM snoop transactions on the ACP port, see [Control the receiving of DVM snoop transactions](/documentation/107721/0001/ACP-subordinate-interface/DVM-snoop-transaction-support/Control-the-receiving-of-DVM-snoop-transactions?lang=en "You must use the signals SYSCOREQS and SYSCOACKS to control the broadcasting of Distributed Virtual Messages (DVM) snoop transactions from the Accelerator Coherency Port (ACP) to your ACP manager.").

> ### Note
>
> - If your ACP manager does not support DVMs, then tie the SYSCOREQS signal LOW.
> - When SYSCOREQS signal is HIGH, it prevents powering down of the cluster. Ensure you deassert SYSCOREQS when the device connected to ACP is inactive and ready to be powered down.
