# MBIST data save and restore

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/MBIST-data-save-and-restore>

### MBIST data save and restore

The system integrator must ensure that the MBIST controller checks the MBIST read data integrity, if the controller uses that data to restore memory state.

This means that the integrity of the data must be guaranteed during its capture and storage, avoiding all single points of failure and written back to the GIC from independent sources that again avoid single points of failure.

It is the system integrators responsibility to decide how to achieve this data integrity. One approach could be to capture the mbistoutdata and mbistoutdata\_chk signals and store them independently in two separate memories. When restoring the RAM data, the two memories would then be used to drive data onto the mbistindata and mbistindata\_chk signals independently. Any inconsistencies between mbistindata and mbistindata\_chk would be detected by the GIC within MBIST protection.
