# Apollo QBox Full-System 빠른 시작

현행 QBox 흐름은 Yocto artifact와 배포된 `.qboxconf`만 사용한다.

```bash
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp
```

제품 image는 다음과 같이 빌드하고 실행한다.

```bash
./yocto_build.sh
./run_qbox_yocto.sh
```

비대화형 검증은 다음 명령을 사용한다.

```bash
./run_qbox_yocto.sh --headless --exit-after-pass
```

상세 artifact 경로와 판정 기준은
`doc/apollo-qvp-yocto-qbox-runbook.md`를 따른다.
