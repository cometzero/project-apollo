# Hashing for CHI transaction distribution

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/Hashing-for-CHI-transaction-distribution>

### Hashing for CHI transaction distribution

When more than one bus requester port is implemented, the hashing to decide which transaction goes to which address target group is based on the Physical Address (PA) of the transaction, and the number of requester ports configured. There is a 1-bit, 2-bit, or 3-bit value that is used to identify the address target group number for each transaction depending on the number of bus requester ports configured. This gives a maximum of eight groups.

### Hashing for two, four, or eight address target groups

The hash function determines which address target group the PA of the transaction is sent to. The hash masks the transaction PA with a configurable mask, and then XORs all the resultant bits together. The configurable mask is set using the REQUESTERINTERLEAVE\* signals before the cluster leaves reset. In the following functions:

- REQUESTERINTERLEAVE0 is the configurable mask value set by REQUESTERINTERLEAVE0 input signal.
- REQUESTERINTERLEAVE1 is the configurable mask value set by REQUESTERINTERLEAVE1 input signal.
- REQUESTERINTERLEAVE2 is the configurable mask value set by REQUESTERINTERLEAVE2 input signal.
- ADDRESS is the PA of the transaction.

Hashing for two address target groups
:   The hash is:

    ```
    ADDRESS TARGET GROUP bit[0] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE0[39:6])
    ```

Hashing for four address target groups
:   The hash is:

    ```
    ADDRESS TARGET GROUP bit[0] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE0[39:6])
    ADDRESS TARGET GROUP bit[1] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE1[39:6])
    ```

Hashing for eight address target groups
:   The hash is:

    ```
    ADDRESS TARGET GROUP bit[0] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE0[39:6])
    ADDRESS TARGET GROUP bit[1] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE1[39:6])
    ADDRESS TARGET GROUP bit[2] = ^(ADDRESS[39:6] & REQUESTERINTERLEAVE2[39:6])
    ```

### Hashing for six address target groups

In the following function:

- ADDRESS is the PA of the transaction.
- REQUESTERADDRBITSELBOTTOM is the value set by REQUESTERADDRBITSELBOTTOM input signal.
- REQUESTERADDRBITSELTOP0 is the value set by REQUESTERADDRBITSELTOP0 input signal.
- REQUESTERADDRBITSELTOP1 is the value set by REQUESTERADDRBITSELTOP1 input signal.
- REQUESTERADDRBITSELTOP2 is the value set by REQUESTERADDRBITSELTOP2 input signal.
- REQUESTERTOPADDRBITINV is the value set by REQUESTERTOPADDRBITINV input signal.

The hash is:

```
ADDRESS TARGET GROUP[2:0] =
(ADDRESS[REQUESTERADDRBITSELBOTTOM[3:0] +: 3]
+ ADDRESS[REQUESTERADDRBITSELBOTTOM[3:0]+3 +: 3]
+ ADDRESS[REQUESTERADDRBITSELBOTTOM[3:0]+6 +: 3]
+ (((REQUESTERTOPADDRBITINV ^ ADDRESS[REQUESTERADDRBITSELTOP2[5:0]])<< 2)
|(ADDRESS[REQUESTERADDRBITSELTOP1[5:0]]<< 1)
| ADDRESS[REQUESTERADDRBITSELTOP0[5:0]])) % 6
```

The maximum value that can be output from this function is 0b101 (six groups).

> ### Note
>
> For information on the functionality of the signals used in the hash functions, see the
>  CHI clock and configuration signals section in the
> Functional integration chapter of the
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
