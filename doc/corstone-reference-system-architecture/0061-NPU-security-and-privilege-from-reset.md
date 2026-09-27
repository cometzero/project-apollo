# NPU security and privilege from reset

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Reset-infrastructure/NPU-Reset-handling/NPU-security-and-privilege-from-reset>

### NPU security and privilege from reset

When the NPU reset is released by the PPU controlling the NPU power domain PD\_NPU<m>, the NPU<m> sample the signals driven by NPUSPPORSL.SP\_NPU<m>PORSL to determine its default security level. And NPUSPPORPL.SP\_NPU<m>PORPL or NPUNSPORPL.NS\_NPU<m>PORPL to determine its default privilege level.

For more details, see [NPUSPPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/NPUSPPORPL?lang=en "The NPU Secure Access Privileged Level Reset Control Register allows software to configure if each NPU resets to privileged or unprivileged state. The value of this register is only sampled by the NPU, when the NPU is released from reset and NPUSPPORSL.SP_NPU<m>PORSL is Secure State. The default reset value of this register is controlled by NPU<m>PORPLRST:") and [NPUNSPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en "The NPU power on reset Non-secure access privileged level reset control registers allow software to configure if each NPU resets to privileged or unprivileged state.").

For information on how the NPU is expected to transition between security and privilege levels, see [NPU security mapping](/documentation/102803/0000/Functional-Description/NPU/NPU-security-mapping?lang=en "The NPU is capable of operating in different security modes. To change from operating in one security world to another, a reset is required.").
