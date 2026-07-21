# Arm Zena CSS FVP Iris 디버깅 가이드

작성일: 2026-07-21

대상: 로컬 빌드 `apollo-fvp`와 `FVP_Zena_CSS_Cfg2`

기본 Iris endpoint: `localhost:7100`

## 1. 이 workspace에 이미 있는 도구

요청한 Iris 실행 및 breakpoint script는 이미 `scripts/debug/`에 구현되어 있다.
기존 도구가 필요한 흐름을 모두 제공하므로 같은 기능의 script를 새로 만들지
않고 다음 script를 공식 진입점으로 사용한다.

| Script | 역할 |
| --- | --- |
| `scripts/debug/run_local_fvp_debug.sh` | local FVP를 기본 halted 상태로 실행하고 Iris server를 열며, 선택적으로 symbolic breakpoint까지 자동 설치한다. |
| `scripts/debug/local_debug_iris.py` | `symbols.json`을 읽어 Iris target을 찾고 program breakpoint를 설치한 뒤 실행/정지/종료한다. |
| `scripts/setup/setup_local_debug_env.py` | unstripped ELF를 찾아 `symbols.json`과 component별 GDB command file을 생성한다. |
| `scripts/run/run_local_fvp_tmux.sh` | FVP process, UART log 및 tmux session을 관리하는 하위 실행기이다. |

`FVP_Zena_CSS_Cfg2`는 GDB remote stub 대신 Iris debug server를 제공한다. 따라서
live target 제어는 Iris 또는 Iris-capable debugger를 사용하고,
`gdb-multiarch`는 ELF symbol, source line 및 주소를 사전 확인하는 용도로
사용한다.

[Arm의 Iris 소개](https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/iris-the-new-debug-and-trace-interface-in-arm-models)는
Iris가 network connection과 Python API를 통해 simulation, debug 및 trace를
제어하는 interface임을 설명한다. 최신 Fast Models에서는 `--iris-server`를
사용해 server를 활성화한다.

## 2. 전체 흐름

```text
local component build
        |
        v
unstripped ELF + FVP config
        |
        v
setup_local_debug_env.py
        |
        +--> debug/symbols.json
        +--> debug/gdb/*.gdb
        |
        v
run_local_fvp_debug.sh
        |
        +--> FVP starts halted
        +--> Iris TCP server
        +--> UART/file logs and tmux session
        |
        v
local_debug_iris.py or Arm Development Studio
        |
        +--> target resolution
        +--> symbolic breakpoint
        +--> run / stop / inspect
```

기본 원칙은 FVP를 먼저 **halted** 상태로 시작한 뒤 breakpoint를 설치하고
실행하는 것이다. reset 직후 symbol을 잡아야 하는 TF-M BL1_1, SCP-firmware 및
TF-A BL2 디버깅에서는 `--run`으로 먼저 실행하면 breakpoint 설치 전에 해당
코드를 지나칠 수 있다.

## 3. 사전 조건

### 3.1 FVP용 local artifact 빌드

현재 active Yocto machine은 `apollo-qvp`이므로 FVP local build를 명시한다.

```bash
cd /build/arm/arm-auto-solutions
MACHINE=apollo-fvp ./local_build.sh build
```

최소 필수 산출물은 다음과 같다.

```bash
test -f build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf
test -d build/tmp_baremetal/sysroots-components/x86_64/\
fvp-rd-aspen-native/usr/lib/fvp/fvp-rd-aspen/Iris/Python
```

특정 component만 다시 빌드한 경우 마지막에 manifest를 갱신한다.

```bash
MACHINE=apollo-fvp ./local_build.sh debug-manifest
```

또는 generator를 직접 실행할 수 있다.

```bash
python3 scripts/setup/setup_local_debug_env.py \
  --local-build-dir build/local-apollo-fvp \
  --out-dir build/local-apollo-fvp/debug
```

### 3.2 manifest 완전성 확인

Generator는 없는 ELF를 오류로 종료하지 않고 `missing` 배열에 기록한다. 따라서
breakpoint 실행 전에 반드시 확인한다.

```bash
jq '.missing' build/local-apollo-fvp/debug/symbols.json
jq -r '.components | keys[]' \
  build/local-apollo-fvp/debug/symbols.json
```

원하는 component가 `components`에 없으면 그 component의 unstripped ELF를 먼저
빌드해야 한다. `missing`이 비어 있지 않더라도 디버깅하려는 component가
정상적으로 등록되어 있으면 해당 component 디버깅은 가능하다.

## 4. 가장 짧은 실행 방법

### 4.1 TF-M reset breakpoint까지 한 번에 실행

```bash
scripts/debug/run_local_fvp_debug.sh \
  --no-attach \
  --iris-port 7100 \
  --break tfm-bl1_1:Reset_Handler \
  --break-timeout 120
```

이 명령은 다음 작업을 자동 수행한다.

1. debug manifest 갱신
2. FVP를 halted 상태로 시작
3. Iris port가 열릴 때까지 대기
4. RSE CPU target에 `Reset_Handler` breakpoint 설치
5. model 실행
6. breakpoint hit 또는 timeout 결과 출력

부팅 후반의 U-Boot나 Linux symbol은 40~60초보다 오래 걸릴 수 있다. 이
workspace의 full-system boot 특성을 고려해 `--break-timeout 300` 이상을
사용하는 편이 안전하다.

### 4.2 대표 component 예제

```bash
# RSE TF-M
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break tfm-bl2:Reset_Handler --break-timeout 120

# Safety Island CL0 SCP-firmware
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break scp-si0:arch_exception_reset --break-timeout 180

# Safety Island CL1 Zephyr
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break si-cl1-zephyr:z_cstart --break-timeout 180

# Primary Compute TF-A
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break tfa-bl31:bl31_main --break-timeout 300

# U-Boot
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break u-boot:board_init_f --break-timeout 600

# Linux
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break linux:start_kernel --break-timeout 600
```

symbol을 생략하면 manifest에 기록된 component 기본 symbol을 사용한다.

```bash
scripts/debug/run_local_fvp_debug.sh --no-attach --break scp-si0
```

## 5. Server와 client를 분리해서 사용

반복적으로 target을 확인하거나 Arm Development Studio를 연결할 때는 server와
client를 분리한다.

### 5.1 FVP를 halted 상태로 시작

```bash
scripts/debug/run_local_fvp_debug.sh \
  --no-attach \
  --iris-port 7100 \
  --session apollo-fvp-iris
```

`--run`을 주지 않았으므로 model은 debugger 연결 전까지 정지 상태이다.

### 5.2 실행 가능한 Iris target 확인

```bash
scripts/debug/local_debug_iris.py \
  --port 7100 \
  --manifest build/local-apollo-fvp/debug/symbols.json \
  --list-targets
```

주요 target mapping은 다음과 같다.

| Component | Iris target |
| --- | --- |
| TF-M BL1_1, BL1_2, BL2, secure runtime | `RD_ASD.css.smb.rseil.rse.cpu` |
| SCP-firmware SI0 | `RD_ASD.css.smb.si.cluster0.cpu0` |
| Zephyr SI1 | `RD_ASD.css.smb.si.cluster1.cpu0` |
| TF-A, OP-TEE, U-Boot, Linux | `RD_ASD.css.app00.cluster.cpu0` |

### 5.3 breakpoint 설치 후 실행

```bash
scripts/debug/local_debug_iris.py \
  --port 7100 \
  --manifest build/local-apollo-fvp/debug/symbols.json \
  --break scp-si0:arch_exception_reset \
  --run \
  --timeout 300
```

여러 breakpoint를 한 번에 설치할 수도 있다. model은 먼저 발생한 breakpoint에서
정지한다.

```bash
scripts/debug/local_debug_iris.py \
  --port 7100 \
  --manifest build/local-apollo-fvp/debug/symbols.json \
  --break tfm-bl1_1:Reset_Handler \
  --break scp-si0:arch_exception_reset \
  --break tfa-bl2:bl2_main \
  --run \
  --timeout 300
```

정상 출력 예시는 다음 형식이다.

```text
breakpoint_set component=scp-si0 symbol=arch_exception_reset ...
running model with timeout=300.0s
breakpoint_hit component=scp-si0 symbol=arch_exception_reset ...
```

### 5.4 FVP 종료

```bash
scripts/debug/local_debug_iris.py \
  --port 7100 \
  --manifest build/local-apollo-fvp/debug/symbols.json \
  --shutdown
```

tmux session만 정리할 때는 먼저 session 이름을 확인하고 정확한 대상만 종료한다.

```bash
tmux list-sessions
tmux kill-session -t apollo-fvp-iris
```

## 6. GDB로 symbol과 source를 사전 확인

GDB command file은 live control용이 아니라 ELF의 symbol/address/source mapping을
검증하기 위한 것이다.

```bash
gdb-multiarch -x build/local-apollo-fvp/debug/gdb/u-boot.gdb
gdb-multiarch -x build/local-apollo-fvp/debug/gdb/linux.gdb
gdb-multiarch -x build/local-apollo-fvp/debug/gdb/scp-si0.gdb
```

GDB 안에서는 다음을 우선 확인한다.

```gdb
info address board_init_f
info line board_init_f
list board_init_f
```

`symbols.json`에는 U-Boot처럼 linked address와 runtime load address가 다른
component의 `load_offset`도 반영된다. breakpoint 주소가 의심되면 다음 항목을
함께 비교한다.

```bash
jq '.components["u-boot"] | {
  elf, linked_text_address, load_offset, text_address, symbols
}' build/local-apollo-fvp/debug/symbols.json
```

## 7. UART 및 실행 증거 확인

`run_local_fvp_debug.sh`는 하위 tmux runner를 사용하므로 일반 local FVP 실행과
같은 file-backed log를 남긴다. 명시적인 output directory가 필요하면 다음과
같이 실행한다.

```bash
scripts/debug/run_local_fvp_debug.sh \
  --no-attach \
  --iris-port 7100 \
  --out-dir build/local-apollo-fvp/iris-run/manual-01
```

확인 대상은 다음과 같다.

```text
build/local-apollo-fvp/iris-run/manual-01/fvp_stdout.log
build/local-apollo-fvp/iris-run/manual-01/ports.tsv
build/local-apollo-fvp/iris-run/manual-01/uarts/rse.log
build/local-apollo-fvp/iris-run/manual-01/uarts/safety_island_cl0.log
build/local-apollo-fvp/iris-run/manual-01/uarts/safety_island_cl1.log
build/local-apollo-fvp/iris-run/manual-01/uarts/tf_a.log
build/local-apollo-fvp/iris-run/manual-01/uarts/u_boot_linux.log
```

breakpoint hit만으로 전체 부팅 성공을 판정하지 않는다. boot validation은
`scripts/run/runfvp_log_boot.py`의 domain별 log/result를 사용하고, Iris는 log로
확인한 최초 실패 domain의 source-level 원인을 좁히는 데 사용한다.

## 8. Arm Development Studio 연결

Arm Development Studio를 사용할 때도 먼저 다음 명령으로 halted Iris server를
연다.

```bash
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100
```

그 다음 debugger에서 `localhost:7100` Iris model에 연결하고 위 표의 target을
선택한다. ELF는 `build/local-apollo-fvp/debug/symbols.json`의 해당 component
`elf` 경로를 사용한다. source 검색 경로는 같은 record의 `source_roots`를
사용한다.

CLI client와 GUI debugger가 동시에 model run control을 시도하지 않도록 한다.
한쪽은 target 목록이나 register read처럼 read-only로 사용하거나, control
owner를 명확히 정한다.

## 9. 문제 해결

### 9.1 `missing FVP config`

증상:

```text
build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf not found
```

해결:

```bash
MACHINE=apollo-fvp ./local_build.sh fvpconf
```

필요한 firmware와 image가 아직 없다면 전체 local build를 수행한다.

```bash
MACHINE=apollo-fvp ./local_build.sh build
```

### 9.2 `unknown component` 또는 symbol 없음

```bash
jq '.missing' build/local-apollo-fvp/debug/symbols.json
jq '.components | keys' build/local-apollo-fvp/debug/symbols.json
jq '.components["scp-si0"].symbols' \
  build/local-apollo-fvp/debug/symbols.json
```

해당 ELF가 없거나 필요한 symbol이 strip된 경우 component를 debug 설정으로
다시 빌드한다.

### 9.3 Iris Python path 없음

```bash
jq -r '.iris_python' build/local-apollo-fvp/debug/symbols.json
```

출력 경로가 없으면 `fvp-rd-aspen-native` sysroot가 준비되지 않은 것이다.
Yocto native FVP provider를 먼저 빌드해야 한다.

### 9.4 port 충돌 또는 연결 timeout

기존 listener를 임의로 종료하지 말고 owner를 확인한다.

```bash
ss -ltnp | rg ':7100\b'
```

다른 port를 선택하면 server와 client에 같은 값을 사용한다.

```bash
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7110
scripts/debug/local_debug_iris.py --port 7110 \
  --manifest build/local-apollo-fvp/debug/symbols.json --list-targets
```

### 9.5 breakpoint timeout

- boot 후반 symbol이면 timeout을 300~900초로 늘린다.
- UART log에서 해당 domain이 실제로 boot 단계에 도달했는지 확인한다.
- `symbols.json`의 address와 GDB의 `info address`를 비교한다.
- target instance가 CFG1/CFG2와 맞는지 `--list-targets`로 확인한다.
- symbol보다 앞선 reset/vector breakpoint로 이동해 실행 경로를 좁힌다.

`local_debug_iris.py`의 timeout exit code는 `2`, breakpoint 없이 정지한 경우는
`3`이다.

### 9.6 model이 이미 실행 중임

reset 직후 breakpoint가 필요하면 실행 중인 session을 종료한 뒤
`run_local_fvp_debug.sh`를 `--run` 없이 다시 시작한다. `--run`과 `--break`는
의도적으로 동시에 사용할 수 없다. `--break` 경로가 breakpoint 설치 후 model을
실행한다.

## 10. 현재 checkout의 검증 상태

2026-07-21 기준으로 다음 정적/API 검증은 통과했다.

```bash
bash -n scripts/debug/run_local_fvp_debug.sh \
  scripts/debug/gdbserver_gdb_wrapper.sh
python3 -m py_compile \
  scripts/debug/local_debug_iris.py \
  scripts/debug/run_local_gdb.py \
  scripts/setup/setup_local_debug_env.py
scripts/debug/run_local_fvp_debug.sh --help
scripts/debug/local_debug_iris.py --help
scripts/setup/setup_local_debug_env.py --help
```

또한 설치된 FVP의 Iris server에 직접 연결하여 target/register 열거와 timer
counter read/write를 확인했다. 다만 현재 checkout의
`build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf`는 존재하지 않으며,
현재 생성된 FVP manifest에는 `si-cl1-zephyr`만 등록되어 있다. 따라서 기존
wrapper의 full local-FVP image 기반 end-to-end breakpoint boot는 위 3.1의
FVP local build를 완료한 뒤 다시 수행해야 한다.

## 11. 관련 문서와 source

- `scripts/debug/run_local_fvp_debug.sh`
- `scripts/debug/local_debug_iris.py`
- `scripts/setup/setup_local_debug_env.py`
- `scripts/setup/local_debug_components.py:47-126`
- `scripts/run/run_local_fvp_tmux.sh`
- `doc/fvp-log-boot.md`
- [Arm Iris: debug and trace interface in Arm Models](https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/iris-the-new-debug-and-trace-interface-in-arm-models)
- [Arm Development Studio 2020.1 and Iris server support](https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/arm-development-studio-2020-1-now-available)
