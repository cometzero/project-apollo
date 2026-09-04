# Apollo QBox Full-System Runbook

지원되는 build와 runtime 절차는
`doc/apollo-qvp-yocto-qbox-runbook.md`에 통합되어 있다.

```bash
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp

./yocto_build.sh
./run_qbox_yocto.sh
```

구조화된 runtime evidence가 필요하면 다음을 사용한다.

```bash
./run_qbox_yocto.sh --headless --exit-after-pass
```

QBox provider, firmware, kernel, root filesystem은 모두 같은 Yocto
generation의 배포 artifact와 `.qboxconf`에서 해석해야 한다.
