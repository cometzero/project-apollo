# LPI power P-Channel

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-power-P-Channel>

### LPI power P-Channel

The power P-Channel interface is used to request power quiescence from the DMAC. A power controller drives the request while the DMAC either accepts or denies the request based on its current internal state. The DMAC can also request power for an activity over the pactive signal.

pactive supports a 10-bit wide activity indication from Off to Warm reset. However, the DMAC only asserts Off, Full retention mode and On indications.

The DMAC is not aimed to support forceful power shutdown. When a request occurs and activity is ongoing, the DMAC simply denies the request and continues its operation. The request has no effect on the operation except the P-Channel handshake.
