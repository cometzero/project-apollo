# 03.5 Runtime artifact handoff와 실패 진단

[상위 장](../03-project-build-architecture.md) · [← 이전](04-os-image-and-storage.md) · [다음 →](../04-qbox-runtime-and-lua.md)

> 목적: deploy image·native provider·launch metadata를 실제 실행 입력으로 묶고 변경 전파를 검증한다.
> 기준: 2026-10-25 checkout의 source·metadata 정적 추적. 새 BitBake 실행이나 runtime 검증 결과를 의미하지 않는다.

## 1. Build에서 runtime으로 넘기는 interface

`qboxboot.bbclass`는 `do_image` 이후, `do_image_complete` 이전에 JSON `.qboxconf`를 생성한다.
이 task는 provider의 `do_populate_sysroot`에 의존한다. `.qboxconf`는 **실행 조합의 기술서**이며 모든 파일을 담은 portable bundle은 아니다.

| `.qboxconf` 필드 | 예시 / 역할 |
|---|---|
| `provider` / `sysroot` | Host 실행 파일·library·module·data의 실제 경로 |
| `exe` | `platforms-vp` |
| `config` | `platforms/apollo/apollo-qvp-saturn-v.lua` |
| `images` | WIC, ROM/OTP/Flash, SI image의 deploy 상대 경로 |
| `env` | `QBOX_APOLLO_NUM_CPUS=${PC_CPUS_COUNT}` 등 |

근거: [qboxboot.bbclass](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass)의 `qboxboot_provider_dep`·`do_write_qboxboot_conf`, [image 공통 include](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc), [native provider](../../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb).

### Deploy와 sysroot를 구분해야 실행물을 찾을 수 있다

| 위치: `build/tmp_baremetal/` 아래 | 무엇을 찾는가 | 소비 시점 |
|---|---|---|
| `deploy/images/apollo-qvp/` | ROM/Flash/OTP, Image/DTB, WIC/UKI, `.qboxconf` | Guest boot와 launcher input |
| `sysroots-components/<host-arch>/qbox-apollo-qvp-native/` | `platforms-vp`, model `.so`, installed Lua | Host process 실행 |
| `sysroots-components/<host-arch>/qbox-libqemu-native/` | Host libqemu/header/CMake package | Provider build와 runtime library 연결 |
| `work/.../recipe-sysroot-native/` | 해당 recipe의 host dependency 집합 | Build tool 실행, 일부 runtime library resolution |
| `work/.../build/`·`temp/` | ELF, generated config, task log | Loader 보조 입력·debug·원인 분석 |

`run_qbox_yocto.sh`는 `.qboxconf`의 provider path를 읽어 executable·module·Lua 위치를 결정한다.
따라서 source checkout의 Lua를 바꾼 뒤 WIC만 복사하면 설치된 Lua는 그대로일 수 있다. Provider install/sysroot와 `.qboxconf`의 연결을 확인해야 한다.
반대로 firmware만 바꾼 경우에도 RSE Flash뿐 아니라 SI loader의 개별 bin/ELF가 갱신됐는지 확인한다.

### Build task가 runtime을 실행하는 것은 아니다

`do_write_qboxboot_conf`는 실행 정보를 JSON으로 기록한다. 그 자체가 QBox boot나 post-login probe를 수행하지 않는다.
실제 handoff는 아래처럼 이어진다.

```text
BitBake image/provider tasks
  → deploy artifacts + native provider + .qboxconf
  → run_qbox_yocto.sh: artifact/provider 선택
  → canonical full runner: preflight와 runtime child
  → platforms-vp: installed Lua와 CCI parameter로 model 구성
  → domain firmware boot → U-Boot/UKI → Linux
```

현재 image include의 `do_build[depends]`에는 `ukiboot`와 vMCU companion 산출물도 연결된다.
이들은 AP product rootfs에 모두 설치되는 package라는 뜻이 아니라, workspace 실행 workflow가 필요로 하는 별도 deploy input이다.
이 구분이 있어야 “build target 완료”와 “어떤 domain·companion이 실제로 실행됐는가”를 분리해 설명할 수 있다.


## 2. `.qboxconf` 생성은 실행 계약을 고정하는 task다

[qboxboot.bbclass](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass)는 `QBOX_PROVIDER`, `QBOX_EXE`, `QBOX_CONFIG` 중 하나라도 설정되면 contract 생성을 활성화한다. 활성화된 경우 provider와 모든 필수 path가 있어야 한다.

| 구현 | 검사 / 기록 | 왜 필요한가? |
|---|---|---|
| `qboxboot_provider_dep()` | Provider `do_populate_sysroot` dependency | Native 실행 layout이 먼저 준비되어야 함 |
| `qboxboot_vars()` | `QBOX_*`와 주요 build variable을 task dependency로 수집 | Machine/image/provider 선택 변화 추적 |
| `safe_relative()` | Executable/config/image entry의 absolute path와 `..` 거부 | Base directory와 relative entry 계약 유지 |
| `get_flags("QBOX_IMAGES")` | Varflag별 artifact filename | ROM/Flash/DTB/WIC 등을 이름으로 연결 |
| `QBOX_ENV_PASSTHROUGH` | CPU count 등 필요한 environment | Build topology를 runtime에 전달 |
| `IMAGE_NAME` / `IMAGE_LINK_NAME` | Versioned JSON과 안정적 symlink | Artifact identity와 편리한 선택을 함께 제공 |

`do_write_qboxboot_conf`는 경로와 schema를 만들지만 파일의 boot 가능성까지 검증하지 않는다. Versioned filename과 stable symlink가 무엇을 가리키는지, provider의 source revision이 무엇인지 실행 기록에서 다시 확인한다.

### Launcher가 contract를 해석하는 순서

[run_qbox_yocto.sh](../../../../run_qbox_yocto.sh)의 `read_qboxconf_shell_assignments()` 안 Python은 JSON object/string, safe relative entry, provider/sysroot path를 검증한 뒤 shell assignment를 생성한다.

1. `validate_trusted_paths()`는 선택한 Yocto build의 `tmp_baremetal/sysroots-components`와 `work` 기준으로 provider 및 native sysroot를 검증한다.
2. `provider.bindir + exe`, `provider.data_dir + config`로 executable과 installed Lua를 찾는다.
3. `image_path()`는 `.qboxconf` directory를 기준으로 image 상대 경로를 계산한다. Provider path 검증과 image path 해석은 다른 규칙이다.
4. Shell의 `resolve_file*()`이 명시 override, `.qboxconf`, deploy/default 후보 중 실제 파일을 고른다.
5. Canonical runner에 이 경로를 전달하고 runtime child가 model process를 시작한다.

따라서 `.qboxconf`를 다른 directory로 복사해도 native provider absolute path가 자동으로 재배치되는 것은 아니다. 실행 조합을 옮기려면 deploy file뿐 아니라 provider layout과 library dependency를 함께 다뤄야 한다.

## 3. SI1 ELF와 bin은 한 쌍의 runtime 입력이다

[run_qbox_apollo_fvp_full.py](../../../../scripts/run/run_qbox_apollo_fvp_full.py)의 `si_cl1_boot_config()`는 SI1 reset vector를 파일명에서 추정하지 않고 **선택한 ELF의 `e_entry`**에서 읽는다. 개별 ELF와 bin을 섞어 복사하는 문제를 boot 전에 좁히기 위한 검사다.

| 검사 | 실제 조건의 의미 | 실패하면 의심할 입력 |
|---|---|---|
| ELF header | ELF64 little-endian, AArch64 executable | 다른 architecture/format의 ELF |
| Entry / load range | SI1 SRAM `0x140000000..0x140800000` 내부, alignment | Standalone/integrated image 또는 linker map |
| PT_LOAD | Bounds와 identity virtual/physical address | 잘못된 segment layout |
| Allocated section bytes | ELF section과 bin의 해당 bytes 비교 | 서로 다른 build의 ELF/bin |
| `.image_crc` | Binary 후처리 CRC 예외를 별도 검증 | CRC patch 결과 또는 잘못된 binary |
| RVBAR | 기본은 ELF entry, explicit 값도 range 검사 | 임의 entry override |

ELF segment padding과 `objcopy` gap bytes는 같지 않을 수 있어 모든 padding을 비교하지 않고 allocated file-backed section을 비교한다. `.image_crc`는 post-build patch 결과이므로 별도 계산한다. 이 preflight의 PASS는 입력 쌍의 일관성이지 Zephyr application이나 HIPC의 runtime PASS가 아니다.

`prepare_si_cl1_boot()`는 오류를 `si_cl1_boot_invalid:...`로 보고하고, build-only에서는 SKIP한다. 진단에서는 이 최초 blocker를 해결한 뒤 CPU/IRQ/application 분석으로 진행한다.

## 4. Artifact가 준비됐어도 qualification은 별도 실행이다

현재 root shell launcher는 `--no-post-login-probe`를 전달하는 boot/login 경로다. Headless 옵션도 이 정책을 바꾸지 않는다. Full post-login service 검증은 canonical Python runner의 해당 profile과 log/report를 기준으로 한다.

| 증거 | 확인되는 것 | 이어서 필요한 증거 |
|---|---|---|
| Recipe compile/install 성공 | Build output와 install contract | 실제 선택 provider/image identity |
| `.qboxconf` 존재 | Launch metadata 생성 | Paths/bytes 및 runtime preflight |
| SI1 ELF/bin preflight PASS | Entry와 input pair의 형식·내용 일치 | CL1 실제 boot와 서비스 동작 |
| Linux login marker | Boot/login path 도달 | Driver traffic, IRQ, HIPC/SCMI, error/reset path |
| Profile 결과와 marker/log | 실행한 scope의 관측 | 다른 profile과 FVP/hardware parity는 별도 |

## 5. 증상에서 가장 가까운 artifact 경계로 돌아간다

| 증상 | 첫 확인 | 다음 source |
|---|---|---|
| Executable/shared library 오류 | Provider paths, library layout, loader output | Native recipe `do_install`과 qboxconf parser |
| Model type/Lua 오류 | Installed Lua와 required `.so` | Provider install → overlay CMake/Lua |
| SI1 preflight 차단 | 실제 선택 ELF/bin hash와 `e_entry` | `si_cl1_boot_config`, Zephyr linker/build |
| RSE 초기 boot 차단 | ROM/OTP/Flash와 provisioning state | Firmware/TF-M task 및 RSE log |
| U-Boot는 되나 Linux 변화가 없음 | Boot한 slot UKI/WIC identity | `do_uki`, WKS, boot selection |
| Login 후 service 실패 | 실행 profile과 domain별 최초 실패 marker | 해당 firmware/client/model contract |

진단 기록에는 command, config snapshot, 선택 artifact의 resolved path/hash, provider/installed Lua, 최초 blocker를 함께 둔다. Rebuild 여부는 이 경계에서 결정한다. 예를 들어 stale installed Lua는 kernel 재빌드로 해결되지 않고, old UKI는 model 재빌드로 바뀌지 않는다.

## 6. 변경 후 어디까지 다시 만들어야 하는가

### End-to-end 사례: Linux DTB와 driver를 변경했다면

1. Local Linux source의 driver/DTS를 수정하고 Apollo defconfig가 driver를 선택하는지 확인한다.
2. `linux-yocto-rt`의 Apollo include가 해당 source/defconfig/DTB를 선택한다. Kernel task 결과는 Image·DTB와 modules다.
3. Product/BSP package 구성에 modules가 들어가고, UKI가 새 Image/DTB/initramfs를 포함한다.
4. WIC의 ESP에 새 UKI가, 필요한 rootfs/initramfs에 같은 kernel용 modules가 들어간다.
5. `.qboxconf`가 가리키는 WIC로 boot한 뒤 Linux의 DT와 driver가 새 device를 인식하고 실제 MMIO/IRQ traffic을 처리하는지 확인한다.

이 경우 `-c compile virtual/kernel`만 성공해도 마지막 단계까지 전파된 것은 아니다.
특히 full-system boot에서 deploy의 `Image` 파일을 따로 발견했다는 사실보다 **WIC 안 UKI가 어떤 kernel/DTB를 포함했는지**가 중요하다.

### End-to-end 사례: SCP module을 변경했다면

SCP source→`si0_ramfw.bin`→signed SI0 payload→RSE Flash와 loader input이 연결된다.
Product module list와 `config_*.c`에서 새 module이 포함되는지 먼저 확인하고, firmware assembly 후 새 run의 CL0 log와 해당 SCMI/IRQ 동작을 확인한다.
AP Linux image를 재사용할 수 있는 변경인지 여부는 SCMI ABI·channel·shared memory 계약이 바뀌었는지에 따라 달라진다.
Firmware와 consumer ABI가 함께 바뀌었다면 두 artifact를 같은 실행 조합으로 전달해야 한다.

| 변경한 것 | 연결해서 갱신/확인할 것 | 실행 시 마지막 확인 |
|---|---|---|
| Linux/DTS | Kernel/DTB/modules → UKI/rootfs/initramfs → WIC | Boot한 UKI, DTB와 modules가 같은 조합인가? |
| U-Boot/OP-TEE/SP | Component → TF-A FIP → AP Flash | 실제 선택된 Flash가 새 artifact인가? |
| TF-M/SCP/CL1 | Firmware assembly + 개별 loader input | OTP/state와 binary/ELF가 호환되는가? |
| QBox model/Lua | Native compile/install/populate_sysroot | `.qboxconf`가 새 provider와 installed Lua를 가리키는가? |
| Product package/WKS | rootfs/initramfs/UKI/WIC | Package·partition·boot policy가 일치하는가? |

Build 완료는 dependency와 artifact 생성의 증거다. Guest에서 실제 driver traffic·IRQ·service를 관측해야 runtime 동작을 주장할 수 있다.
이 자료는 wrapper·recipe·class·설정의 정적 확인에 한정하며, sstate hit·최종 expanded datastore·새 image boot는 확인하지 않았다.

## 7. Source를 따라 다시 설명할 때의 출발점

| 교육용 질문 | 문서·구현 근거 |
|---|---|
| Reference는 왜 kas/Kconfig를 사용하는가? | [Reproduce / Kas build](../../../../arm-zena-css/documentation/user_guide/reproduce.rst), [Integration](../../../../arm-zena-css/documentation/design/integration.rst) |
| Apollo는 어떤 설정을 선택하는가? | [yocto_build.sh](../../../../yocto_build.sh), [QVP template](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/), [machine](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf) |
| Component가 어디서 build되는가? | [BSP source registry](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/layer.conf), component common/QVP include |
| 왜 여러 firmware를 하나의 Flash에 모으는가? | [Boot process / RSE-oriented boot flow·Images layout](../../../../arm-zena-css/documentation/design/boot_process.rst), `firmware.cfg` |
| Product rootfs와 UKI는 어떻게 묶이는가? | `nexios-initramfs-image.bb`, `auto-ad-nexios-uki-ab.bbclass`, QVP WKS |
| Build 결과가 QBox에 어떻게 전달되는가? | `qboxboot.bbclass`의 JSON schema, native provider install, [launcher](../../../../run_qbox_yocto.sh) |

## 다음 읽기

[04. QBox 실행 구조와 Lua](../04-qbox-runtime-and-lua.md)에서 runner가 전달한 artifact/parameter를 SystemC/QEMU instance와 domain fabric에 연결한다.

[상위 장](../03-project-build-architecture.md) · [← 이전](04-os-image-and-storage.md) · [다음 →](../04-qbox-runtime-and-lua.md)
