# LPI clock Q-Channel

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-clock-Q-Channel>

### LPI clock Q-Channel

The clock Q-Channel interface is used to request clock quiescence from the DMAC. A clock controller drives the request while the DMAC either accepts or denies the request based on its current internal state. The DMAC can also request clock for an activity over the qactive signal.

The DMAC is not aimed to support forceful clock shutdown. When a request occurs and activity is ongoing, the DMAC simply denies the request and continues its operation. The request has no effect on the operation except the Q-Channel handshake.
