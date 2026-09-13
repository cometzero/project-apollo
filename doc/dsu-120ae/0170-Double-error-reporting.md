# Double error reporting

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Error-detection-and-reporting/Double-error-reporting>

### Double error reporting

If the DSU-120AE detects an Error Correcting Code (ECC) error in the L3 data RAM, the DSU-120AE performs a two-stage sequence that typically causes it to report two errors in the Error Record registers, even though there was only one original error.

This occurs because when the DSU-120AE detects an error in the L3 data RAM, the DSU-120AE reports the error in the Error Record registers and moves the data to the Long-Term Data Buffer (LTDB) RAM without correcting it. The LTDB RAM then reads the data and corrects it. When this occurs, the DSU-120AE reports a second error in the Error Record registers. Therefore, an ECC error in the L3 Data RAM is reported as if two errors occurred.

An error on a single read of the L3 data RAM results in the following error record contents, assuming the Error Record was initially empty:

- A 1-bit error increments the ERR0MISC0.CECO due to the reporting of a second Correctable Error. The contents of the ERR0STATUS accurately shows that the error came from the L3 Data RAM. For example, ERR0STATUS.SERR=6, ERR0STATUS.V=1 and ERR0STATUS.CE=1.
- A 2-bit error might be Deferred or Uncontainable depending on whether the target of the data supports poison. This is determined during the LTDB RAM read. The L3 data RAM always generates a Deferred Error, if there is a 2-bit error.

  Depending on if the error is Deferred or Uncontainable, the Error Record is updated as follows:

  - For a Deferred error, the contents of the Error Record accurately shows the error that came from the L3 data RAM. For example, ERR0STATUS.V=1, ERR0STATUS.DE=1 and ERR0STATUS.SERR=6. However, the extra error from the LTDB RAM also sets ERR0STATUS.OF=1.
  - For an Uncontainable error, the contents of the Error Record shows the LTDB RAM error. However, it does not provide details of the original L3 data RAM error. For example, ERR0STATUS.V=1, ERR0STATUS.UE=1, ERR0STATUS.SERR=2. The extra error also means that ERR0STATUS.OF=1. Also even though L3 data RAM poisoned the data, ERR0STATUS.PN=0.
