# Uncorrectable MHU Sender error record 1 in MHU Receiver

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Sender-error-record-1-in-MHU-Receiver>

### Uncorrectable MHU Sender error record 1 in MHU Receiver

Error record 1 in the MHU Receiver contains uncorrectable RAM errors that have been observed in the MHU Sender. The aim of this error record is to let the MHU Receiver software know that a particular channel has been corrupted in case it needs to take action, even if the corruption is not local. The channel type and number information can be obtained from RRAS\_ERR1MISC0.
