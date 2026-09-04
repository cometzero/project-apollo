# Apollo FVP Log-Backed Boot

Build the selected Yocto image first:

```bash
./yocto_build.sh --machine apollo-fvp
```

Run the headless log-backed gate with the deployed FVP configuration:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp.fvpconf \
  --out-dir build/fvp-boot/apollo-fvp \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
```

Inspect `result.json`, `summary.txt`, `fvp_stdout.log`, and every
per-UART log before reporting PASS. Build completion or an interactive tmux
session is not runtime evidence.
