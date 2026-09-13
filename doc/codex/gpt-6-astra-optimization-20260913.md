# GPT-6 Astra Codex 환경 최적화

2026-09-13. 개인 환경, Apollo, `/srv/oss_contrib` 순으로 적용했다.

## 판단 기준

사용자가 지정한 [OpenAI 원문](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)을
직접 읽고, 짧고 구체적인 스킬 설명, 필요한 시점의 참고자료 로딩,
불필요한 고정 절차 제거, 작업에 비례하는 검증을 기준으로 삼았다.
`skill-creator`의 범위가 명확한 설명과 비중복 참고자료 원칙도 적용했다.
공식 문서만으로 설정 지원 여부를 추정하지 않고 설치된 Codex CLI
0.154.0의 설정 파서와 app-server를 통해 실제 로드를 확인했다.

## 변경 내용

### 개인 환경

- `~/.codex/config.toml`: Astra/medium 유지. 수동 context/compaction 한도,
  지원되지 않는 `network_access`, 제거된 feature 키, 잘못된
  `features.multi_agent_v2` 테이블을 제거했다. 승인·sandbox·trust 정책은 유지했다.
- 동일한 SessionStart 메시지를 두 번 주입하던 훅과 관련 신뢰 상태를 제거했다.
  인덱싱을 모든 탐색의 선행조건으로 만들지 않는다.
- superpowers와 ponytail의 전역 동작 주입을 비활성화했다. 플러그인 캐시를
  직접 수정하지 않았으며 GitHub/리서치/검색 등의 기능 플러그인은 유지했다.
- 중복·범용 절차 스킬 82개, 범용 에이전트 18개, 기존 prompts 디렉터리와
  HOME의 OMX AGENTS.md를 복구 가능한 백업 위치로 이동했다.
- `~/.codex/AGENTS.md`를 사용자 선호·완료 조건 중심으로 축약했다.
  글로벌 Yocto 스킬의 방대한 일반 튜토리얼을 실제 판단 기준으로 대체했다.
- QBox/SystemC/Linux/Zephyr 에이전트의 고정 문서 선독 및 특정 보드 가정을
  제거했다. 해당 역할은 주 모델을 상속한다. LazyCodex의 별도 비용 계층은 유지했다.

### Apollo

- `.codex/config.toml`의 Sol/xhigh 강제 설정과 이전 방식의 역할 등록을 제거했다.
  네이티브 `.codex/agents/*.toml` 탐색과 개인 Astra 기본값을 사용한다.
- 전문 역할 10개를 간결하게 정리했다. 복잡한 역할은 모델 상속/high,
  빠른 탐색·테스트 역할은 Terra/medium을 유지했다.
- AGENTS.md와 도메인 스킬에서 반복되는 빌드 절차·의무 위임을 제거했다.
  소유권, 외부 소스 경계, 하드웨어 모델 충실도, 증거 기준은 보존했다.
- 현재 MACHINE/CPU 수를 문서에 고정하지 않고 실제 build/conf를 확인하도록 했다.
- headless launcher를 full post-login 검증으로 오인하던 참고문서를 수정했다.
- 커널 설정 변경에서 항상 두 머신의 여러 태스크를 강제 실행하던 예제를
  영향받는 머신의 정상 signature 기반 빌드로 축소했다.

### OSS workspace

- 잘못된 `gpt-5.6-astra` 모델명, 의사 설정 테이블과 1000-agent 설정을 제거했다.
  Astra 기본값을 상속하며 MCP 명령·캐시 경로·메모리/worker 설정은 유지했다.
- AGENTS.md를 upstream 관례, 소유권, 영구 Kconfig, 검증 및 캐시 계약으로 축약했다.
- 기존 contribution harness가 참조하는 역할/스킬은 호환성을 위해 보존하되,
  6개 범용 단계 스킬을 harness 요청에만 맞는 호출 조건으로 좁혔다.
- implementation worker가 검증 계획만 남기지 않고 실제 검증까지 끝내도록 했다.
- smoke 검사가 이미 삭제된 hooks.json과 존재하지 않는 문서를 필수로 요구하던
  문제를 수정했다. 훅이 없으면 선택 기능 미설정으로 처리하고, 있으면 기존
  스키마 검사를 유지한다. 실제 AGENTS.md 존재 여부를 확인한다.

## 실제 측정

app-server `config/read`, `skills/list`를 새 프로세스에서 호출했다.
스킬 수는 활성 카탈로그 항목 수이고, 설명 길이는 문자 수이며 토큰 수가 아니다.

| 환경 | 모델 변경 | 활성 스킬 전→후 | 설명 문자 전→후 | AGENTS.md 줄 전→후 |
| --- | --- | --- | --- | --- |
| 개인 | Astra 유지 | 125→37 | 26,167→13,871 | 71→17 |
| Apollo | Sol→Astra | 134→46 | 28,674→15,282 | 352→58 |
| OSS | 잘못된 Astra 별칭→Astra | 143→55 | 28,890→16,535 | 193→55 |

HOME의 별도 326줄 OMX 지침도 활성 경로에서 제거했다.
현재 세 환경의 기본 reasoning effort는 medium이다.
이 결과는 설정/지침 규모의 개선이며 모델 품질·속도·비용 벤치마크는 아니다.

## 검증

- 각 작업 디렉터리에서 `codex app-server --strict-config --stdio </dev/null`: PASS.
- 설정 및 에이전트 TOML 41개 파싱/필수 필드 검사: PASS.
- 프로젝트 스킬과 변경한 글로벌/OSS 스킬 16개 quick_validate: PASS.
- `python3 build/codex-astra-optimization/probe.py build/codex-astra-optimization/after`:
  세 환경 Astra/medium, 스킬 로딩 오류 0.
- OSS `python3 -m pytest -q tests/test_kernel_contrib_harness.py`: 12 passed, 0.67초.
  초기에는 기존 smoke의 누락 훅/문서 요구 때문에 1 failed, 10 passed였으며 수정했다.
- OSS `python3 scripts/smoke_harness.py --workspace . --write build/codex-astra-optimization/smoke.json`: PASS.
- 두 저장소 `git diff --check`: PASS.
- 하드웨어/펌웨어/Yocto 소스 변경이 없어 이미지 빌드·게스트 부팅은 수행하지 않았다.

원본/최종 카탈로그는 Apollo `build/codex-astra-optimization/{before,after}/`에 있다.
OSS smoke 결과는 OSS `build/codex-astra-optimization/smoke.json`에 있다.
OSS의 `scripts/smoke_harness.py`, `tests/test_kernel_contrib_harness.py`는 현재
Git ignore 대상인 기존 로컬 도구다. 수정과 검증은 완료했으나 일반 git diff에는
나오지 않으므로 향후 커밋 시 추적 여부를 별도로 판단해야 한다.

## 복구 및 적용 범위

백업: `/home/cometzero/.local/share/codex-config-backups/astra-20260913.U18hM4/`.
개인/프로젝트 원본은 global, apollo, oss에 있고, 이동한 항목은 retired에 있다.
전체 복원은 이후 변경을 덮어쓸 수 있으므로 필요한 파일만 원본과 비교해 복구한다.
`retired/codex-skills`, `retired/agents-skills`, `retired/agents`, `retired/prompts`는
각각 `~/.codex/skills`, `~/.agents/skills`, `~/.codex/agents`, `~/.codex/prompts`에 대응한다.

기존 사용자 미커밋 소스와 삭제한 OSS hooks.json은 보존했다. 인증 파일,
세션/메모리 DB, MCP 캐시 데이터, nested source는 변경하지 않았다.
커밋·push는 수행하지 않았다. 현재 대화에 이미 주입된 지침은 소급 제거되지
않으므로 새 Codex 세션에서 정리된 전체 구성을 사용한다.
