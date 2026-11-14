# Compatibility

Verified machine: **Apple MacBook Pro Mac15,10 / J514M / T6034**, 14-inch M3 Max, 14 CPU / 30 GPU cores, 36 GB nominal RAM. Unless a candidate is explicitly identified, results refer to the exact [known-good package/firmware manifest](manifests/known-good.json), not every M3 Max or any arbitrary Aurora release.

| Feature | Status | Evidence / limitation |
| --- | --- | --- |
| Native installation / boot | Verified working | Official installer origin, current custom kernel booted |
| CPU | Verified working | 14 logical CPUs; light desktop sample, not a stress qualification |
| GPU acceleration | Experimental; verified working | Apple M3 Max EGL renderer and bound render node |
| Internal display | Verified working | 3024×1964, scale 2 |
| Internal high refresh | Verified working | Selected 120 Hz |
| Display brightness | Verified working on panel candidate | Kernel `7.2.11-16-1.2-ARCH`, `apple-panel-bl` max 500; owner confirmed built-in and external keyboard with internal screen focused. Original baseline lacks this fix; see [candidate manifest](manifests/panel-candidate.json). |
| USB-C / Thunderbolt external display | Experimental; partially working | Samsung C49J89x 3840×1080 ~60 Hz via Surface TB4 Dock; startup works, later disabled-output incident |
| HDMI external display | Not tested | No direct-HDMI claim |
| Multiple external displays | Not tested | One external plus internal verified |
| Clamshell close/open | Verified working | Internal disabled on close, external usable; both active after open; no suspend |
| Wi-Fi | Verified working | Owner-confirmed use |
| Bluetooth | Not tested | No dedicated qualification in this mission |
| Audio / speakers | Verified working | Owner-confirmed; dock/display audio not qualified |
| Trackpad / keyboard | Verified working | Owner-confirmed daily use |
| Built-in keyboard backlight | Verified working | `white:kbd_backlight`, range 0–255; command set 0 → 25 (10%), owner confirmed illumination. Existing Omarchy Ctrl + display-brightness keys; no patch added. Tested on kernel `7.2.11-16-1.2-ARCH`. |
| External keyboard / mouse | Verified working | Through dock, including clamshell |
| Webcam | Not tested | No capture performed during this mission |
| Suspend / resume | Not working previously; current stack not tested | Earlier black-screen failure; deliberately disabled |
| Battery / power management | Partially working | Usable desktop/charging; no battery-runtime, thermal or power qualification |
| Tailscale / SSH | Verified working, owner report | No credentials/network topology published; recovery connectivity must be rechecked before a change |
| External 120 Hz | Not tested | Advertised only; never applied |

“Verified working” describes the stated test, not production certification. Contributors must provide exact model/board/SoC, package/firmware versions, setup and reproducible evidence. New submissions remain **unverified** until reviewed; do not extrapolate between J514M/J516M/J514C/J516C.
