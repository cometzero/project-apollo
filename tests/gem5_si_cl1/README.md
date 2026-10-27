# SI CL1 MHUv3 native MMIO test

실제 guest MMIO로 `SiCl1Mhu`와 GIC pending 상태를 검사한다. 네 PFDI
channel의 version/status, 잘못된 length와 unsupported command/protocol,
slot 경계 guard word, TX ACK, RX mask/clear, GIC IRQ pending/deassert,
HIPC AP offline 동작을 검사한다. CPU interrupt exception 진입, 실제 SCP
firmware, MHU safety extension, 물리 timing은 검증 범위에 포함하지 않는다.

Workspace root에서 실행한다. 새 `SiCl1Mhu`가 포함된 Yocto native binary와
그 manifest의 Python/library 환경을 사용한다. Fixture compilation은 독립적인
regression test용이며 launcher에서 guest를 다시 빌드하는 동작이 아니다.

```bash
GEM5_SRC="$PWD/hsoc-stack/tools/gem5"
TEST_OUT="$PWD/build/gem5-apollo-qvp/si-cl1-mhu-test"
mkdir -p "$TEST_OUT"
aarch64-linux-gnu-gcc -O2 -ffreestanding -nostdlib -static \
  -fno-stack-protector -mgeneral-regs-only -DSI_CL1_PRIMARY \
  -Wl,--build-id=none -Wl,-T,"$GEM5_SRC/tests/zena_si_cl1/probe.ld" \
  "$GEM5_SRC/tests/zena_si_cl1/start.S" tests/gem5_si_cl1/mhu.c \
  -o "$TEST_OUT/mhu.elf"
python3 - <<'PYTHON'
import json
import os
import subprocess
from pathlib import Path
root = Path.cwd()
meta = json.loads((root / "build/tmp_baremetal/deploy/gem5-native/gem5-native.json").read_text())
env = dict(os.environ, PYTHONHOME=meta["python_home"],
           LD_LIBRARY_PATH=os.pathsep.join(meta["library_path"]))
out = root / "build/gem5-apollo-qvp/si-cl1-mhu-test"
for cpu in ("atomic", "minor"):
    subprocess.run([meta["executable"], f"--outdir={out}/{cpu}",
                    "tests/gem5_si_cl1/mhu.py",
                    f"--gem5-source={root}/hsoc-stack/tools/gem5",
                    f"--elf={out}/mhu.elf", f"--cpu={cpu}"],
                   env=env, check=True, timeout=90)
PYTHON
```

`result.json`의 `status=PASS`, guest terminal의 `MHU_NATIVE_PASS`,
`m5_exit instruction encountered`와 exit code 0을 확인한다.
