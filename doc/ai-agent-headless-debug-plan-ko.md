# Apollo FVP/QBox AI Agent Headless Debug 구현 계획

## 1. 목적

기존 `run_*.sh --debug`의 사람 중심 interactive GDB/tmux 동작은 유지하면서,
AI agent가 터미널 입력 없이 FVP와 QBox의 breakpoint 도달 여부, 현재 PC와
source 위치를 수집할 수 있는 bounded debug 경로를 추가한다. FVP는 live
Iris/GDB snapshot을 수집하고, QBox는 co-simulation timing을 교란하지 않도록
runtime PC-entry event와 offline GDB symbolization을 결합한다.

완료 조건은 다음과 같다.

1. `interactive`, `probe`, `server` debug mode가 명확히 분리된다.
2. `probe`는 timeout 안에 종료되고 `debug-result.json`과 debugger raw log를
   생성한다.
3. `probe` 종료 시 자신이 실행한 FVP/QBox process group만 정리한다.
4. `server`는 debugger endpoint 준비 결과를 기록하고 외부 client가 연결할 수
   있도록 foreground에서 유지된다.
5. 실제 FVP와 QBox에서 동일한 firmware breakpoint probe가 성공한다.
6. 프로젝트-local Codex skill이 이 경로를 선택하고 결과를 판정할 수 있다.

## 2. 비목표

- 기존 interactive tmux layout이나 GDB 사용법을 변경하지 않는다.
- FVP/QBox 모델, firmware, kernel 또는 Yocto image를 변경하지 않는다.
- GDB/MI 기반 범용 debugger frontend를 새로 구현하지 않는다.
- 모든 GDB command를 CLI 문자열로 전달하는 임의 실행 interface를 만들지 않는다.
- debug probe 결과를 정상 boot qualification 결과로 간주하지 않는다.

## 3. CLI 계약

debug target은 기존 값을 유지한다.

```text
qbox, rse, si_cl0, si_cl1, tf-a, u-boot, linux
```

FVP는 기존과 같이 `qbox` host target을 제외한다.

새 공통 옵션은 다음과 같다.

```text
--debug TARGET
--debug-mode interactive|probe|server
--debug-timeout SECONDS
--debug-result FILE
```

- `interactive`: 현재 기본값. tmux 안에서 GDB를 실행한다.
- `probe`: headless runner를 실행하고 기본 entrypoint에서 bounded snapshot을
  수집한 뒤 종료한다.
- `server`: endpoint가 준비되면 결과 JSON을 기록하고 runner를 foreground에서
  유지한다. 종료 signal을 받으면 자식 process group을 정리한다.
- `probe`와 `server`는 QBox에서 headless 실행을 강제한다.
- `--debug-mode`는 `--debug`와 함께 사용해야 한다.
- `--debug-timeout`은 endpoint, breakpoint와 debugger command의 상한이다.
- `--debug-result` 기본값은 `${OUT_DIR}/debug-result.json`이다.

대표 명령은 다음과 같다.

```bash
./run_fvp.sh --machine apollo-qvp \
  --debug tf-a --debug-mode probe --debug-timeout 600 \
  --out-dir build/agent-debug/fvp-tfa

./run_qbox_yocto.sh --bsp --headless \
  --debug tf-a --debug-mode probe --debug-timeout 600 \
  --out-dir build/agent-debug/qbox-tfa

./run_qbox_local.sh --headless \
  --debug tf-a --debug-mode server \
  --out-dir build/agent-debug/qbox-server
```

## 4. 구현 구조

### 4.1 공통 process/result 계층

`scripts/debug/agent_debug_common.py`가 다음을 담당한다.

- runner를 새 process session으로 실행
- TCP endpoint 및 log marker bounded wait
- stdout/stderr log 저장
- signal 전달과 process-group 종료
- atomic `debug-result.json` 기록
- command와 elapsed time 기록

### 4.2 QBox probe

`scripts/debug/run_agent_qbox_debug.py`가 다음 순서로 실행한다.

1. headless Apollo full-system runner 실행
2. firmware CPU target은 QBox PC-entry hook의 fresh marker 대기
3. marker에 기록된 실제 guest PC 추출
4. debug manifest의 동일 ELF/GDB command file을 오프라인 GDB에 로드
5. symbol, instruction과 source line 해석
6. 기대 entry address와 관측 PC 비교
7. `gdb.log`과 `debug-result.json` 기록
8. probe mode에서는 runner process group 정리

QBox host target은 별도 gdbserver의 첫 client로 GDB가 직접 연결한다. firmware
CPU probe는 QEMU remote GDB에 연결하지 않는다. 실제 검증에서 remote attach가
AP를 stop-all 상태로 전환하여 RSE SCMI power-domain 절차와 SI/PFDI timing을
교란했기 때문이다. live register/backtrace가 필요하면 `server` 또는
`interactive` mode를 사용하고, debug attach로 인한 timeout을 정상 부팅 결함과
분리해 해석한다.

### 4.3 FVP probe

`scripts/debug/run_agent_fvp_debug.py`가 다음 순서로 실행한다.

1. Iris server를 활성화한 FVP를 tmux 없이 실행
2. Iris endpoint 대기
3. `local_debug_iris.py`로 component entry breakpoint 설치 및 실행
4. breakpoint hit 후 lite-cornea와 GDB batch를 연결
5. PC, threads, backtrace, registers, instruction과 source line 수집
6. `iris-probe.log`, `gdb.log`, `debug-result.json` 기록
7. FVP process group 정리

Iris Python API는 deterministic breakpoint/run-control에 사용하고,
lite-cornea/GDB는 DWARF source와 backtrace 수집에만 사용한다.

### 4.4 launcher 연동

- `run_fvp.sh`
  - interactive mode는 기존 tmux 경로 유지
  - probe/server mode는 FVP agent helper 호출
- `run_qbox_yocto.sh`
  - interactive mode에서만 `--headless --debug` 거부
  - probe/server mode는 기존 headless full-system command를 QBox agent helper에
    전달
- `run_qbox_local.sh`
  - `--headless` 추가
  - Yocto launcher와 동일한 canonical Python full-system runner를 사용
  - probe/server mode는 QBox agent helper 호출

## 5. 결과 계약

`debug-result.json`의 최소 필드는 다음과 같다.

```json
{
  "schema_version": 1,
  "backend": "fvp-iris|qbox-gdb",
  "mode": "probe|server",
  "status": "passed|ready|failed|timeout",
  "passed": true,
  "target": "tf-a",
  "component": "tfa-bl2",
  "breakpoint": "bl2_main",
  "expected_pc": "0x...",
  "observed_pc": "0x...",
  "breakpoint_hit": true,
  "timed_out": false,
  "debugger_returncode": 0,
  "runner_returncode": null,
  "elapsed_seconds": 0.0,
  "runner_log": "...",
  "debugger_log": "...",
  "runtime_out_dir": "...",
  "cleanup_completed": true
}
```

exit code 계약은 다음과 같다.

- `0`: probe 성공 또는 server ready
- `2`: CLI, manifest 또는 artifact 오류
- `3`: endpoint/breakpoint timeout
- `4`: debugger 실행 실패 또는 기대 PC 불일치
- runner가 먼저 실패하면 runner exit code와 log를 결과 JSON에 기록하고 `4`를
  반환한다.

## 6. 테스트 계획

### 6.1 실패 테스트 우선

- common helper의 endpoint wait, process cleanup과 result 기록
- fake QBox runner/GDB를 사용한 probe 성공, timeout, PC mismatch
- fake FVP/Iris/cornea/GDB를 사용한 probe 성공과 timeout
- 각 root launcher의 debug mode option mapping
- `interactive` 기본 동작 보존
- Yocto `--headless --debug`는 probe/server에서 허용하고 interactive에서 거부
- local QBox headless command가 tmux wrapper를 사용하지 않는지 확인

### 6.2 정적 및 회귀 테스트

```bash
python3 -m py_compile scripts/debug/*.py
bash -n run_fvp.sh run_qbox_local.sh run_qbox_yocto.sh
python3 -m pytest -q \
  tests/test_run_agent_fvp_debug.py \
  tests/test_run_agent_qbox_debug.py \
  tests/test_run_fvp_debug_option.py \
  tests/test_run_qbox_local_debug_option.py \
  tests/test_run_qbox_yocto_sh.py
```

기존 launcher/debug 관련 테스트도 함께 실행한다.

## 7. Skill 계획

`.codex/skills/apollo-platform-debug/`에 프로젝트-local skill을 생성한다.

- log 기반 triage를 첫 단계로 강제
- FVP/QBox와 local/Yocto artifact 선택 기준 제공
- `interactive`, `probe`, `server` 선택 기준 제공
- target별 기본 entrypoint와 timeout 안내
- `debug-result.json` 판정 방법 제공
- probe artifact와 runtime log를 최종 근거로 요구
- session/process cleanup 범위를 현재 UID와 해당 out-dir로 제한

`skill-creator`의 `init_skill.py`, `generate_openai_yaml.py`,
`quick_validate.py`를 사용한다.

## 8. 실제 검증 결과

동일한 `tf-a:bl2_main` probe를 FVP와 QBox에서 실행했다. 모든 결과에서
`status=passed`, `breakpoint_hit=true`, expected/observed PC `0x82964`,
`cleanup_completed=true`를 확인했다.

| 대상 | 결과 artifact | 경과 시간 | source 증거 |
| --- | --- | ---: | --- |
| FVP Iris | `build/agent-debug/fvp-tfa-actual/debug-result.json` | 16.654초 | `bl2_main.c:52`, live GDB snapshot |
| QBox 1차 | `build/agent-debug/qbox-tfa-offline-final-1/debug-result.json` | 22.752초 | `bl2_main.c:52`, entry symbol/disassembly |
| QBox 2차 | `build/agent-debug/qbox-tfa-offline-final-2/debug-result.json` | 22.551초 | `bl2_main.c:52`, entry symbol/disassembly |
| skill forward-test | `build/agent-debug/qbox-tfa-skill-forward-final/debug-result.json` | 22.542초 | `bl2_main.c:52`, entry symbol/disassembly |
| 최종 release probe | `build/agent-debug/qbox-tfa-release-final/debug-result.json` | 22.407초 | `bl2_main.c:52`, entry symbol/disassembly |

QBox와 libqemu는 실험 코드를 제거한 source 상태에서 다음 task를 강제
재빌드했고 모두 성공했다.

```bash
bitbake qbox-libqemu-native -c populate_sysroot -f
bitbake qbox-apollo-qvp-native -c populate_sysroot -f
```

runtime recipe sysroot와 component sysroot의
`libqemu-system-aarch64.so` SHA-256은 모두
`d993803c8888384f56bfc98aed8a5e73ea73f8a4ef176760800e24a544bce4ad`로
일치했다.

최종 정적/회귀 검증은 다음과 같다.

- 변경 Python `py_compile`: 성공
- root/debug shell script `bash -n`: 성공
- launcher/agent-debug pytest: `73 passed`
- `skill-creator` `quick_validate.py`: `Skill is valid!`
- top-level, QBox, QEMU `git diff --check`: 성공

forward-test agent는 생성된 skill을 다시 읽은 후 fresh QBox probe를 독립
실행했다. PC, symbol/source/disassembly, process cleanup과 TCP 12343 종료를
모두 확인했으며 source file은 변경하지 않았다.

## 9. 위험과 완화

- debugger attach가 boot timing을 바꿀 수 있으므로 probe 결과를 성능 측정에
  사용하지 않는다.
- FVP lite-cornea는 single-core view와 write 제한이 있으므로 secondary CPU
  분석에는 Iris target을 명시하는 후속 확장이 필요하다.
- QBox live GDB는 여러 virtual CPU와 SystemC 동기화를 정지시킬 수 있으므로,
  자동 probe는 PC-entry event와 offline symbolization만 판정한다.
- debug session은 정상 boot fail-pattern을 의도적으로 만날 수 있으므로
  runtime pass/fail과 debugger pass/fail을 별도 필드로 기록한다.
- destructive 전역 cleanup 대신 helper가 생성한 process group만 종료한다.
