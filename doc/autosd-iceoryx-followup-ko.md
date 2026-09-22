# AutoSD iceoryx2 후속 실행 준비

## 결과와 범위

공식 데모가 사용하는 동일 upstream publisher/subscriber를 AArch64 ELF로
cross-build하고 Apollo standalone QEMU guest에서 root↔QM 실제 통신을
검증했다. **빌드 PASS, 공식 permissive 조건 PASS, 공유 경로를 qm_file_t로
제한적으로 재라벨한 Enforcing 조건 PASS**다. 기존 user_tmp_t 라벨의
Enforcing 시험은 실패했으며 그 증거를 보존했다.
공식 Bazel RPM을 생성한 결과가 아니라 upstream에서 문서화한 Cargo 예제
빌드 경로를 사용한 Apollo용 실행 payload다. root↔QM 통신 성공도 ASIL-B
인증이나 실시간 지연 보장을 의미하지 않는다.

| 실행 조건 | 결과 | 실제 관측 |
|---|---|---|
| Enforcing, 기존 user_tmp_t | FAIL | publisher 전송 시작, QM subscriber InternalError; qm_t의 user_tmp_t open/write AVC |
| 명시적 임시 permissive | PASS | QM subscriber 14건 수신; 종료 후 Enforcing 복구 확인 |
| Enforcing, /tmp/iceoryx2만 qm_file_t | PASS | QM subscriber 14건 수신; 새 node/data/service 파일도 qm_file_t; 시험 구간 kernel journal `-- No entries --` |

증거 디렉터리는 모두 `build/autosd/` 아래다.

- `demo-qm-iceoryx-enforcing/`: 최초 실패와 return code 1
- `demo-qm-iceoryx-diagnose/`: 구체적인 AVC와 기존 파일 라벨
- `demo-qm-iceoryx-permissive/`: 공식 permissive 비교, Enforcing 복구
- `demo-qm-iceoryx-label-trial/`: Enforcing 재라벨 비교, x=4부터 x=17까지
  14개 TransmissionData 및 y=3*x payload 확인

`qm_file_t`는 기존 QM domain의 파일 접근을 활용하는 기능 검증이다.
iceoryx 전용 정책이나 앱별 least-privilege 접근 제어를 추가·검증한 결과가
아니다. 해당 시험 구간에 새 kernel journal entry가 없었다는 관측도 전체
SELinux 정책의 안전성을 증명하지 않는다. QBox 실행은 아직 미검증이다.

## 입력과 재현

- 공식 데모: `autosd/sig-docs/demos/iceoryx2_ipc/`
- source: `autosd/iceoryx2`, revision
  `bb0cb8a01bc5cc7b7462e258e04f3d56bf988496`
- Rust 1.83.0 및 AArch64 standard library: 작업 전용
  `build/autosd/demo-iceoryx-followup/toolchains/rustup/`
- Cargo source/cache: `autosd/.iceoryx-cargo/`
- target: `aarch64-unknown-linux-gnu`, 기존 호스트 AArch64 GCC 및 libclang 18
- `Cargo.lock`을 변경하지 않고 `--locked`로 release 빌드
- 공식 Bazel 설정의 native RPM architecture 선택과 별도로 Cargo의
  cross-compilation 경로를 사용했다. 예제 Rust source는 수정하지 않았다.

```sh
bash scripts/autosd_demo/iceoryx_build.sh
```

산출물은 `build/autosd/demo-iceoryx-followup/payload/`의
`publisher`, `subscriber`, `iceoryx2.toml`, `config/iceoryx2.toml`이다.
실제 빌드 로그는 `build-second.log`에 있다. 최초 `build.log`는 task-local
CARGO_HOME에서 rustup self-update 경로를 찾지 못한 실패다. `--no-self-update`
추가 후 빌드 성공했으며 호스트 전역 toolchain이나 binfmt는 변경하지 않았다.

| 파일 | SHA-256 |
|---|---|
| publisher | `639c4c6f835cd5ab8998dead3ddb1a0f77b9be3afe97c4e32ebf4ccea2aaa054` |
| subscriber | `044007076eb268880bb8f4062bde772552ab9e093fd860cdd712700dfdc64755` |
| iceoryx2.toml | `2eb5e22cbbc875d37cc61a6b9f090d4bbe014c0112a5b9ff19653c4ec0a1a70e` |

## 실제 실행 전제

root와 QM에 같은 절대 경로의 payload를 배치한다. 예를 들어
`/var/tmp/apollo-iceoryx/{publisher,subscriber,config/iceoryx2.toml}`을 사용하면
read-only `/usr`를 수정할 필요가 없다. 애플리케이션은 작업 디렉터리의
`config/iceoryx2.toml`을 검색한다.

공식 manifest처럼 `/tmp/iceoryx2`를 root와 QM이 공유해야 하며 `services`,
`nodes` 하위 디렉터리도 필요하다. 공식 예제는 QM memory max/high를 infinity,
SELinux를 permissive로 설정한다. 기존 Enforcing guest를 무단 변경하지 않고
그대로 실행한 결과와 permissive 전용 데모 결과를 구분해야 한다.

준비된 guest에서 아래 probe를 실행할 수 있다. 기본 실행은 SELinux 모드나
QM volume 구성을 변경하지 않는다. 실패 시 kernel journal과 최근 AVC를
수집한다. AVC 수집이 불가능한 환경에서는 해당 오류도 로그에 보존한다.

```sh
bash iceoryx_guest_probe.sh /var/tmp/apollo-iceoryx /var/tmp/iceoryx-run-1
```

이번 실제 시험은 root와 QM의 `/opt/apollo-iceoryx` 경로를 사용했다.
`scripts/autosd_demo/iceoryx_guest_setup.sh PAYLOAD_DIR --qm-shared-label`은
기존 QM drop-in을 보존하면서 전용 `30-apollo-iceoryx.conf`로 공유 volume을
구성하고 `/tmp/iceoryx2`만 `qm_file_t`로 재라벨한다. 이 옵션은 명시적으로
선택해야 하며 생략 시 원래 SELinux 라벨로 시험한다. `/tmp`는 volatile이므로
재부팅 후 publisher/subscriber 실행 전에 setup을 다시 실행해야 한다.
재부팅 후 라벨 지속성 검증이나 production용 영구 fcontext 정책 구현은
이번 결과에 포함하지 않는다.

Enforcing에서 실패하여 공식 permissive 조건과 비교해야 할 때만 별도 private
guest에서 `--private-guest-permissive`를 명시할 수 있다. 원래 Enforcing이면
시험 동안만 permissive로 전환하며 EXIT/INT/TERM 처리에서 Enforcing으로
복구한다. SIGKILL이나 guest crash는 trap 실행을 보장하지 않으므로 재접속하여
상태를 확인해야 한다. 초기/시험 중/종료 후 모드와 comparison flag를 기록하여
permissive 성공을 Enforcing 성공으로 보고하지 않는다.

publisher의 `Send sample`과 QM subscriber의 `received: TransmissionData`를
각각 3회 이상 확인한다. 실행은 bounded timeout을 사용하고 로그와 SELinux
모드, QM inspect 정보를 보존한다. 위 결과표는 이 probe를 실제 private
Apollo QEMU guest에서 실행한 결과다.

기존 `demo-iceoryx-preflight`에서 RPM 미설치는 유효한 차단 근거지만
`/usr/bin/iox2` 부재는 이 데모의 실행 파일 계약과 무관하다. 공식 RPM은
publisher/subscriber를 제공한다.

## QBox 교차 실행

동일 payload와 opt-in `qm_file_t` 조건을 QBox AP-only에서도 실행했다.
`build/autosd/demo-qm-followup-qbox-recheck-2/console.log`에서 Enforcing 상태의
publisher 전송 및 QM subscriber의 실제 14회 수신과 정상 종료를 확인했다.
상세 로그는 `build/autosd/demo-qm-followup-qbox-recovered-evidence/`의
`apollo-followup-recheck.eIAZ4Q/iceoryx/`에 보존했다. 최초 회수 archive는
생성 중 종료로 손상되어 증거에서 제외했고, 정상 종료한 디스크에서
read-only로 재회수하여 완전성을 검사했다.

첫 cold boot의 공유 디렉터리 누락은 tmpfiles 설정으로 보완했다.
다음 cold boot에서 디렉터리 자동 생성과 QM 기동을 확인했지만 앱 실행용
`qm_file_t` opt-in 재라벨은 별도로 필요하다. 지연·안전성·앱별 최소권한
검증으로 확대하지 않는다.
