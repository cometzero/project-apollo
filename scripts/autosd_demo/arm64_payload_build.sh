#!/usr/bin/env bash
# Compile only small ARM64 applications; kernels come from validated Yocto deploys.
set -euo pipefail
root=/workspace
out=/output
mkdir -p "$out/payload"
test "$(gcc -dumpmachine)" = aarch64-redhat-linux
for app in workload latency-probe; do
 gcc -static -O2 -Wall -Wextra -Werror "$root/autosd/customization/apps/$app.c" -o "$out/payload/$app"
done
cmake -S "$root/autosd/pfdi" -B "$out/pfdi-build" -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release
cmake --build "$out/pfdi-build" -j"${JOBS:-2}"
DESTDIR="$out/pfdi-stage" cmake --install "$out/pfdi-build"
mkdir -p "$out/pfdi-stage/usr/lib64" "$out/pfdi-stage/etc/pfdi" "$out/pfdi-pack"
cp -a "$out/pfdi-stage/usr/lib/"*.so* "$out/pfdi-stage/usr/lib64/"
rm -rf "$out/pfdi-stage/usr/lib" "$out/pfdi-stage/usr/include"
cd "$out/pfdi-pack"
export PYTHONPATH="$root/autosd/pfdi/pfdi-demo/pfdi-tool"
python3 -c 'from pfdi_tool.run import main; main()' generate 0 40 60 1 4 .
python3 -c 'from pfdi_tool.run import main; main()' pack .
cp pfdi_test_config_0.pack "$out/pfdi-stage/etc/pfdi/"
mkdir -p "$out/pfdi-stage/usr/lib/python3.12/site-packages" "$out/pfdi-stage/usr/share/licenses/apollo-pfdi"
cp -a "$root/autosd/pfdi/pfdi-demo/pfdi-tool/pfdi_tool" "$out/pfdi-stage/usr/lib/python3.12/site-packages/"
cp "$root/autosd/pfdi/license.rst" "$out/pfdi-stage/usr/share/licenses/apollo-pfdi/"
printf '#!/usr/bin/python3\nfrom pfdi_tool.run import main\nmain()\n' > "$out/pfdi-stage/usr/bin/pfdi-tool"
chmod 755 "$out/pfdi-stage/usr/bin/pfdi-tool"
