# 04.2 QemuInstance와 SystemC/QOM object 생성

> **학습 목표:** 4개 firmware domain·5개 QemuInstance와 elaboration, realize, reset release의 차이를 설명한다.
> Source 기준: 2026-10-25 checkout. 이 장의 작성·분할 검증에서는 build와 runtime을 실행하지 않았다.

[상위 장](../04-qbox-runtime-and-lua.md) · [전체 목차](../README.md) · [이전: Launcher와 runtime](01-launcher-runtime.md) · [다음: Lua composition과 reset](03-lua-composition.md)

## 이 장이 다루는 생성의 단위

![Runtime의 host 실행기와 firmware domain](../diagrams/04-qbox-runtime.drawio.svg)

[draw.io 편집 원본](../diagrams/04-qbox-runtime.drawio) · [기존 HTML 보기](../diagrams/04-qbox-runtime.html)

이 그림의 domain box는 firmware 역할을 나타낸다.
그 box가 SystemC object와 libqemu instance로 바뀌는 과정을 아래에서 추적한다.
Lua table 생성, C++ module constructor, QOM realize, CPU 실행 시작은 각각 다른 단계다.

## 한 process 안의 execution domain

| Firmware domain | 실행 CPU | QemuInstance의 공개 경로 | 기본 TCG mode |
|---|---|---|---|
| AP | Cortex-A720AE, full runner 기본 4 PE | `platform.ap_qemu_inst` | `MULTI` |
| SI CL0 | Cortex-R82, 1 PE | `platform.si_cl0_qemu_inst` | `MULTI` |
| SI CL1 | Cortex-R82, 4 PE | `platform.si_cl1_qemu_inst` | `MULTI` |
| RSE CPU | Cortex-M55, 1 PE | `platform.rse_cpu_pass.qemu_inst` | `SINGLE` |
| RSE peripheral helper | CPU domain 추가가 아닌 device 지원 | `platform.qemu_inst` | `SINGLE` |

기본 full-system은 **4개 firmware domain, 5개 QemuInstance**다.
각 QemuInstance는 한 `platforms-vp` process 안에서 독립 QEMU 상태를 보유한다.
CPU 수·QemuInstance 수·host process 수·host thread 수는 서로 다른 단위다.
외부 vMCU를 켜면 별도의 backend/process가 추가될 수 있다.

### QEMU machine을 실행하는 대신 QOM object를 조립한다

QemuInstance는 기본적으로 `-M none -m 0`으로 초기화한다.
즉 QEMU의 완성된 machine에 모든 구성을 맡기지 않고,
QBox의 CPU/device wrapper가 QOM object를 만들고 property를 설정한 뒤 realize한다.
`gs_memory`와 router 같은 SystemC module이 memory topology를 제공한다.

| 층 | 생성·실행 단위 | 이 층에서 연결하는 것 |
|---|---|---|
| Lua/CCI | `moduletype`, `args`, parameter preset | model 선택, constructor 참조, socket 이름 |
| ModuleFactory | SystemC module object | TLM socket, signal socket, 하위 container |
| QEMU wrapper | QOM object와 `MemoryRegion` | CPU/device property, GPIO, memory callback |
| libqemu | instance별 QEMU 상태·API | I/O thread, virtual clock, TCG CPU 실행 |

RSE는 CPU-local M55/NVIC와 주변장치 helper를 나누어 배치한다.
`rse_cpu_pass` container와 `LocalPass`는 두 영역의 TLM/IRQ 연결을 전달한다.
따라서 host-side `platform.qemu_inst`에는 추가 RSE firmware CPU가 없다.
이 경계는 RSE local crypto/flash backend를 선택할 때도 중요하다.

### Host thread와 SystemC process

AP/SI의 `MULTI`는 vCPU별 host thread를 사용한다.
RSE의 `SINGLE`은 해당 instance의 CPU들을 하나의 QEMU CPU thread에서 순환 실행하는 방식이다.
별도로 QEMU I/O thread와 SystemC kernel을 진행시키는 host thread가 있다.
SystemC의 `SC_THREAD`는 kernel이 scheduling하는 process이며, 선언할 때마다 OS thread가 생기지 않는다.

일반 MMIO에서 CPU thread는 BQL을 내려놓고 SystemC 작업을 요청한 뒤 완료를 기다린다.
SystemC thread가 router/target의 `b_transport()`를 호출하고,
응답 뒤 CPU thread가 BQL을 다시 잡아 guest 실행을 이어 간다.
**병렬 TCG 실행과 shared device register 처리는 같은 scheduling 단계가 아니다.**

근거: [QemuInstance 초기화·QK 소유](../../../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h),
[ModuleFactory Container](../../../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h),
[QEMU initiator](../../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h),
[RSE interconnect/LocalPass](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua).

현재 `local.conf`의 AP 설정은 4 PE다. Lua/runner는 1~16 PE를 받지만,
현재 Yocto `APOLLO_QVP_DTB` 선택은 4/16 PE 두 variant를 명시한다.
임의의 `--cpus` 값만 바꾼 구성을 배포 image가 지원한다고 가정하지 않는다.

근거: [RSE instance 생성](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua),
[RSE 실행 정책](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/qemu.lua),
[CL0](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua),
[CL1](../../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua),
[QVP machine](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf).

## Lua descriptor가 실제 object가 되는 과정

QBox의 `sc_main()`은 CCI broker를 만든 뒤 `ArgParser`로 Lua와 command-line preset을 읽고,
`GreenSocsPlatform("platform")`을 생성한다. 이 class가 ModuleFactory `Container`이므로
최종 Lua table의 `moduletype`, `args`, `bind`가 SystemC object graph로 변환된다.
마지막 `sc_start()`가 elaboration callback을 거쳐 simulation을 진행시킨다.

| 순서 | 실제 owner / 함수 | 생성 또는 연결되는 것 |
|---|---|---|
| 1 | `sc_main()` / `ArgParser` | CCI preset와 top-level `platform` |
| 2 | `ContainerBase::PriorityConstruct()` | priority·constructor dependency를 고려한 module 순서 |
| 3 | `get_module_args()` → `construct_module()` | `&object` 참조를 해석한 C++ module instance |
| 4 | `ModulesConstruct()`의 `name_bind()` | TLM, signal, biflow 등 타입에 맞는 socket 연결 |
| 5 | `QemuDevice::before_end_of_elaboration()` | `instantiate()` → instance 안의 QOM object |
| 6 | `QemuDevice::end_of_elaboration()` | `realize()` → `realized=true`, device 활성 구성 |
| 7 | `QemuInstance::start_of_simulation()` | `finish_qemu_init()`, runtime 진입 준비 |
| 8 | `QemuCpu::start_of_simulation()` | 초기 reset hold와 time-sync 상태 적용 |

이 표의 5~8은 SystemC lifecycle 단계다.
동일 callback 단계의 sibling module들이 table의 위아래 순서대로 호출된다고 가정하지 않는다.
특정 dependency가 필요한 부분은 factory dependency나 명시적인 callback/binding으로 표현해야 한다.

### Constructor dependency와 socket binding은 다르다

`args = {"&platform.ap_qemu_inst"}`는 CPU wrapper constructor에 전달할 QemuInstance 참조다.
그 object가 준비되어야 CPU wrapper를 만들 수 있다.
반면 `mem.bind`는 이미 생성될 socket의 상대편을 지정한다.
`ModulesConstruct()`는 module을 만든 뒤 `name_bind()`를 호출한다.

`get_module_args()`는 `&`로 시작하는 문자열을 object reference로 처리하고,
상대 이름이면 container scope에 맞는 parent prefix를 붙인다.
그래서 Lua의 `&ap_qemu_inst`와 실제 `platform.ap_qemu_inst` 사이에는 이름 해석 규칙이 있다.
파일을 다른 폴더로 옮긴 것만으로 CCI object scope가 바뀌는 것은 아니다.

`PriorityConstruct()`는 construction priority별로 의존성을 해결한다.
진행이 막히면 binding dependency 제약을 완화하여 재시도하지만,
constructor object를 찾지 못하는 경우까지 조용히 무시하지 않는다.
`Unresolvable module dependencies`와 `Missing dependency`가 나오면
CPU instruction 실행 이전의 object graph 문제다.

근거: [QBox main](../../../../hsoc-stack/tools/qbox/platforms/src/main.cc),
[ModuleFactory 구현 header](../../../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h)
`PriorityConstruct`, `ModulesConstruct`, `get_module_args`, `name_bind`.
`module_factory_container.cc`는 module 등록 translation unit이며 이 생성 로직의 본문은 header에 있다.

## QOM 생성과 CPU release 사이

`QemuDevice` constructor는 QemuInstance reference와 QOM type을 보관한다.
이때 guest device가 완성되는 것은 아니다.
`instantiate()`가 `object_new()`를 호출한 뒤 concrete wrapper가 property를 설정하고,
`realize()`가 실행 가능한 QEMU device로 확정한다.

CPU wrapper는 `before_end_of_elaboration()`에서 CPU handle을 얻고
request context를 memory socket에 설정한다. 이어 `socket.init(m_dev, "memory")`로
QEMU memory interface를 QBox initiator에 연결하고 CPU를 soft-stopped 상태로 둔다.
그 뒤 time-sync callback, reset state, runtime release 조건이 결합된다.

| 상태 | 의미 | 여기서 보장하지 않는 것 |
|---|---|---|
| SystemC module 존재 | wrapper constructor 완료 | QOM realize 또는 CPU 실행 |
| QOM object 존재 | `object_new()` 완료, property 설정 가능 | reset 해제 |
| Realized device | QEMU device 구성 완료 | firmware image 준비 또는 boot 성공 |
| Start in reset | CPU/model이 초기 hold 상태 | PPU ON 이전의 instruction 실행 |
| Firmware release | reset adapter·PPU의 해제 조건 충족 | 이후 firmware의 인증·driver 동작 성공 |

`QemuInstance::get()`은 필요한 시점에 instance를 initialize할 수 있다.
`before_end_of_elaboration()`도 아직 initialize되지 않았으면 `init()`을 호출한다.
따라서 “Lua에서 instance를 선언한 순간 libqemu boot가 끝난다”는 설명은 맞지 않는다.

근거: [QemuDevice lifecycle](../../../../hsoc-stack/tools/qbox/qemu-components/common/include/device.h),
[QemuCpu 초기화·request context·reset](../../../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h),
[QemuInstance lifecycle](../../../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h).

## 실행 policy의 조합 제약과 진단

QemuInstance core의 기본 `sync_policy`는 `multithread-quantum`이다.
Apollo VP와 full runner가 선택하는 `multithread-freerunning`은 별도 override다.
Core constructor default, VP descriptor default, 실행 manifest의 effective value를 분리해야 한다.

| 조합 또는 증상 | 현재 source 계약 | 진단 방향 |
|---|---|---|
| `MULTI` + `icount` | `push_icount_mode_args()` / `push_tcg_mode_args()`에서 거부 | TCG threading과 시간 전략 입력 확인 |
| SystemC-thread QK | `init()`이 `COROUTINE` 실행 조건을 적용 | QK thread type과 TCG mode 일치 확인 |
| `COROUTINE` + 다른 QK type | unsupported 조합을 fatal로 처리 | 임의 mode 혼합 대신 profile policy 확인 |
| unknown `moduletype` | 등록 factory 또는 dynamic library 필요 | provider library와 factory 등록 확인 |
| IRQ 연결 직후 instance lock 문제 | target signal wrapper가 대상 instance의 lock 소유 | CPU와 device의 QemuInstance 참조 확인 |
| CPU object는 있으나 실행하지 않음 | `start_in_reset`, external hold, PPU 상태가 남을 수 있음 | [Lua/reset 장](../04-qbox/03-lua-composition.md)에서 release owner 추적 |

QemuInstance 다섯 개는 “다섯 개의 SystemC kernel”을 뜻하지 않는다.
각 libqemu의 CPU/I/O 실행은 공통 SystemC model graph에 transaction과 signal로 들어온다.
이 경계에서 lock, callback context, reset state를 읽는 것이
process 이름이나 thread 개수만 세는 것보다 실행 구조를 잘 설명한다.

---

[상위 장](../04-qbox-runtime-and-lua.md) · [전체 목차](../README.md) · [이전: Launcher와 runtime](01-launcher-runtime.md) · [다음: Lua composition과 reset](03-lua-composition.md)
