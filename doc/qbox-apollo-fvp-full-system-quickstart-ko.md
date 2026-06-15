# QBox Apollo FVP Full-System Quickstart

생성일: 2026-06-08

이 문서는 Apollo FVP local build 산출물을 QBox full-system에서 바로 실행해
볼 수 있는 최소 절차를 정리한다. 자세한 검증 절차와 completion gate는
`doc/qbox-apollo-fvp-full-system-runbook-ko.md`와
`doc/qbox-apollo-fvp-full-system-goal-verification.md`를 참조한다.

## 현재 준비 상태

현재 checkout 기준으로 실행 준비 상태는 확인되어 있다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --check-only \
  --out-dir build/qbox-apollo-fvp/full-ready-check

JOBS=8 ./local-build.sh qbox
```

확인 결과:

- `build/qbox-apollo-fvp/full-ready-check/result.json`: `passed: true`
- `build/qbox-apollo-fvp/full-ready-build/result.json`: `passed: true`
- Safety Island mode: `live-cl0-cl1`
- 필요한 local boot artifact 누락: 없음
- `tmux -V`: `tmux 3.4`

## 바로 실행

workspace top directory인 `/build/arm/arm-auto-solutions`에서 실행한다.

```bash
./local-build.sh
./run_qbox.sh
```

`run_qbox.sh`는 다음 동작을 자동으로 수행한다.

- `live-cl0-cl1` Safety Island mode 선택
- QEMU-native CC3XX backend와 현재 RSE fast-path 옵션 적용
- `2222`부터 빈 SSH host-forward port 자동 선택
- rootfs와 EFI capsule disk를 `out-dir/input-images/` 아래 per-run copy로 생성
- timestamp가 포함된 tmux session과 output directory 생성
- QBox runner와 subsystem별 UART log tail pane으로 자동 attach

- RSE / TF-M: `qbox-rse.log`
- Safety Island CL0 / SCP-firmware: `qbox-safety-island-cl0.log`
- Safety Island CL1 / Zephyr: `qbox-safety-island-cl1.log`
- TF-A / OP-TEE secure console: `qbox-secure-console.log`
- U-Boot / Linux primary console: `qbox-primary-console.log`
- QBox platform stdout: `qbox-platform.log`

`--timeout 0`과 `--keep-running-after-pass`를 사용하므로 Linux boot와
post-login probe가 통과해도 QBox는 자동 종료되지 않는다.

기본 SSH forwarding은 `host:<자동 선택 포트>`에서 guest `:22`로 연결된다.
기본 포트를 직접 지정하려면 다음처럼 실행한다.

```bash
SSH_PORT=2225 ./run_qbox.sh
```

기존 QBox 실행이 같은 disk image를 잡고 있으면 QEMU가 `Failed to get "write"
lock`으로 시작에 실패할 수 있다. `run_qbox.sh`는 기본적으로 rootfs와 EFI
capsule disk를 per-run copy로 만들어 이 충돌을 피한다. 이 복사를 끄고 원본
local build disk를 직접 사용하려면 다음처럼 실행한다.

```bash
RUN_QBOX_COPY_DISKS=0 ./run_qbox.sh
```

## 백그라운드 실행

터미널을 바로 점유하지 않으려면 `--no-attach`를 추가한다.

```bash
./run_qbox.sh --no-attach
```

실행 시 출력되는 session 이름으로 나중에 접속한다.

```bash
tmux attach -t <session-name>
```

종료는 tmux 내부에서 `F12`를 누르거나, 외부 터미널에서 다음 명령을 사용한다.

```bash
tmux kill-session -t <session-name>
```

## 성공 확인

실행 결과는 `--out-dir` 아래에 남는다.

```bash
jq '{passed, verdict, blocker, safety_island_mode, marker_groups}' \
  <out-dir>/result.json
```

정상 부팅이면 다음 evidence가 확인된다.

- RSE log: `Starting TF-M BL1_1`, `Jumping to the first image slot`
- Safety Island CL0 log: `SCP-firmware`, `GIC-multiview configured successfully`
- Safety Island CL1 log: `Booting Zephyr OS`, `PFDI service ready`
- Primary console: `Booting Linux on physical CPU`, `apollo-fvp login:`
- Post-login probe 사용 시 primary console: `__QBOX_PROBE_DONE__`

`summary.txt`는 사람이 읽기 쉬운 요약이고, `result.json`은 자동 검증용
결과다.

## 다시 빌드가 필요할 때

QBox module 또는 local boot artifact가 없다는 오류가 나오면 먼저 build-only
검증을 다시 실행한다.

```bash
JOBS=8 ./local-build.sh qbox
```

local boot image 자체를 다시 만들려면 다음을 사용한다.

```bash
./local-build.sh
```

그 뒤 다시 `./run_qbox.sh`를 실행한다.

## 참고

성능 옵션은 RSE 전체 부팅을 stub하지 않는다. `--cc3xx-qemu-native-backend`와
RSE fast-path 옵션은 secure boot chain은 유지하면서 QBox 내부 register/MMIO
경로와 일부 read-only boot path 병목을 줄이기 위한 실행 옵션이다.

더 엄격한 fidelity 비교나 negative secure-boot test를 수행할 때는
`doc/qbox-apollo-fvp-full-system-runbook-ko.md`의 full verification 절차를
사용한다.
