#!/usr/bin/env bash
# Run only inside a disposable AutoSD guest, using its matching Yocto archive.
set -euo pipefail
archive=${1:?Usage: install_guest_modules.sh matching-modules.tgz [--load|--install-only]}
mode=${2:---load}
[[ "$mode" == --load || "$mode" == --install-only ]]
release=$(uname -r)
prefix="lib/modules/$release/"
[[ $(id -u) == 0 ]]
echo "Validating module archive for $release ($mode)"
# Do not extract the archive's lib/ directory over AutoSD's usr-merge symlink.
# Restrict this helper to the expected trusted Yocto modules archive layout.
tar tzf "$archive" | awk -v prefix="$prefix" '
  $0 == "lib/" || $0 == "lib/modules/" { next }
  index($0, prefix) != 1 || $0 ~ /(^|\/)\.\.(\/|$)/ { bad=1 }
  END { exit bad }
'
tar tzf "$archive" | grep -Fx "$prefix" >/dev/null
mkdir -p /usr/lib/modules
echo 'Extracting matching kernel modules'
tar xzf "$archive" -C /usr/lib/modules --strip-components=2 "$prefix"
echo 'Restoring SELinux labels and module dependency indexes'
restorecon -R "/usr/lib/modules/$release"
depmod -a "$release"
if [[ "$mode" == --install-only ]]; then
    echo 'MODULE_INSTALL_PASS (next matching kernel boot required; no live module replacement)'
    exit 0
fi
modinfo -F vermagic bridge
modprobe bridge
modprobe nft_ct
modprobe nft_nat
modprobe nft_masq
modprobe nft_reject_inet
modprobe nft_limit
modprobe nft_fib_ipv4
modprobe nft_fib_ipv6
modprobe nft_fib_inet
echo 'MODULE_DEPLOYMENT_PASS (not a container network qualification)'
