# 필수 코드 정리 및 계측 패치 보관

작성일: 2026-10-01. 목적은 실험 코드의 상시 유지 없이 필요한 수정과
검증만 남기는 것이다. 기존 로그와 PASS/FAIL 판정은 삭제하거나 변경하지 않는다.

## 남긴 코드

| 소유 저장소 / 파일 | 남긴 이유 |
|---|---|
| Linux `sound/soc/dwc/dwc-pcm.c` | PCM stream lock으로 threaded IRQ의 FIFO 처리와 trigger/state 전환을 직렬화한다. lock 내부에서는 `snd_pcm_period_elapsed_under_stream_lock()`을 사용한다. 관측된 PIO START 경쟁 수정 |
| Root `scripts/test/verify_qemu_i2s_wav.py` | capture RUNNING 확인 후 재생, `--fatal-errors`, 실패 시 상대 프로세스 정리, 실패 exit code 보존, UART canonical line 한도 내 분할. WAV 전체 비교 및 기존 rate/frame/buffer 기준 유지 |
| Root `scripts/test/qbox_audio_health.py` 및 두 QBox audio verifier | 이미 출력된 XRUN/PFDI timeout/RCU stall을 PASS로 오판하지 않도록 검사. 새 계측이나 guest 정책 변경 없음 |
| Root `scripts/test/verify_qbox_linux_audio.py` | 실제 두 I2S DT가 요청한 DMA/PIO 모드인지 확인 |
| Root `scripts/test/verify_qbox_full_audio.py` | launcher에 정수 timeout을 전달 (`1800.0` 인자 문제 방지) |
| Root `tests/test_qbox_audio_health.py`, `tests/test_verify_qemu_i2s_wav.py` | 실패 메시지의 범위·오판 방지와 WAV 프로세스 종료/실패 전파 회귀 검사 |

Guest health의 `NO_FAILURE_OBSERVED`는 로그 구간에서 실패가 없었다는 뜻이며
PFDI liveness/deadline PASS가 아니다. 첫 `AUDIO_DT_BEGIN` 이전 실패는 별도로
기록한다. 기본 full DMA의 XRUN 원인은 이 정리로 해결됐다고 주장하지 않는다.

## 제거하고 패치로 옮긴 코드

[패치 목록과 적용 절차](patches/README.md), [파일별 hash/mode](patches/manifest.json).

- QEMU DMA350/I2S telemetry, QBox initiator DMI/alias/BQL/transport telemetry,
  PCM checker의 선택적 ALSA 상태 dump를 active source에서 제거했다.
- P3 regular IRQ cache도 제거했다. native 호출 감소는 관측됐지만 full DMA
  실패를 해결하지 못했고 기존 GpioProxy가 이미 같은 level의 SystemC 전달을
  걸러낸다. 필수 기능 수정으로 유지할 근거가 부족하므로 독립 후보 패치로 보관한다.
- `qbox_audio_experiment.py`, `qbox_audio_diagnostics.sh`,
  `qbox_audio_repeat.py`, `qbox_audio_uki.py`, `qbox_audio_dma_cfs.sh`,
  `qbox_audio_rr60.sh`, `summarize_qbox_audio_trace.py` 및 해당 테스트를 제거했다.
  두 runner의 diagnostics/repeat/kernel/PCM-only 실험 옵션과 추가 model 후보
  테스트도 같은 패치에 보관했다. 표준 memory/PCM/WAV suite는 유지한다.
- WAV의 준비 상태 판정은 남기고 `/proc/asound` 상태 본문 dump는 패치로 옮겼다.

QEMU, QBox core, auto-solutions PCM recipe 소스는 해당 파일의 기존 HEAD와
동일하다. Linux 수정과 검증 코드를 제외한 추가 동작 변경은 없다.
Lua, freerunning, quantum_keeper, quantum, AP CPU 수, firmware domain,
DMI 구성과 I2S frame pacing은 수정하지 않았다.

## 증거 보존과 검증

정리 전 소스 snapshot 및 정리 검증 로그:
[`build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/`](../../build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/).
패치는 정리 후 소스를 base로 생성했고 임시 Git 트리의 적용·역적용에서
원본 파일 byte와 mode를 확인했다. 관련 없는 `.vscode`, SCP, BSP U-Boot
변경 및 기존 비추적 문서는 보존했다. 커밋과 push는 수행하지 않았다.

기존 [실험 결과](04-implementation-results.md)는 **정리 전 binary/kernel**의
결과다. CFS warm3 PASS를 정리 후 기본 정책의 PASS로 이전하지 않는다.
특히 기존 BSP WIC의 kernel은 PIO 수정 Image와 다르며, 이전 full 실험은
private UKI의 `--kernel` 교체를 사용했다. 현재 표준 full verifier는 WIC의
kernel을 사용한다. 패치 없이 수정 kernel을 full에 적용하려면 BSP 이미지를
정상 재빌드해야 한다.

정리 후 검사 결과는 아래에 기록한다.

- 패치 5개: 임시 트리 적용/역적용 byte·mode 복원 PASS. 현재 트리의 base hash
  및 적용 검사 PASS (02는 01 적용 후 검사).
- 남긴 Python/WAV shell 회귀 검사: **45 PASS** (`pytest-final.log`).
- 재빌드한 standalone QEMU 모델의 FIFO/frame/DMA/IRQ 검사: **28/28 PASS**
  (`models/result.json`).
- 두 QBox verifier `--help`, 관련 Git diff whitespace 및 문서 링크 검사 PASS.
- `qbox-apollo-qvp-native qemu-apollo-native i2s-loopback -c populate_sysroot`:
  **1,190 tasks 성공**, 이 중 1,177은 재실행 불필요. QBox `do_check`는
  플랫폼 **64/64**, core **61/61 PASS** (`build.log`, `qbox-do-check.log`).
  경고 1개는 이전 강제 실행의 `do_check is tainted from a forced run`이다.
  BSP WIC/initramfs 전체 재생성은 수행하지 않았다.

- 정리 후 재빌드한 QBox로 AP-only 표준 suite를 DMA/PIO 각 1회 실행:
  **두 모드 모두 PASS**, 모드별 memory **4 cases × 5 iterations = 20/20**,
  PCM **4/4**, 48kHz S16_LE stereo WAV **양방향 2/2**.
  각 녹음은 **96,000 frames**이며 원본 WAV 전체 byte 및 PCM이 동일하다.
  PFDI timeout/RCU stall은 관측되지 않았다.
  [결과](../../build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/ap-audio/result.json),
  [요약](../../build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/ap-summary.json),
  [binary/Image hash](../../build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/rebuilt-artifacts.json).
  실행 명령:

  ```bash
  python3 scripts/test/verify_qbox_linux_audio.py \
      --out-dir build/qbox-apollo-qvp/dma-i2s-cleanup-20261001/ap-audio --mode both
  ```

- 재빌드한 QEMU/libqemu와 QBox DMA/I2S wrapper에서 제거한 telemetry 활성화
  문자열이 없는 것도 확인했다. **Full-system은 이번 정리에서 재시험하지 않았다.**
  기존 기본 full DMA FAIL 및 장시간/반복 시험 한계는 그대로 남는다.
