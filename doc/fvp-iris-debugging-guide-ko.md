# Apollo FVP Iris 디버깅

FVP 디버깅 입력은 Yocto 빌드 결과만 사용한다.

```bash
./yocto_build.sh --machine apollo-qvp
./run_fvp.sh --machine apollo-qvp --debug linux
```

지원 target은 `rse`, `si_cl0`, `si_cl1`, `tf-a`, `u-boot`,
`linux`이다. FVP는 native GDB stub 대신 Iris를 제공하므로 launcher가
Yocto의 `lite-cornea-native`를 통해 GDB를 연결한다.

자동화된 breakpoint probe는 다음과 같이 실행한다.

```bash
./run_fvp.sh --machine apollo-qvp \
  --debug tf-a \
  --debug-mode probe \
  --debug-timeout 600 \
  --out-dir build/agent-debug/fvp-tfa
```

성공 판정에는 `debug-result.json`의 `status=passed`,
`breakpoint_hit=true`, expected/observed PC 일치,
`cleanup_completed=true`가 모두 필요하다. 함께 생성된 `gdb.log`,
`fvp_stdout.log`, UART 로그에서 source location과 가장 이른 실패
handoff를 확인한다.

일반 boot 로그를 먼저 분석하고 실패 domain을 좁힌 뒤 Iris/GDB를
사용한다. 빌드 성공이나 열린 tmux pane만으로 runtime PASS를 주장하지
않는다.
