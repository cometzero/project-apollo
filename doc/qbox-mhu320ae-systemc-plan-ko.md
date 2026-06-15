# QBox MHU-320AE SystemC Implementation Plan

작성일: 2026-06-09

## Goal

MHU-320AE SystemC component를 구현하고 Apollo/RD-Aspen QBox default MHU
backend를 `mhu320ae`로 전환한다. 전환 후 Apollo full-system live CL0/CL1
부팅에서 RSE, Safety Island CL0/CL1, TF-A, U-Boot, Linux login 및 post-login
probe가 통과해야 한다.

Goal 도구 상태: 이전 MMU-720AE goal이 `complete` 상태로 남아 있어 새 goal
생성은 도구에서 거부되었다. 따라서 이 문서를 이번 MHU-320AE goal의 source of
truth로 사용한다.

완료 상태: 2026-06-09에 `mhu320ae` component 전환, component test, isolated
CL1 boot, Apollo full-system live CL0/CL1 boot가 통과했다.

## 단계

1. Baseline 확인
   - 기존 `mhuv3_stub` register/service behavior와 tests를 확인한다.
   - Zena CSS guide, AP DTS, CL1 DTS, QBox Lua memory/IRQ map을 대조한다.

2. Component 생성
   - `mhu320ae` dynamic module을 추가한다.
   - 기존 검증된 PBX/MBX frame model과 Apollo boot hook을 동일 semantics로
     이동한다.
   - 테스트 target `mhu320ae-tests`를 추가한다.

3. Platform default 전환
   - AP SCMI, RSE/SI SCMI, AP/RSE secure service, AP/SI CL1 HIPC/PFDI 경로의
     `moduletype`을 `mhu320ae`로 바꾼다.
   - Build helper의 required target 목록에 `mhu320ae`를 추가한다.
   - RSE fidelity label을 `systemc-mhu320ae`로 갱신한다.

4. 정적/컴포넌트 검증
   - Shell/Python syntax check.
   - QBox map validation.
   - `mhu320ae`, `mhu320ae-tests`, `platforms-vp` build.
   - `mhu320ae` ctest.

5. Runtime 검증
   - 가능하면 isolated CL1 boot를 먼저 실행한다.
   - Apollo full-system live CL0/CL1 boot를 `--post-login-probe`로 실행한다.
   - Result JSON, UART logs, MHU trace, coverage marker를 확인한다.

6. Commit/push/shutdown
   - `tools/qbox` nested repo를 먼저 atomic commit한다.
   - root repo에서 docs/scripts/submodule pointer를 atomic commit한다.
   - GitHub remote branch로 push한다.
   - 모든 push 성공 후 `sudo poweroff`를 실행한다.

## 구현 원칙

- 기존 통과 경로의 behavior를 refactor 중 변경하지 않는다.
- Register model과 service-model hook은 문서에서 구분하지만, runtime 전환은
  한 component에서 먼저 검증한다.
- `mhuv3_rproc_stub`는 이번 전환에서 유지한다. 해당 path는 별도 regression과
  통합 계획이 필요하다.
- `mhuv3-trace.log` 파일명과 trace event format은 기존 analyzer 호환성을 위해
  유지한다.

## Verification commands

```bash
python3 -m py_compile \
  scripts/run/run_qbox_apollo_fvp_full.py \
  scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run/run_qbox_apollo_fvp_si_cl1.py \
  scripts/test/validate_qbox_fvp_rd_aspen_map.py

bash -n run_qbox.sh scripts/run/run_qbox_apollo_fvp_full_tmux.sh

./scripts/test/validate_qbox_fvp_rd_aspen_map.py

cmake --build tools/qbox/build \
  --target mhu320ae mhu320ae-tests platforms-vp --parallel 8

ctest --test-dir tools/qbox/build -R 'mhu320ae' --output-on-failure

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 900 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/mhu320ae-live-verify-$(date +%Y%m%d-%H%M%S)
```

## Review criteria

- Platform Lua에서 boot-critical MHU instance가 `mhu320ae`를 사용한다.
- Component tests가 기존 `mhuv3_stub-tests`의 핵심 behavior를 모두 보존한다.
- Full-system result JSON이 pass이고 marker group `rse`, `si_cl0`, `si_cl1`,
  `ap_firmware`, `linux`, `post_login_probe`가 통과한다.
- Fidelity label과 문서가 temporary stub이 아닌 `systemc-mhu320ae` 상태를
  반영한다.
