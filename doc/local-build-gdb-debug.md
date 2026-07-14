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

## AP CPU의 TF-A, OP-TEE, U-Boot, Linux

이 네 컴포넌트는 같은 AP CPU GDB stub에 각 단계의 ELF를 선택해 연결한다.
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

현재 QBox의 기본 SCP `service-model` 경로는 실제 SCP CPU GDB target을 만들지
않으므로 `scp-si0`는 심볼/소스 검사만 가능하다. SI CL1도 현재 full-system
경로에는 CPU `gdb_port`가 연결되지 않아 `si-cl1-zephyr`는 심볼/소스 검사만
가능하다. 해당 CPU 모델의 GDB port가 platform에 연결되면 생성된 ELF/GDB
설정은 그대로 `--remote`에 사용할 수 있다.

FVP는 GDB remote stub 대신 Iris를 제공한다. FVP의 실시간 breakpoint는
`scripts/debug/run_local_fvp_debug.sh`와
`scripts/debug/local_debug_iris.py`를 사용한다.
