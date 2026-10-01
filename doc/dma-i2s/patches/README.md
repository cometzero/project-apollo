# 계측·실험 패치 보관

2026-10-01 코드 정리에서 live source에서 제거한 코드이다. 빌드/launcher는
이 디렉터리의 패치를 자동 적용하지 않는다. 필수 수정과 판단 근거는
[코드 정리 기록](../05-code-cleanup.md), 기존 실행 결과는
[실험 기록](../04-implementation-results.md)을 참고한다.

| 패치 | 적용 저장소 | 내용 / 의존성 |
|---|---|---|
| [01](01-qemu-audio-telemetry.patch) | `hsoc-stack/tools/qemu` | DMA command/DONE/rearm/beat, I2S frame/FIFO/timer 계측 |
| [02](02-qemu-irq-cache-experiment.patch) | `hsoc-stack/tools/qemu` | **01 적용 후** regular IRQ 중복 호출 cache 및 카운터. 효과 미확정 후보 |
| [03](03-qbox-initiator-telemetry.patch) | `hsoc-stack/tools/qbox` | initiator DMI/alias/fallback/BQL/transport 계측과 테스트 |
| [04](04-i2s-loopback-diagnostics.patch) | `hsoc-stack/yocto/meta-hsoc-auto-solutions` | `I2S_LOOPBACK_DIAGNOSTICS=1` ALSA 오류 상태 출력 |
| [05](05-audio-experiment-tools.patch) | workspace root | 진단 수집·kprobe·반복 실행·private UKI 교체·CFS/RR60 대조군·분석 도구와 관련 테스트/runner 통합 |

01, 03, 04는 독립적으로 적용할 수 있다. 02는 01에 의존한다. 05는 도구를
복구하며 실제 native/bridge 측정에는 01/03 적용 후 재빌드가 필요하다.
정리 전 전체 실험 소스를 복원하려면 5개 모두 적용한다. RR60은
PFDI/RCU 실패가 관측된 **실패 대조군**이다. CFS 대조군도 기본 정책의 수정이 아니다.

## 적용 기준과 무결성

[manifest.json](manifest.json)은 패치 SHA256, 소유 저장소 HEAD, 각 파일의
**정리 후 base**와 **정리 전 archived** SHA256 및 mode를 기록한다.
`null`은 파일 부재다. QEMU 02의 base만 01 적용 상태다.
Root 05는 HEAD 자체가 아니라 **이번 정리에서 남긴 검증 수정까지 포함한 트리**에
적용한다. 따라서 HEAD SHA만으로 적용 가능 여부를 판단하지 않는다.

검증은 임시 Git 저장소에서 `reverse → apply → reverse` 순으로 수행했고,
각 단계에서 모든 대상 파일의 내용과 mode를 원본과 비교했다. 정리 후 실제
저장소에서도 `git apply --check`를 확인한다. 05에는 과거 원본의 EOF 빈 줄
1개가 있어 기본 whitespace 경고가 발생할 수 있다. 원본 byte 복원을 위해
그대로 보존했으며 아래 `--whitespace=nowarn`은 원본을 수정하지 않는다.

보관 파일 자체의 whitespace 검사는 이 디렉터리의 `.gitattributes`로
제외한다. unified diff의 빈 context 행에는 의미 있는 공백 prefix가 있으며,
패치 내부 소스의 무결성은 위 적용·역적용 및 SHA256 검사로 확인한다.

## 재적용

Workspace root에서 실행한다. patch 01/02의 순서는 필수다.

```bash
archive="$PWD/doc/dma-i2s/patches"
git -C hsoc-stack/tools/qemu apply --check "$archive/01-qemu-audio-telemetry.patch"
git -C hsoc-stack/tools/qemu apply "$archive/01-qemu-audio-telemetry.patch"
git -C hsoc-stack/tools/qemu apply --check "$archive/02-qemu-irq-cache-experiment.patch"
git -C hsoc-stack/tools/qemu apply "$archive/02-qemu-irq-cache-experiment.patch"
git -C hsoc-stack/tools/qbox apply --check "$archive/03-qbox-initiator-telemetry.patch"
git -C hsoc-stack/tools/qbox apply "$archive/03-qbox-initiator-telemetry.patch"
git -C hsoc-stack/yocto/meta-hsoc-auto-solutions apply --check "$archive/04-i2s-loopback-diagnostics.patch"
git -C hsoc-stack/yocto/meta-hsoc-auto-solutions apply "$archive/04-i2s-loopback-diagnostics.patch"
git apply --check "$archive/05-audio-experiment-tools.patch"
git apply --whitespace=nowarn "$archive/05-audio-experiment-tools.patch"
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j4 ./yocto_build.sh --keep-conf \
    qbox-apollo-qvp-native qemu-apollo-native i2s-loopback -c populate_sysroot
```

04의 `populate_sysroot`는 기존 WIC/initramfs를 갱신하지 않는다. 진단 PCM
도구는 05의 `--pcm-binary`로 해당 recipe의 `image/usr/bin/i2s-loopback`을
명시하거나 BSP 이미지를 재빌드한다. 커널 kprobe는 반드시 실험에 사용한
Image hash와 probe offset이 일치해야 한다. 명령과 artifact 경로는
[실험 기록](../04-implementation-results.md)에 보존했다.

제거할 때에는 추가 편집이 없는지 확인하고 각 저장소에서 `git apply -R
--check` 후 `git apply -R`을 사용한다. QEMU는 02, 01 순으로 제거한다.
계측 제거 후에도 native binary는 재빌드해야 source와 일치한다.
