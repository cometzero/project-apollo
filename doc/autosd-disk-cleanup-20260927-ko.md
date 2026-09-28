# AutoSD 디스크 정리 결과 (2026-09-27)

사용자 요청으로 `build/autosd`의 사용하지 않는 VM 디스크 복사본 19개를 삭제했다.
실제 할당 공간 기준 약 **42.52 GiB**를 회수했으며, `/build` 가용 공간은
약 **25 GiB → 67 GiB**, 사용률은 **95% → 85%**로 개선됐다.
삭제한 복사본은 직접 복구할 수 없다. 원본을 사용한 재실행은 가능하나
과거 복사본 내부의 런타임 변경 상태까지 재현되지는 않는다.

## 삭제 목록

다음 10개 경로는 `build/autosd/dashboard/` 아래이며 `/vm/rootfs.wic` 파일만 삭제했다.
이웃한 UART/Host 로그, job JSON, 결과 파일은 보존했다.

```text
20260927-142454-8e9492e4/f37076a4b1524f9bb658257cb95720a1
20260927-120355-51b341a1/aed18e8a4db54cb99613b3ee7dd43ad3
20260927-131149-4c30df89/eb12147abeb64d5fa97cffb3617f29e3
20260927-131149-4c30df89/cc8fc76fc02a43dab7ae3d899a83865f
20260927-135515-37b96135/b8f1c8758b164448b69ffa95a8fe9d01
20260927-135515-37b96135/2ca1c75d340c4b8eaa1e4e4127e7d76d
20260927-132411-c4c2fd8b/60520627560e4edaa421857c53a67a97
20260927-114209-02d26f85/107750b50a3146fc8367d0a101330647
20260927-112413-1341e716/b7b352a4bb484b8d9e284d1dd4eb69e5
20260927-130708-1dd19134/f0109cec2729430f9b3cc38993745546
```

다음 9개 경로는 `build/autosd/` 아래이며 `/rootfs.wic` 파일만 삭제했다.
해당 실행의 로그와 launch/result JSON은 보존했다.

```text
qemu-regular-validated
qemu-uki-regular-validated
qemu-ostree-validated
qemu-uki-ostree-validated
ukiboot-regular-b
ukiboot-regular-second
ukiboot-ostree-second
demo-newkernel-ostree-smoke
qbox-efi-ostree-first
```

## 보존 및 안전 확인

- 프로세스 인자와 열린 파일을 확인해 현재 VM 디스크를 제외했다.
- AutoSD loop mount가 없고 조사한 qcow2 이미지가 backing file 없는 독립 이미지임을 확인했다.
- 현재 실행 디스크: `dashboard/20260927-161222-530e591a/10e53714acf34799b09e9b7ef4ad8033/vm/rootfs.wic`.
- 서버 재시작 원본: `dashboard/20260927-142454-8e9492e4/5347146a956c443cbdca1340b59902e7/vm/rootfs.wic`.
- `demo-minimal-qm-prepared`, canonical regular/OSTree 입력, customization bundle 및 kernel 산출물 보존.
- `demo-builder-fullsystem/scratch.raw`는 31 GiB를 사용하지만 builder 재개 입력이므로 보존.
- `demo-regular-session/rootfs.wic`은 builder 복사 원본이므로 보존.
- 문서의 재사용 입력인 `demo-network-fixed-session` 및 `ukiboot-switch-b` 보존.
- 소스 저장소와 현재 VM 실행 상태는 정리 대상에서 제외했다.

## 반복 사용: 실행 이미지 정리 스크립트

`scripts/cleanup_run_images.py`는 workspace 위치를 자동으로 계산하며 다음 범위만 조사한다.

- `build/autosd/`
- `build/qbox-*/`
- `build/qemu-*/`

`launch.json`으로 별도 원본에서 생성된 실행 복사본임을 확인한 `rootfs.wic`만 삭제 후보로 삼는다.
커널·initrd·qcow2 원본·로그·결과 JSON·디렉토리 전체를 삭제하지 않는다.
builder/prepared/bundle/customization 경로, 다른 launch의 원본, 실행 중/마운트/backing 디스크,
symlink/hardlink 및 `--keep` 경로를 보존한다. 기본 보존 기간은 7일이며 계열별 최신 2개도 남긴다.
스크립트가 알 수 없는 외부 도구·문서의 재사용 경로는 `--keep`으로 지정해야 한다.

### 1. 삭제 없는 기본 확인

```sh
python3 scripts/cleanup_run_images.py > /tmp/run-image-cleanup-preview.json
jq '{mode, blocked, errors, eligible_allocated_bytes}' /tmp/run-image-cleanup-preview.json
```

권한 때문에 프로세스/컨테이너 저장소/이미지 의존성을 확인하지 못하면 `blocked: true`,
exit 2로 중단하며 `--apply`가 있어도 삭제하지 않는다. 이 호스트에서는 비특권 검사에서
권한 오류가 확인됐다. 권한을 완화하거나 저장소 소유권을 변경하지 말고 필요 시 sudo로 실행한다.

### 2. 최근 이미지까지 포함한 미리보기

작업 중인 다른 터미널에서 새 VM을 시작하지 않는 상태에서 수행한다.
다음 예시는 7일 제한만 없애고 최신 2개 보존 및 모든 안전 검사는 유지한다.

```sh
sudo python3 scripts/cleanup_run_images.py \
  --older-than-days 0 --keep-newest 2 \
  --keep build/autosd/demo-ota-followup \
  --keep build/autosd/demo-regular-session \
  --keep build/autosd/demo-network-fixed-session \
  --keep build/autosd/ukiboot-switch-b \
  > /tmp/run-image-cleanup-preview.json
jq '.items[] | {path, decision, reason, allocated_bytes}' /tmp/run-image-cleanup-preview.json
```

### 3. 확인한 정책으로 삭제

위 명령에 `--apply`를 추가한다. 삭제 직전 실행 중인 파일 및 파일 identity를 재검사한다.
삭제된 디스크는 복구할 수 없으며, 다른 터미널의 동시 VM 시작까지 원자적으로 차단하지는 않는다.

```sh
sudo python3 scripts/cleanup_run_images.py --apply \
  --older-than-days 0 --keep-newest 2 \
  --keep build/autosd/demo-ota-followup \
  --keep build/autosd/demo-regular-session \
  --keep build/autosd/demo-network-fixed-session \
  --keep build/autosd/ukiboot-switch-b \
  > /tmp/run-image-cleanup-result.json
jq '{mode, blocked, errors, eligible_allocated_bytes}' /tmp/run-image-cleanup-result.json
df -h build
```

이번 스크립트 검증은 임시 디렉토리의 실제 unlink 테스트와 workspace dry-run으로 수행했다.
현재 호스트의 sudo는 비밀번호가 필요하므로 스크립트를 통한 추가 실제 삭제는 하지 않았다.
앞서 회수한 42.52 GiB는 경로·의존성을 개별 확인한 19개 파일의 정리 결과다.
