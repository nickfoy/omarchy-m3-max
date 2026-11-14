# Troubleshooting without replacing the working stack

First run the hardware gate and both verifiers. Preserve output privately; do not upload raw logs. Check the installed local baseline before changing packages.

| Symptom | Inspect first | Next step |
| --- | --- | --- |
| llvmpipe / high compositor CPU | GPU verifier, driver/render node, running kernel vs installed versions | Review matched kernel/loader/Mesa and boot evidence; use recovery plan |
| External screen dark | DRM connected state vs compositor active/disabled, dock authorization, EDID/modes, DCP routing | Keep lid open; preserve logs; restore previously working mode only with approval |
| Monitor connected but disabled | `hyprctl monitors all -j` | A runtime rule may preserve disabled state unless explicitly cleared; owner-approved example below |
| Brightness unavailable | `/sys/class/backlight` | Current baseline has no interface; do not call this a new regression |
| Internal screen dark after sleep | SSH/TTY availability and suspend protections | Do not repeat experiments; preserve logs and use approved recovery |
| Boot mismatch | boot consistency check | Do not reboot until file mismatch is understood |

For an owner-approved recovery after confirming the connector and last working mode, this baseline used Lua monitor syntax:

```sh
hyprctl eval 'hl.monitor({ output = "DP-3", mode = "3840x1080@60", position = "auto", scale = 1, disabled = false })'
```

`DP-3` is an example, not a universal connector. Re-enabling recovered one incident; this is not a root-cause fix or automatic service. Do not apply 120 Hz just because it appears in EDID. Preserve the manual SUPER+ALT+W display-wake binding; its exact current Lua command is in the example configuration.

For kernel evidence inspect relevant `asahi-g15`, `apple-dcp`, DART and Thunderbolt messages locally. Remove MAC/IP addresses, serials, UUIDs, account paths, SSIDs and unrelated personal logs before sharing even a short excerpt. The inventory tool uses an allowlist rather than pretending broad regex redaction makes arbitrary logs safe.
