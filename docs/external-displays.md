# External displays and clamshell

Verified: Samsung **C49J89x**, 3840×1080 at approximately 59.968 Hz through a **Microsoft Surface Thunderbolt 4 Dock**, alongside internal 3024×1964 at 120 Hz. Kernel messages explicitly routed the display to **Thunderbolt DP tunnel dpin0**. This evidence establishes Thunderbolt DisplayPort tunneling; it is not inferred from USB-C or from USB hub enumeration. DisplayLink was not used for this arrangement.

The local backport supplies T6034 external processor dcpext0 and Type-C routes, with a matched loader memory/display-DART handoff. It uses `chosen.asahi,t6034-dispext=1`. The J514M loader profile must dispatch external handoffs; enabling only the J516M profile does nothing here. Nodes remain disabled until the validated handoff. See [build sources](building.md).

Connector numbering varies by port (DP-3 and DP-1 were observed). Run:

```sh
./scripts/check-hardware.sh --json
./scripts/verify-displays.sh --json
hyprctl monitors all -j
```

Plug the dock/monitor in before boot for the verified startup arrangement. A single unplug/replug test succeeded, but a later reconnect left the compositor output disabled despite a present EDID and usable modes. Explicitly enabling that output at the working 60 Hz restored the picture. This remains a reliability limitation; do not describe hotplug as fully qualified.

Clamshell close/open passed: existing Omarchy lid handling disabled the internal output with the lid closed, external keyboard/mouse/display remained usable, and the internal panel returned on opening. Sleep was not entered. Preserve the existing ignore-lid policy and sleep masks. An intentionally disabled clamshell panel or disconnected external screen is not a regression.

No direct HDMI, second external display, external 120 Hz, HDR or dock-attached suspend qualification is claimed. Available EDID modes are not evidence those modes work. `config/hyprland/monitors.example.lua` is an optional example, not an automatic replacement for user configuration.
