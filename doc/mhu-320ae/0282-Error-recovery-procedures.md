# Error recovery procedures

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-recovery-procedures>

### Error recovery procedures

When a protection mechanism is triggered then it might be necessary for software to perform a recovery procedure, so that the MHU-320AE or system can continue functioning. The following sections provide guidance about the recovery process that we recommend for the MHU Sender and MHU Receiver protection mechanism IDs.

### Asynchronous input error recovery

The MHU does not need to be reset after an asynchronous input error because corrupt input transitions are contained by the input protection logic. The incoming event might not have been sampled, but architectural MHU operation is unaffected.

### Block reset

The MHUS, MHUR, and their corresponding FMUs must be reset. Follow the steps in the [Power management](/documentation/107612/0001/Operations-of-MHU-320AE/Power-management?lang=en "Each domain present in a MHU-320AE configuration exposes a power Q-Channel interface that allows the system power controller to power down the corresponding domain.") section to get all the blocks into the defined state before resetting them.

It is possible that the system is in a state where it is unable to complete the full powerdown sequence and a complete system reset is required.

### CRC error recovery

Read the error type from the AXI5-Stream protection block that is reporting the error. If the error type is a:

CRC timeout error
:   Increase the CRC timeout and continue. If the timeout is repeatable, then it might require a block reset.

CRC error
:   Perform a block reset, as described in Block reset.

### External error recovery

An external error does not indicate an issue within the MHU. The system integrator is responsible for ensuring that recovery is sufficient for the external error source, which might include resetting the MHU or the entire system.

### FMU APB access error recovery

If the FMU has detected an incorrect access type, then there is no specific recovery procedure needed. The error has been contained by the FMU. If software was attempting an update when this error occurred, then software should repeat the update.

### FMU APB recovery

If an APB parity error occurred on the register write, then perform the write again. Data in the FMU might have been corrupted.

### FMU reset

Reset the FMU. Ideally the FMU Q-Channel must be quiesced before reset is applied. If resetting while not in the QSTOPPED state, then it violates the Q-Channel protocol, so an unexpected response might be logged in the FMU when exiting reset.

### Full reset

Software initiates the quiesce procedure and then resets the MHU-320AE. If the MHU-320AE fails to respond to the powerdown sequence, then a full system reset is required.

### LPD error recovery

The LPD recovery sequence depends on whether the error type as follows:

LPD Q-Channel error PROTID
:   This error requires a full reset.

LPD unprotected Q-Channel error PROTID
:   This error requires an MHU reset.

Unprotected devices are AXI5-Stream interconnect components within the MHU top-level and a fault here is contained within the MHU.

### Q-Channel error recovery

The MHU-320AE does not need to be reset after a Q-Channel error because corrupt transitions on the qreqn signal are contained by the Q-Channel protection logic. In the event of a qreqn signal fault, the MHU-320AE does not change its state. If in QSTOPPED, the MHU-320AE remains there and a full reset is necessary.

If the Q-Channel error is persistent, steps should be taken to ensure that the clock that the Q-Channel controls continues to run, if necessary, by keeping it running at all times.

### RAM error recovery

For SECD RAM errors, no recovery procedure is required. For SECA and DED RAM errors, a recovery procedure is required. The recovery procedure is different for each type of RAM, see the following procedures:

- [Doorbell channel error recovery procedure](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/Doorbell-channels/Doorbell-channel-error-recovery-procedure?lang=en "If an uncorrectable doorbell channel error occurs, then the data being transferred in this channel is lost together with the channel configuration information.")
- [Fast channel error recovery procedure](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/Fast-channels/Fast-channel-error-recovery-procedure?lang=en "If an uncorrectable fast channel error occurs, then the data being transferred in this channel is lost together with the channel configuration information.")
- [FIFO channel error recovery procedure](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/FIFO-channels/FIFO-channel-error-recovery-procedure?lang=en "If an uncorrectable FIFO channel error occurs, then the data being transferred in this channel may have been corrupted and a recovery sequence needs to be performed by software to bring the FIFO channel back to a known state.")

Some RAM errors are lossy and the system integrator must determine the system recovery behavior for each RAM type. RAM error reports are also duplicated in the corresponding SRAS or RRAS address space.

### Reset error recovery

Reset errors are contained within reset protection, so no recovery procedure is required.

### Wire-only error reported recovery

When reading FMU\_ERR<>STATUS, if V=1 and W=1 but PROTID=0 (IERR=0) is observed, software should continue to read FMU\_ERR<n>STATUS until either PROTID is not 0 or a timeout is reached. The timeout should be determined by the maximum AXI5-Stream fabric packet delay. If a timeout occurs, then either there is a fault with being able to receive packets from MHU-320AE blocks or there is a fault with the error wire and so the W bit reporting.

To determine if packets can be received properly, access FMU\_ERRUPDATE to cause all errors to be resent for that error record. If this fails to complete normally, then perform a MHU-320AE reset recovery. If FMU\_ERRUPDATE completes normally but PROTID is still 0, then there could be a fault on the error wires which set the W bit. The error wires can be disabled by clearing FMU\_ERR<n>CTLR.W\_EN. Operation can continue but without the error reporting redundancy provided by the error wires and the FMU\_ERR<n>STATUS.W bit.
