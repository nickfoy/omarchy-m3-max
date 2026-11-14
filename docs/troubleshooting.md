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

## Brightness keys appear ineffective

On the [panel candidate](j514m-candidates.md), both the MacBook keyboard and external keyboard control the internal panel when it is focused. Move the pointer onto the MacBook screen and retry. Omarchy targets the focused display; the current dock connection exposes no connector DDC brightness interface for the external monitor. Use its physical menu. A backlight device alone is not proof of visible dimming; verify the panel with the owner.

## MacBook keyboard backlight

Verified on Mac15,10 / J514M with kernel `7.2.11-16-1.2-ARCH` and Omarchy `4.5.0-3`: the built-in keyboard LED device is `white:kbd_backlight`, maximum 255. It was set to zero; the existing Omarchy command raised it to 25 (10%), and the owner confirmed visible illumination. No additional kernel patch or binding override was needed.

- **Ctrl + display-brightness up:** increase keyboard illumination.
- **Ctrl + display-brightness down:** decrease keyboard illumination.

These are existing Omarchy bindings, distinct from plain display-brightness keys. They control the MacBook keyboard LEDs, not an external keyboard's own illumination. Direct checks and adjustment:

```sh
brightnessctl -d white:kbd_backlight info
omarchy brightness keyboard up
omarchy brightness keyboard down
```

Automatic ambient-light adjustment, idle/lock restoration and persistence across reboot were not qualified by this test. Upstream implementations are `bin/omarchy-brightness-keyboard` and `default/hypr/bindings/media.lua` in [Omarchy](https://github.com/omacom/omarchy); this repository documents the installed behavior rather than copying their implementation.

## Built-in webcam

Verified on Mac15,10/J514M with kernel `7.2.11-16-1.2-ARCH`: the `apple_isp` module exposes an `apple-isp` capture device. A 60-frame NV12 stream at 1920×1080 completed at approximately 29.95 fps, and the owner confirmed the live preview looked correct. No driver changes were needed. Frames were discarded; no camera images or video were saved or published.

Identify the camera by name, not a permanent video-node number:

```sh
for device in /sys/class/video4linux/*; do
  printf '%s: ' "$device"
  cat "$device/name"
done
```

In this test the built-in camera was `/dev/video1`; `/dev/video0` was the hardware video decoder, and other nodes belonged to an attached Logitech BRIO. Recheck before using these example commands:

```sh
# Brief capture to discard, with a timeout:
timeout 15s v4l2-ctl -d /dev/video1 --stream-mmap=4 --stream-count=60 --stream-to=/dev/null
# Optional visible preview; opens the camera for up to 25 seconds:
timeout 30s ffplay -hide_banner -loglevel error -f v4l2 -input_format nv12 -video_size 1920x1080 -framerate 30 -window_title 'MacBook built-in camera test' -autoexit -t 25 /dev/video1
```

Open the lid before testing. Browser permissions, PipeWire/portal integration, conferencing apps and the external BRIO were not qualified. The installed GStreamer setup lacked `v4l2src`; FFplay provided the successful preview without installing packages. Camera support comes from the upstream Aurora/Asahi stack credited in [third-party notices](../THIRD_PARTY_NOTICES.md).
