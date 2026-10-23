"""The BSP core device probe split into independently observable checks."""

TOPOLOGY_COMMAND = (
    "( set -u; rc=0; "
    "check() { printf 'TOPOLOGY field=%s actual=%s expected=%s\\n' \"$1\" \"$2\" \"$3\"; "
    "test \"$2\" = \"$3\" || rc=1; }; "
    "check nproc_all \"$(nproc --all)\" 4; "
    "count=$(find /sys/firmware/devicetree/base/cpus -maxdepth 1 "
    "-name 'cpu@*' | wc -l | tr -d '[:space:]'); check dt_cpu_nodes \"$count\" 4; "
    "for name in possible present online; do "
    "value=$(cat /sys/devices/system/cpu/$name) || rc=1; "
    "printf 'TOPOLOGY field=%s actual=%s\\n' \"$name\" \"$value\"; done; "
    "for cpu in 0 1 2 3; do "
    "size=$(cat /sys/devices/system/cpu/cpu$cpu/cache/index3/size) || rc=1; "
    "shared=$(cat /sys/devices/system/cpu/cpu$cpu/cache/index3/shared_cpu_list) || rc=1; "
    "check cpu${cpu}_cache_size \"$size\" 4096K; "
    "check cpu${cpu}_cache_shared \"$shared\" 0-3; done; "
    "test $rc -eq 0 && echo __QBOX_BSP_CORE_TOPOLOGY_OK__ )"
)
DSU_COMMAND = (
    "( set -eu; for event in 0x002A 0x002B; do "
    "if out=$(perf stat -e arm_dsu_0/event=$event/ -- dd if=/dev/zero "
    "of=/dev/null bs=1M count=64 2>&1); then rc=0; else rc=$?; fi; "
    "printf 'DSU event=%s rc=%s\\n%s\\n' \"$event\" \"$rc\" \"$out\"; "
    "test $rc -eq 0; "
    "printf '%s\\n' \"$out\" | grep -Eq '[0-9]+[[:space:]]+arm_dsu_0/'; "
    "done; echo __QBOX_BSP_CORE_DSU_OK__ )"
)
DEVICES_COMMAND = (
    "( set -eu; test -e /dev/rtc0; hwclock >/dev/null; test -e /dev/watchdog0; "
    "grep -qw virtio_rng.0 /sys/devices/virtual/misc/hw_random/rng_available; "
    "grep -qw virtio_rng.0 /sys/devices/virtual/misc/hw_random/rng_current; "
    "hexdump -n 32 /dev/hwrng | grep -q '[0-9a-f]'; "
    "echo __QBOX_BSP_CORE_DEVICES_OK__ )"
)
