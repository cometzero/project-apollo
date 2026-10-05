# TC397 CAN / SIL Kit native participants

독립 TC397 QEMU의 CAN controller frame endpoint를 실제 SIL Kit CAN service에
연결한다. `vmcu-silkit` 실행 파일은 `bridge`와 `restbus` 두 역할을 제공한다.
QBox/SystemC 또는 기존 SI firmware에 SDK를 링크하지 않는다.

## 빌드

```sh
scripts/build/build_vmcu_silkit.sh --bootstrap
```

공식 SIL Kit **5.0.7**, commit `fcb625632ad82edd85e322e1ec0de6f021bff497`,
Ubuntu 22.04 x86_64 prebuilt package를
`build/qbox-apollo-qvp/vmcu-silkit/sdk/`에 내려받는다. archive SHA256은
`0f2ad1ed0a78bc1655eb6e2d451890973fdc2ab3b6b7cd73f7d5f24b86595990`이다.
필요 도구는 CMake, Ninja, C++14 compiler, Python3, curl, unzip, sha256sum이다.
libc/libstdc++/libgcc/libm과 SDK shared library는 실제 `ldd` 결과로
`build-manifest.json`에 기록한다. 원본 MIT LICENSE 및 ThirdParty/LICENSES.rst를
SDK와 함께 보존한다. SDK core 자체는 C++17이지만 이 client는 공개 API를
`-std=c++14 -Wall -Wextra -Werror -Wpedantic`으로 빌드한다.

다른 host architecture에서는 같은 source commit으로 SIL Kit를 별도 빌드하고
`cmake -S scripts/silkit -B <build> -DCMAKE_PREFIX_PATH=<installed-SilKit>`로
client를 구성할 수 있다. SDK bootstrap 스크립트의 배포 바이너리는 x86_64용이다.

## 실행 계약

Registry는 `sil-kit-registry --listen-uri silkit://127.0.0.1:0
--generate-configuration <run>/registry.yaml`로 임의의 가용 port를 선택할 수 있다.
해당 파일 생성이 완료되면 `Middleware.RegistryUri`를 두 participant에 전달한다.
registry executable은 다운로드한 package의 `SilKit/bin/`에 있다.

```sh
vmcu-silkit --role bridge --registry-uri "$registry_uri" \
  --qemu-endpoint "127.0.0.1:$can_port" --require-peer VehicleRestbus \
  --events "$run_dir/bridge.jsonl"
vmcu-silkit --role restbus --registry-uri "$registry_uri" \
  --require-peer TC397CanBridge --stdin --events "$run_dir/restbus.jsonl"
```

이 명령의 `vmcu-silkit`은 build 디렉터리의 `native/vmcu-silkit`이다.
QEMU는 별도 CAN chardev TCP server를 사용한다. network 기본값은 `VehicleCAN`,
controller 이름은 `VMCU_CAN0`/`Vehicle_CAN0`이다. 이름과 network는 CLI로
선택하며 다른 실험의 participant와 섞지 않는다. Registry 생성·외부 registry
사용·process 소유권 관리는 상위 runner 책임이다. 각 participant의
`participant_ready`와 필수 상대의 `peer_running` 로그를 확인한 뒤 시험한다.

SIL Kit autonomous lifecycle을 사용하며 communication-ready callback에서
500 kbit/s nominal, 2 Mbit/s FD를 설정하고 controller를 시작한다.
virtual-time synchronization을 활성화하지 않는다. SDK callback은 frame의
Span을 즉시 소유 배열로 복사하고 최대 256개 event queue에 넣는다. main
thread만 socket, request table, SDK 송신과 scenario를 처리한다. overflow는
명시적 오류 종료다. CAN payload의 물리 bit timing/중재/error counter는 이
simple network에서 검증하지 않는다.

## CAN1 socket contract

고정 92 bytes: `CAN1`, type byte(TX=1/RX=2/ACK=3/CONTROL=4), flags byte,
DLC byte, payload length byte, LE32 epoch/token/CAN ID/status, payload64,
앞의 88 bytes에 대한 CRC32 IEEE LE32. 남는 payload bytes는 0이어야 한다.
flags는 IDE=1, RTR=2, FDF=4, BRS=8, ESI=16이며 SDK의 flag 값으로 명시 변환한다.

- classic DLC 0..8만 지원한다. RTR의 실제 payload는 0 bytes다.
- FD DLC 0..15는 0..8,12,16,20,24,32,48,64 bytes로 해석한다.
- 표준 ID는 11 bits, 확장 ID는 29 bits다. FD+RTR 및 classic+BRS/ESI는 거부한다.
- CONTROL START=1/STOP=2가 현재 epoch를 알린다. TX token은 nonzero,
  RX token은 0이다. ACK는 epoch/token을 되돌리고 나머지 CAN 필드는 0이다.
- ACK status는 Transmitted=1/Canceled=2/Error=3/QueueFull=4다. 성공 ACK는
  실제 `AddFrameTransmitHandler`에서만 생성한다. `SendFrame` 반환이나 TCP
  write 성공은 TX completion으로 처리하지 않는다.

callback context는 dereference하지 않는 단조 증가 opaque handle이다.
2초 ACK deadline, 최대 256 pending requests, 최대 256 socket output frames를
사용한다. timeout된 handle은 재사용하지 않으며 늦은 callback을 버린다.
QEMU reconnect/epoch 변경 전 요청의 callback은 새 MCU session에 전달하지
않는다. disconnected socket의 parser/output을 비운다. 필수 restbus 부재는
TX Error이며 성공 ACK로 대체하지 않는다.

SIL Kit simple CAN은 실제 SDK callback을 통해 **항상 긍정적인 bus 전송 결과**를
발생시킨다. 따라서 이 callback은 physical CAN ACK slot 또는 상대 application의
처리 완료 증거가 아니다. application 왕복은 별도 response frame으로 검증한다.
registry 장애는 participant lifecycle 실패로 보고 상위 runner가 관리해야 한다.
자동 registry 재생성이나 가짜 CAN 성공을 이 client에서 수행하지 않는다.

## VehicleRestbus와 시험 입력

기본 restbus는 수신을 기록하며 자동 제어하지 않는다. `--stdin`에서 다음을 받는다.

```text
status
send 0x123 0 8 0001020304050607
command 1 0
quit
```

`send ID FLAGS DLC HEX`는 일반 CAN 시험용이며 raw `0x600` 제어는 거부한다.
`--echo-fixture`를 지정한 경우에만 `0x123→0x321` 및
`0x1abcde→0x1abcdf`로 같은 flags/DLC/payload를 반환한다.
`--period-ms N`은 시험용 ID `0x700` 주기 frame을 선택적으로 발행한다.

`0x510` FD32 telemetry에서 SI epoch, MCU cookie, 마지막 command sequence를
읽어 `command OP ARG`의 `0x600` FD24 payload를 만든다. reply는 `0x601`이다.
1=status, 2=AP ping, 3=PMIC rail, 4=PMIC fault는 관찰 명령이다.
5=AP recover, 6=graceful off, 7=on/wake는 **`--allow-actuation`**이 있어야
전송한다. 실제 권한·allowlist·freshness·중복 처리의 최종 책임은 MCU app이다.
필수 peer가 사라지면 restbus의 cached telemetry session도 지운다.

SIGINT/SIGTERM과 `quit`은 socket을 닫고 handler를 제거한 뒤 lifecycle을
종료한다. lifecycle 종료 대기는 최대 3초이며 실패하면 nonzero로 종료한다.
상위 runner는 자신이 시작한 registry/QEMU/participants만 회수해야 한다.

## 공식 근거

- [SIL Kit v5.0.7 release](https://github.com/vectorgrp/sil-kit/releases/tag/v5.0.7)
- [CAN service와 ACK/DLC 계약](https://vectorgrp.github.io/sil-kit-docs/api/services/can.html)
- [CMake package 사용](https://vectorgrp.github.io/sil-kit-docs/for-developers/developers.html)
- [Registry 준비 완료와 동적 port](https://vectorgrp.github.io/sil-kit-docs/utilities/utilities.html)
- [v5.0.7 simple CAN ACK 구현](https://github.com/vectorgrp/sil-kit/blob/v5.0.7/SilKit/source/services/can/SimBehaviorTrivial.cpp)
