# Known limitations

- Scope: one Mac15,10/J514M/T6034, 14 CPU/30 GPU cores and 36 GB nominal memory. No blanket M3 Max support claim.
- Native graphics/display components remain experimental; upstream success on other boards does not qualify this board's power/thermal behavior.
- Suspend previously returned to a black internal display while networking/kernel resumed. It has **not** been retested with the new graphics stack. Sleep/hibernate targets remain masked and lid-triggered suspend ignored. No test or setting change was performed during this mission.
- The original known-good baseline lacks panel brightness. The installed panel candidate exposes `apple-panel-bl`; the owner verified visible dimming using both keyboards when the internal display is focused. Omarchy targets the focused screen; the external dock connection exposes no connector DDC brightness control. Actual 120 fps presentation remains unmeasured. See [candidate results](j514m-candidates.md).
- External cold/startup and clamshell close/open worked. Hotplug is partially working: a later disabled-output incident required explicit compositor enable. Initial cause remains unresolved.
- Direct HDMI, multiple external monitors, external 120 Hz, HDR, display audio and other docks remain unqualified. DisplayLink support is not claimed.
- Built-in webcam capture and live preview are verified at 1080p/~30 fps; browser/video-call integration and the attached Logitech BRIO remain unqualified. Bluetooth, battery runtime, thermal/power envelope and sustained GPU compute are not qualified by this mission. Owner-reported audio/network success is distinguished from automated graphics checks.
- Root snapshots do not independently restore separate boot/EFI partitions or Apple boot policy. Disaster recovery and a clean from-scratch build have not been rehearsed.
- Published artifact hashes identify existing local packages; they do not promise reproducible binary bytes or permanent upstream artifact availability. Keep private/offline copies.
- Update preflight is reporting only; system-wide interception is not activated. All scope/solver limitations must remain visible.

Future suspend validation requires separate authorization, saved work, confirmed SSH/Tailscale reachability from another device, exact rollback artifacts, boot/EFI backups and a recovery operator. Capture pre/post kernel and display state privately, change one condition at a time, and stop on failure. This is a plan, not permission to unmask or suspend.

A focused [suspend source review](suspend-review.md) compares the exact J514M success report with our installed stack, documents the attached-display veto and a possible GPU power-retention gap. It does not qualify suspend or authorize testing.
