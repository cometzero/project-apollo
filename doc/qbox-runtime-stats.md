# QBox 실행 중 부하 표시

`run_qbox_yocto.sh`, `run_qbox_linux.sh`, `run_qbox_autosd.sh`는
`--stats`를 지정하면 기본 **host 시간 5초** 간격으로 부하를 로그에 기록한다.
`--stats-interval SECONDS`는 간격을 변경하면서 수집을 활성화한다.
옵션을 생략하면 수집하지 않는다. 간격은 유한한 양수여야 한다.
`--stats`와 `--stats-interval`은 monitor와 QMP도 자동 활성화한다.

```bash
./run_qbox_yocto.sh --bsp --stats
./run_qbox_linux.sh --bsp --stats-interval 10
./run_qbox_autosd.sh --headless --stats
```

- Yocto/full-system: 실행 디렉토리의 `qbox-platform.log`, TUI의 platform pane.
- Direct Linux: 실행 디렉토리의 `qbox.log`, TUI의 QBox log pane.
- AutoSD: 실행 디렉토리 아래 `full-system/qbox-platform.log`, full-system TUI.
- Headless도 같은 파일에 기록한다. guest UART에는 통계를 쓰지 않는다.
- `--no-attach`에서도 수집하며, 로그인 PASS 이후에도 runtime이 살아 있으면
  계속 출력한다. 기존 timeout·F12·종료 정책을 따른다.

다음은 형식 예시이며 측정 결과가 아니다.

```text
[70s] CPU 16.0% (main 2.8% | vCPU 10.7% [AP 7.8 RSE 0.2 SI0 1.5 SI1 1.2] | other 2.6%) RSS 2276M threads=28
```

| 항목 | 의미 |
|---|---|
| `[70s]` | 수집 시작 이후 host 경과 시간, 정수 초 |
| `CPU` | 실제 QBox PID의 user+kernel CPU 사용률 |
| `main` | SystemC kernel·모델 등을 실행하는 main OS thread |
| `vCPU` | 이름이 `/TCG`로 끝나는 OS thread의 CPU 사용률 합계 |
| `other` | 그 외 I/O·RCU·backend 등 OS thread의 합계 |
| `RSS` | QBox PID의 RSS 근사값, `M`은 MiB |
| `threads` | snapshot에서 읽은 OS thread 수 |

100%는 host 논리 CPU 하나다. 사용률은 `/proc`의 user/system 누적 tick 차이를
`CLK_TCK`와 실제 monotonic 경과 시간으로 나눠 계산한다. guest CPU 사용률이나
전체 host의 load average가 아니다. subprocess CPU/RSS도 합산하지 않는다.
Thread snapshot은 원자적이지 않아 thread 합계와 process 전체 값이 조금 다를
수 있다. `main`은 개별 SystemC process의 순수 CPU 비용을 뜻하지 않는다.

## Subsystem별 출력

`--stats`만 지정하면 monitor와 QMP가 자동 활성화되어 각 subsystem의
vCPU 사용률을 표시한다. `--stats-interval`도 동일하게 동작한다.
별도 `--qmp`, `--monitor`, QMP 디렉토리 환경변수는 필요하지 않다.

```bash
./run_qbox_yocto.sh --bsp --stats
./run_qbox_linux.sh --bsp --stats
# AutoSD도 기존 실행 명령에 --stats만 추가
```

Direct Linux는 AP만, full-system은 AP·RSE·SI0·SI1을 표시한다.
Monitor는 기본 `127.0.0.1:18080`이며, 다른 실행과 포트가 겹치면
`--monitor-port 18180`처럼 지정한다. QMP는 전용 임시 Unix socket 디렉토리를
사용한다. Full-system runtime이 직접 만든 디렉토리는 VM 종료 후 정리하며,
상위 launcher에서 전달받은 디렉토리의 소유권은 유지한다.

도메인별 값은 `vCPU` 뒤 대괄호 안에 AP, RSE, SI0, SI1 순서로 출력하며
모두 % 단위다. 도메인 값은 vCPU thread 비용이며 주변장치·SystemC 비용 전체가 아니다.
QMP 매핑은 30초 동안 캐시하며 TID 소멸·identity 변경 시 갱신한다.
설정된 domain의 매핑이나 thread 측정이 불가능하면 `N/A`로 표시한다.
Monitor/QMP가 아직 준비되지 않았거나 조회에 실패하면 host 통계는 계속 출력한다.
user/kernel 구분·simulation 진행률은 간결한 한 줄 출력에서 생략한다.

HTTP/QMP 조회는 runtime 로그 loop 밖에서 실행한다. `/proc` 기본 수집은
별도 패키지나 perf 권한이 필요 없다. QMP 상세 조회는 기존 dashboard의
`websocket-client` 의존성을 사용하며 없으면 상세 정보만 사용할 수 없다.
통계 출력은 boot/PASS 판단에 사용하는 simulator 원본 문자열에 추가하지 않는다.

## 구현 및 검증

공통 수집기는 `scripts/run/qbox_load_stats.py`, 선택적 monitor 조회는
`scripts/run/qbox_stats_monitor.py`에 있다. 실제 QBox child를 소유한 runtime에만
연결하여 AutoSD → Yocto → runtime 경로에서 중복 수집하지 않는다.

관련 테스트는 `tests/test_qbox_load_stats.py`, `tests/test_qbox_stats_monitor.py`,
`tests/test_qbox_stats_options.py`이다. 실제 실행 증거는
`build/qbox-apollo-qvp/stats/`에 보관한다. 이 기능은 운영 중 부하 추세를 보는
용도이며 perf stack 분석, SystemC process별 계측, 전체 기능 qualification을
대체하지 않는다.

최초 구현의 이전 출력 형식으로 수행한 실행 검증에서는 full-system headless와 TUI 모두 BSP 로그인 후에도
5초 간격 출력이 지속됨을 확인했다. Direct Linux의 headless 2초 간격,
QMP AP 매핑, simulation 진행률 및 TUI 5초 간격 표시도 확인했다.
TUI capture와 결과 요약은 `build/qbox-apollo-qvp/stats/validation.json`에서
참조한다. Direct Linux BSP의 `pfdi_misc` selftest FAIL은 그대로 남아 있으므로
통계 기능 검증을 BSP 전체 PASS로 해석하지 않는다. AutoSD는 옵션 전달 테스트를
수행했으며 이번 변경에서 별도 AutoSD 이미지 부팅은 수행하지 않았다.

최종 한 줄 형식과 자동 monitor/QMP 활성화는 `--stats`만 지정한
full-system BSP 부팅에서 AP·RSE·SI0·SI1 값이 모두 출력되는 것으로 확인했다.
해당 실행은 `build/qbox-apollo-qvp/stats/auto-monitor-validation.json`,
최종 관련 테스트 224개 PASS는 같은 디렉토리의 `commit-tests.log`에 기록했다.
