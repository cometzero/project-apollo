# local_build GDB 디버깅

`local_build.sh` 결과물 중 Buildroot를 제외한 QBox, QBox 플러그인,
libqemu, TF-M, SCP-firmware, Zephyr, TF-A, OP-TEE, U-Boot, Linux의 ELF와
GDB 설정을 한 곳에서 관리한다.

## 준비와 빌드

호스트에는 `gdb`와 `gdb-multiarch`가 필요하다. QBox는 기본적으로
`RelWithDebInfo`로 빌드되므로 최적화된 실행 성능과 소스/라인 정보를 함께
유지한다. 완전한 비최적화 디버깅이 필요하면 빌드할 때
`QBOX_CMAKE_BUILD_TYPE=Debug`를 지정한다.

```bash
./local_build.sh qbox debug-manifest --no-package
```

기존 QBox 빌드가 `Release`였다면 CMake 명령 해시 변경을 감지해 자동으로
재구성한다. 펌웨어도 새로 빌드해야 하면 평소처럼 필요한 컴포넌트를 먼저
빌드하고 마지막에 `debug-manifest`를 선택한다.

생성 결과는 다음 위치에 있다.

- `build/local-apollo-qvp/debug/symbols.json`: ELF, 아키텍처, 디버그 정보,
  기본 심볼 목록
- `build/local-apollo-qvp/debug/gdb/*.gdb`: 컴포넌트별 GDB command file
- `build/local-apollo-qvp/debug/.build-id/`: strip된 실행용 libqemu가 사용할
  비-strip 심볼 ELF 연결
- `build/local-apollo-qvp/debug/README.md`: 현재 빌드 결과에서 생성한 요약

## 전체 QBox 디버그 세션

다음 명령은 `run_qbox_local.sh`와 같은 `fvp-like` tmux 창을 열고, 기존
interactive shell pane을 QBox host GDB로 교체한다.

```bash
./run_qbox_local_debug.sh
```

`qbox` window의 `gdb-host` pane은 `platforms-vp`를 `gdbserver`로 시작해
`main`, `sc_main`, `libqemu_init`에 breakpoint를 설정한다. 별도의
`gdb-targets` window에는 다음 네 GDB가 열린다.

- RSE `127.0.0.1:12340`: TF-M BL1_1, BL1_2, BL2, secure runtime
- SI0 `127.0.0.1:12341`: SCP-firmware
- SI1 `127.0.0.1:12342`: Zephyr
- AP `127.0.0.1:12343`: TF-A BL2/BL31, OP-TEE, U-Boot, Linux symbols

각 domain command file은 단계별 ELF를 한 GDB에 함께 로드하고 각 컴포넌트의
첫 entry symbol 주소에 breakpoint를 설정한다. 시작할 때 `info symbol`과
`info line` 결과가 출력된다. 단계별 이미지가 주소 공간을 재사용하더라도
breakpoint에 도달하면 해당 ELF가 active symbol file로 자동 전환된다.
이후 `list`, `info source`, `bt` 같은 일반 GDB 명령으로 소스와 호출 경로를
확인할 수 있다. QBox host는 `127.0.0.1:12339`를 사용한다. 이 다섯 포트는
실행 전에 비어 있어야 한다.

target이 실행 중일 때 GDB pane에서 `Ctrl+C`를 누르면 target만 interrupt하고
같은 pane의 GDB prompt로 돌아온다. GDB와 pane을 종료할 때만 `quit`을 사용한다.

기본 RSE/SI/AP pane은 4코어 PFDI 검사가 끝났음을 나타내는
`PFDI: OoR tests on core 3 succeeded.` 로그를 기다린 뒤 GDB를 연결한다. AP
또는 system-management GDB를 부팅 초기에 연결하면 QEMU의 stop 상태와
SystemC secondary CPU reset release가 충돌해 PFDI poll에서 멈출 수 있기
때문이다. 이 기본 모드에서는 실행 중인 OP-TEE의 심볼/소스와 U-Boot, Linux
entry breakpoint를 자연 부팅 중에 사용할 수 있다. OP-TEE `_start` 자체는
조기 AP 연결 모드에서 확인한다.
U-Boot ELF는 `0x88000000`에 link되어 있지만 TF-A가 BL33을
`0xe0000000`에 적재하므로, 생성된 domain script가 `0x58000000` offset을
자동 적용한다.

TF-A BL2/BL31, OP-TEE `_start`, 또는 RSE/SCP/Zephyr entry를 먼저 확인하려면
별도 실행에서 필요한 조기 연결 옵션을 쓴다.

```bash
./run_qbox_local_debug.sh --ap-early-attach
./run_qbox_local_debug.sh --firmware-early-attach
```

두 옵션을 함께 지정하면 모든 target GDB가 조기에 연결된다. 조기 연결 세션은
초기 firmware entry 확인용이다. PFDI와 후속 OS까지 계속 디버깅하려면 세션을
종료하고 기본 지연 연결 모드로 다시 실행한다.

세션만 띄우고 나중에 attach하려면 `--no-attach`를 사용한다. F12는 기존
`run_qbox_local.sh`와 동일하게 QBox와 tmux session을 종료한다.

## VS Code

권장 extension의 `Microsoft C/C++` 디버거를 설치한 뒤 Run and Debug에서
`Apollo QBox: all domains`를 선택한다. VS Code는
`run_qbox_local_debug.sh --vscode`로 동일한 QBox를 시작하고, host/RSE/SI0/
SI1/AP debugger를 각 포트에 연결한다. 단일 domain만 선택할 때는 먼저 VS Code
task `Apollo QBox: start debug servers`를 실행한 뒤 해당 debugger를 선택한다.
`all domains` compound는 이 start task가 debug manifest와 domain GDB script를
모두 생성하고 새 runtime log를 준비한 뒤에만 개별 debugger를 시작한다.
이 start task는 이전 `apollo-qbox-debug-vscode` tmux 세션이 남아 있으면 먼저
종료하고 새 세션으로 교체하므로, 실패한 실행 뒤에도 별도 정리 없이 재시작할 수
있다.
실행 중인 QBox의 모든 UART와 platform pane은 VS Code 명령 팔레트에서
`Tasks: Run Task`를 선택한 뒤 `Apollo QBox: open tmux console`을 실행하면
전용 통합 터미널에서 확인할 수 있다. `Ctrl+b`, `d`는 QBox를 종료하지 않고
터미널만 tmux에서 분리한다.
compound의 RSE/SI/AP 구성은 모두 PFDI core 3 성공 로그까지 기다리는 기본
지연 연결 모드다. compound의 `host run` debugger는 QBox가 domain GDB server를
생성하도록 host entry breakpoint를 제거하고 자동으로 실행한다. 모든 debugger가
연결된 뒤에는 host debugger를 Pause하고 QBox/libqemu breakpoint를 추가할 수 있다.

QBox `sc_main`부터 확인하려면 먼저 task `Apollo QBox: start debug servers`를
실행하고 `Apollo QBox: host`를 단독으로 선택한다. RSE/SI/AP의 초기 entry는
compound 대신 `RSE early`, `SI0 early (SCP)`, `SI1 early (Zephyr)`,
`AP early (TF-A)` 중 필요한 구성을 선택한다. 수동으로 서버만 시작하려면 다음
명령을 사용한다.

```bash
./run_qbox_local_debug.sh --vscode --no-attach
```

종료는 VS Code task `Apollo QBox: stop debug servers`를 실행하거나 tmux에서
F12를 누른다. `.vscode/launch.json`은 기본
`build/local-apollo-qvp` 경로를 사용하므로 다른 `--local-build-dir`을 쓰면
해당 `program`과 GDB command file 경로도 맞춰야 한다.

## 컴포넌트 확인과 심볼 검사

```bash
scripts/debug/run_local_gdb.py --list
scripts/debug/run_local_gdb.py qbox-host --batch
scripts/debug/run_local_gdb.py libqemu-aarch64 --batch
scripts/debug/run_local_gdb.py tfm-bl1_1 --batch
scripts/debug/run_local_gdb.py linux --batch
```

`--list`에서 `debug-info`는 소스 라인 디버깅이 가능한 ELF이고,
`symbols-only`는 심볼 테이블만 있는 ELF이다. QBox 플러그인은
`qbox-plugin-*` 이름으로 각각 선택할 수 있다.

## QBox 호스트와 libqemu

실행 중인 QBox에 attach할 수 있는 호스트에서는 다음과 같이 사용한다.

```bash
scripts/debug/run_local_gdb.py qbox-host --attach "$(pidof platforms-vp)"
```

`ptrace_scope` 정책으로 사후 attach가 차단되면 QBox runner가 처음부터 GDB의
자식 프로세스로 실행되게 한다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --host-gdb-script build/local-apollo-qvp/debug/gdb/qbox-host.gdb \
  --timeout 0
```

QBox가 Yocto의 strip된 libqemu를 로드하더라도 GDB는 실행 파일의 Build-ID와
`debug/.build-id/`를 이용해 같은 Build-ID의 비-strip ELF에서 소스와 심볼을
읽는다. libqemu만 별도로 검사할 때는 다음 명령을 사용한다.

```bash
scripts/debug/run_local_gdb.py libqemu-aarch64 \
  --break libqemu_init
```

## 개별 AP CPU의 TF-A, OP-TEE, U-Boot, Linux

이 컴포넌트들은 같은 AP CPU GDB stub에 각 단계의 ELF를 선택해 연결한다.
직접 부팅 runner에서 CPU 0의 stub을 연 예시는 다음과 같다.

터미널 1:

```bash
QBOX_APOLLO_GDB_CPU_INDEX=0 \
QBOX_APOLLO_GDB_PORT=12341 \
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build --interactive --timeout 0
```

터미널 2:

```bash
scripts/debug/run_local_gdb.py linux \
  --remote localhost:12341 --break start_kernel
```

부팅 단계에 따라 `tfa-bl2`, `tfa-bl31`, `optee-core`, `u-boot`, `linux` 중
현재 PC에 맞는 컴포넌트를 선택한다.

## RSE TF-M과 Safety Island

RSE의 TF-M 이미지는 기존 다중 타깃 helper가 RSE/AP GDB 포트를 함께 열고
검증 로그를 남긴다.

```bash
python3 scripts/debug/debug_qbox_fvp_rd_aspen_rse_gdb.py \
  --out-dir build/qbox-fvp-rd-aspen/gdb-local \
  --launch --sample-only --host-sample
```

개별 RSE 포트가 열려 있으면 `tfm-bl1_1`, `tfm-bl1_2`, `tfm-bl2`, `tfm-s`를
`run_local_gdb.py COMPONENT --remote HOST:PORT`로 연결할 수 있다.

`run_qbox_local_debug.sh`는 `live-cl0-cl1` 경로를 사용하고 SI0/SI1 CPU의
`gdb_port`를 명시적으로 열기 때문에 SCP-firmware와 Zephyr도 실시간
breakpoint를 사용할 수 있다. 기본 `run_qbox_local.sh`의 GDB port는 계속
비활성 상태다.

FVP는 GDB remote stub 대신 Iris를 제공한다. FVP의 실시간 breakpoint는
`scripts/debug/run_local_fvp_debug.sh`와
`scripts/debug/local_debug_iris.py`를 사용한다.
