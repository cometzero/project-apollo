# ACC_WAIT Control

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/System-interconnect-infrastructure/ACC-WAIT-Control>

### ACC\_WAIT Control

CRSAS Ma1 provides a set of controls to let you add access control gates or block access to the system expansion interfaces.

These controls let you:

- Add access control gates, driven using the ACCWAITn signal
- Block access to the system, when the system:

  - Leaves HIBERNATION{0-1} state
  - Resets
  - Performs first power up
  - When software wants to reconfigure security settings in the system

  These controls prevent access to the system until all security-related features of the system have been set up correctly.

  After software is ready, it can release the gates by writing to the BUSWAIT.ACC\_WAITN register. Then software can check the current status of all external gating units by reading the ACCWAITNSTATUS signal value through the BUSWAIT.ACC\_WAITN\_STATUS register.
