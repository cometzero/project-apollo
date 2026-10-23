# Apollo SoC runtime tests

`qa-tests`는 QBox에서 Apollo QVP를 실제 부팅하고 UART/SSH 명령과 부팅 로그로
기능을 검사하는 pytest suite입니다. `sw-ref-stack/documentation/test_automation`
가이드의 `Device`, `DriverBundle`, `platform_base_obj`, `session_manager` API를
사용합니다. [설계](DESIGN.md), [기능 대응표](COVERAGE.md), [원본 revision](upstream.json)을
함께 관리합니다.

## 실행

workspace의 기존 Yocto `apollo-qvp` 이미지와 설치된 QBox provider가 필요합니다.
pytest는 빌드하지 않습니다. Python 3.12 이상과 pytest, PyYAML, paramiko, jsonschema를
사용합니다. 개발 환경에 의존성이 없으면 별도 venv에서 `pip install -e ./qa-tests`로
설치할 수 있습니다. 이 suite는 workspace의 canonical launcher와 evaluator를 사용하므로
workspace checkout 안에서 실행합니다.

```bash
cd qa-tests
python3 -m pytest --collect-only -q
python3 -m pytest --image=bsp -v
python3 -m pytest --image=product -v
```

`--image`는 부팅할 이미지를 선택합니다. 테스트의 적용 범위는 별도 `image` marker로
분류하며, 기본 실행에서는 선택한 이미지에 맞는 전용 테스트와 `any`를 함께 실행합니다.

| 테스트 분류 | BSP 실행 | Product 실행 | 현재 분류 기준 |
|---|---|---|---|
| `bsp-only` | 실행 | SKIP | BSP에만 존재하는 인터페이스; 현재 해당 case 없음 |
| `product-only` | SKIP | 실행 | OVS/systemd 장치 profile, PSA 테스트 도구, RAS 서비스 |
| `any` | 실행 | 실행 | 공통 firmware/kernel 기능, boot, UART/SSH, power, PFDI, SI 진단 |

`any`는 양쪽 이미지에 적용된다는 의미이며 PASS를 보장하지 않습니다. 미구현 crypto
extension/HIPC/MBPP는 `any`에 속하되 이유를 적은 SKIP을 유지합니다. CPU idle도 실제
DT/sysfs에서 QVP의 WFI-only 제약이 확인되면 기능 미지원 사유로 SKIP됩니다.
기본 설정은 `configs/qbox.yaml`의 `qbox_apollo_qvp`, `--image=bsp`, boot timeout 600초입니다.

BSP WIC가 기본 deploy 경로에 없으면 YAML의 해당 플랫폼에
`rootfs: /absolute/path/to/nexios-bsp-initramfs-apollo-qvp.wic`를 지정하고
`--config`로 선택합니다. BSP `.qboxconf`가 없을 때 product `.qboxconf`의 provider/firmware를
재사용하되 BSP WIC를 별도로 검증·지정합니다. product 디스크를 BSP로 간주하지 않습니다.

```bash
# 도메인/category 또는 개별 기능 선택
python3 -m pytest tests/si_cl0 -v
python3 -m pytest tests/ap/power/test_cpu_frequency.py -v
python3 -m pytest tests/ap/network/test_ssh.py --image=bsp -v
python3 -m pytest tests/ap/network/test_ssh.py --image=product -v

# 분류 하나만 선택: 이미지 선택과 독립이며, 맞지 않는 이미지는 계속 SKIP
python3 -m pytest --image=product --test-scope=any -v
python3 -m pytest --image=product --test-scope=product-only -v
python3 -m pytest --test-scope=bsp-only --collect-only -q

# 모든 도메인의 boot 로그만 검사
python3 -m pytest tests/*/boot --image=product -v

# 별도 Yocto TOPDIR 및 새 evidence directory
python3 -m pytest --build-dir=/path/to/build --boot-timeout=900 \
  --run-dir=/path/to/new-run --image=bsp -v

# workspace 루트에서 실행할 때 설정을 명시
python3 -m pytest -c qa-tests/pyproject.toml qa-tests/tests --image=bsp -v
```

`--config`와 `--platform`으로 YAML/플랫폼을 선택할 수 있습니다. 실행은 직렬이며 xdist는
지원하지 않습니다. 테스트 간 UART 및 SoC 상태를 공유하므로 병렬 testcase 실행은
적합하지 않습니다. 파괴적 fault injection/hotplug 검사 뒤에는 다음 runtime 검사 전에
새 QBox generation을 부팅합니다. Ctrl+C도 fixture 정리와 부분 보고서를 수행합니다.

## 구조

```text
qa-tests/
  configs/qbox.yaml
  test_automation/
    configs/                  # upstream Config
    utils/                    # upstream Device/platform/network API
    targets/registry.py       # upstream DriverBundle/factory registry
    targets/qbox/             # QBox process lifecycle, UART, guest SSH
    checks/                   # 공통 runtime 명령과 판정
    pytest_plugin.py          # fixtures/configuration/lifecycle
    reporting.py              # pytest 단계별 결과와 보고서
  tests/
    ap/{boot,devices,network,power,safety,security}/test_*.py
    rse/boot/test_*.py
    si_cl0/{boot,safety}/test_*.py
    si_cl1/{boot,devices,network,safety}/test_*.py
  unittests/                  # host unit/regression tests
```

이전 `qa-tests/tests`의 host test는 `unittests`로 이동했습니다. OEQA/profile CLI와
profile/schema/matrix/injection 자료는 [scripts/validation](../scripts/validation/README.md)로
이동했습니다. 기존 `run_test.sh`, dashboard, canonical runner의 호출 방식은 유지합니다.
이곳의 runtime pytest 결과와 host unit 결과는 별도 보고서입니다.

```bash
# workspace root: 전체 host suite, QBox 부팅 없음
python3 scripts/test/run_pytest.py -q
# framework만
python3 -m pytest -c pytest.ini qa-tests/unittests -q
```

## 테스트 작성 API

```python
import pytest

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("power"), pytest.mark.image("any")]


def test_cpu_frequency(platform_base_obj):
    mgr = platform_base_obj.mgr
    port = mgr.get_port("ap")
    rc, output = mgr.execute_command_with_prompt_capture(
        port, "cat /sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq",
        timeout=30,
    )
    assert rc == 0, output
    assert int(output.strip()) > 0
```

`tests/<domain>/<category>/test_<feature>.py`가 report 분류 기준입니다.
`@pytest.mark.image("bsp-only"|"product-only"|"any")`는 이미지 적용 범위이며 생략하면 `any`입니다.
잘못된 값은 collection 단계에서 오류로 처리합니다. 이미지 불일치는 fixture를 시작하기 전에 SKIP됩니다.
`--test-scope`는 정확히 해당 분류만 선택하며 제외된 case는 SKIP 대신 deselected로 집계합니다.
현재 `bsp-only`만 선택하면 0건이므로 pytest의 `no tests collected`(exit 5)가 정상 결과입니다.
기존 `scripts/validation/profiles/`의 이미지 목록은 별도 legacy CLI 정책이며 이 suite를 제한하지 않습니다.
`@pytest.mark.destructive`는 다음 검사 전 재부팅을 의미합니다.
`cfg → auto_platform_config_data → platform_bundle → platform_driver/session_manager → platform_base_obj`
fixture를 제공합니다. boot 실패/명령 timeout/cleanup 실패는 오류로 보고합니다.

| Port 역할 | 입력/확인 방법 |
|---|---|
| `ap` | AP UART FIFO, 새 로그 cursor + command별 nonce, guest shell exit code |
| `ssh` | localhost hostfwd → guest SSH 인증·명령, guest exit code |
| `si_cl0` | SCP CLI Ctrl-E/command/Ctrl-D, 새 응답 및 기능별 completion 검증 |
| `si_cl1` | Zephyr shell 명령, 새 prompt/응답 및 기능별 내용 검증 |
| `rse` | RSE 부팅/measured boot 로그 확인 |
| `secure` | TF-A/OP-TEE/AP secure partition 로그 확인 |

로그 대기는 가이드의 `mgr.wait_for_prompt_in_log(port, prompt, timeout, regex=False)`를
사용합니다. QBox 확장 `mgr.read_log(port)`는 현재 generation의 정규화된 console 로그를
반환합니다. AP/SSH rc는 실제 guest exit code입니다. 펌웨어의 rc 0/1은 응답 완료/오류이며
Unix process exit code가 아닙니다. transport timeout은 124, 연결 종료는 125입니다.
RSE/secure를 interactive shell로 취급하지 않습니다. SSH 성공은 실제 SSH case로 검증합니다.
BSP와 product 모두 SSH case를 실행합니다. BSP의 Dropbear 기동 로그만으로는 연결·인증·명령
성공을 판정하지 않습니다. 최초 runtime 발견 사항과 재검증 경계는 [기능 대응표](COVERAGE.md)에
기록합니다.

## 부팅 단계별 검사

모든 도메인의 `boot` case를 일반 기능 검사보다 먼저 실행합니다. 각 case는 현재 QBox
generation의 UART 로그를 사용하며, 부팅 중간 배너뿐 아니라 다음 단계로의 진행도 확인합니다.

| 도메인/단계 | 로그 확인 내용 |
|---|---|
| RSE | TF-M BL1_1/BL1_2, SCP SCMI 연결·AP power-on, image slot 진입, TF-M runtime 시작 |
| RSE measured boot | BL2 및 BL_33 measurement 확장 |
| SI CL0 | SCP 시작, FWK 초기화 완료, CMN discovery 완료 |
| SI CL1 | Zephyr 시작, secondary CPU 1–3 시작, UART shell prompt |
| AP TF-A | BL2→BL31, runtime services 초기화, EL3→normal world handoff |
| AP U-Boot | U-Boot 시작, autoboot, Linux에서 확인한 U-Boot EFI handoff |
| AP Linux | kernel entry, Linux version, init process 실행 |
| AP OP-TEE | primary 및 secondary CPU 1–3의 normal world handoff |

SI CL1은 Zephyr의 primary 선출을 허용하되, secondary 1–3의 MPID가 DT에 속하고
중복 없이 나머지 CPU 순서와 일치하는지 검사합니다. 특정 physical CPU를 primary로 고정하지 않습니다.

8개 부팅 case를 각각 보고합니다. Linux `uname`과 Zephyr `kernel version`은 각 도메인의
`devices/`에서 별도 명령 검사로 실행합니다. 현재 공통 fixture는 AP readiness/login까지
기다리므로 Linux 부팅 자체가 실패하면 boot case도 setup ERROR로 기록되며 UART 로그가 보존됩니다.

## 자동 보고서와 원본 증거

별도 report 옵션 없이 실행마다
`build/qbox-apollo-qvp/qa-runtime-<UTC>-<unique>/`에 생성합니다.

- `report.html`, `report.md`: 상단 summary/분류별 수 → 도메인 → category → testcase 분류/결과/시간.
- `results.json`: testcase 및 setup/call/teardown 단계별 상태·시간, 실패 traceback/captured log.
- `junit.xml`: CI용 결과와 `image_scope` property. `--junitxml`을 직접 지정하면 지정 경로에 저장합니다.
- `invocation.json`, `platform.json`: 실행 인자와 적용 설정.
- `target/run-0001/` 등: QBox 실행 인자, UART/platform 로그, 명령 기록, process cleanup receipt.

실패 상세에 traceback 및 명령/응답을 보존합니다. SKIP/ERROR/NOT_RUN을 PASS로 세지 않고,
수집 오류·중단·collect-only도 구별합니다. 시간은 host wall time이며 첫 의존 testcase의
setup 시간에 해당 generation 부팅 비용이 포함됩니다. 내부 profile assertion 수와 pytest
case 수는 다릅니다. 기존 79개 assertion의 대응은 COVERAGE.md에서 추적합니다.

QBox 세션은 고유 출력 디렉터리, 디스크 복사본, 새 RSE 상태와 독립 SSH 포트를 사용합니다.
외부 TC397/vMCU는 SoC suite 기본 범위에서 제외합니다. 소유한 PID만 정리하며 기존 managed
session은 보존합니다. 기능 PASS는 silicon timing, 물리적 safety 검증 또는 FVP parity를
의미하지 않습니다.
