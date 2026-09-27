# NPU<m> registers

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/NPU-m--registers>

### NPU<m> registers

CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm® Ethos™-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.

All NPUs reside in the PD\_NPU<m> power domain and are reset by nWARMRESETNPU<m>.
