# Control the receiving of DVM snoop transactions

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/DVM-snoop-transaction-support/Control-the-receiving-of-DVM-snoop-transactions>

### Control the receiving of DVM snoop transactions

You must use the signals SYSCOREQS and SYSCOACKS to control the broadcasting of Distributed Virtual Messages (DVM) snoop transactions from the Accelerator Coherency Port (ACP) to your ACP manager.

### About this task

How to control the DynamIQ Shared Unit-120AE (DSU-120AE) to start or stop broadcasting DVM snoops from the ACP port, using a four-phase handshake, with the signals SYSCOREQS and SYSCOACKS.

> ### Note
>
> The use of
> SYSCOREQS (SYSCOREQ) and
> SYSCOACKS (SYSCOACK) is described in
>  [AMBA® AXI Protocol Specification](https://developer.arm.com/documentation/ihi0022/latest/).

### Procedure

1. Instruct your ACP manager to assert the SYSCOREQS signal (HIGH) when it is ready to receive DVM snoop transactions.
2. Wait for the signal SYSCOACKS to go HIGH. This signal indicates that DSU-120AE has acknowledged the request.

   When both the
   SYSCOREQS and
   SYSCOACKS signals are HIGH, the
   DSU-120AE is enabled to start broadcasting DVM snoop transactions on the ACP port.
3. When you want to stop receiving DVM snoop transactions, instruct your ACP manager to deassert SYSCOREQS signal (LOW).
4. Wait for the signal SYSCOACKS to go LOW.

   When the signal
   SYSCOACKS has gone LOW, the
   DSU-120AE stops the broadcasting of the DVM snoop transactions.

   > ### Note
   >
   > You must deassert
   > SYSCOREQS before you power off the cluster. Any request to power off the cluster will be denied if
   > SYSCOACKS remains HIGH.
