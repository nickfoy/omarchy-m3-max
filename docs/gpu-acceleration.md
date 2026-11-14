# Verify actual acceleration

Run `scripts/check-hardware.sh --json`, then `scripts/verify-gpu.sh --json` in the graphical user session. The verifier is read-only and returns PASS, FAIL or UNKNOWN (exit 0, 1, 2). PASS needs a live hardware EGL renderer and a render node bound to the expected GPU driver; enumeration alone does not suffice. Software renderer strings such as llvmpipe/softpipe are failures. Missing tools/session evidence remains UNKNOWN.

Manual evidence collected on the verified host:

```sh
uname -r
ls -l /dev/dri
readlink -f /sys/class/drm/renderD128/device/driver
eglinfo -B
hyprctl systeminfo
ps -C Hyprland -o pcpu,pmem,comm
vmstat 1 3
```

Observed renderer: **Apple M3 Max (G15C B1)**; driver **asahi-g15**. Original llvmpipe load approached ten CPU cores; afterward observed Hyprland idle was about 1–3% of one core and aggregate CPU idle 96–98%. These samples depend on workload and are not performance promises. `/sys/class/drm` names can change; the script discovers render nodes rather than trusting a fixed path.

An EGL client probe is not direct proof of Hyprland's own selected renderer. The script separates those evidence sources; missing compositor renderer introspection is reported, not filled in from the EGL process. Vulkan enumeration, if available, establishes a device/loader path, not compute correctness or long-run qualification. No heavy benchmark or suspend test is required.

Use source pins and full firmware identity checks in the matched kernel/loader/Mesa combination. Do not use generic firmware-prefix overrides from another board. Details: [building](building.md), [upstream](upstream-references.md).
