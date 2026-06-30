# Uncorrectable MHU Receiver error record 1 in MHU Sender

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Receiver-error-record-1-in-MHU-Sender>

### Uncorrectable MHU Receiver error record 1 in MHU Sender

Error record 1 in the MHU Sender contains uncorrectable RAM errors that have been observed in the MHU Receiver. You can use this error record to let the MHU Sender software know that a particular channel has been corrupted, even if the corruption is not local, in case the MHU Sender software needs to take action. You can obtain the channel type and number information from SRAS\_ERR1MISC0 register.
