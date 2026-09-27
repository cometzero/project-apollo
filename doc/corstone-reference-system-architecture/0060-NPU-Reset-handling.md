# NPU Reset handling

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Reset-infrastructure/NPU-Reset-handling>

### NPU Reset handling

If NUMNPU > 0, each nRESET input of the NPUs is driven by the PPU that controls the NPU power domain PD\_NPU<m> and the Warm reset is driven from Warm Reset Generation logic that resides in the PD\_AON domain. This, along with all PPUs in the system, is used to force the system to idle before driving Warm reset. The PPU itself is reset using nCOLDRESETMGMT.

- **[NPU security and privilege from reset](/documentation/102803/0000/Functional-Description/Reset-infrastructure/NPU-Reset-handling/NPU-security-and-privilege-from-reset?lang=en)**
   When the NPU reset is released by the PPU controlling the NPU power domain PD\_NPU<m>, the NPU<m> sample the signals driven by NPUSPPORSL.SP\_NPU<m>PORSL to determine its default security level. And NPUSPPORPL.SP\_NPU<m>PORPL or NPUNSPORPL.NS\_NPU<m>PORPL to determine its default privilege level.
