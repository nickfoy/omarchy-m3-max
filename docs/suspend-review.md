# J514M suspend source review

This is a read-only review of the running `7.2.11-16-1.2-ARCH` installation against a community success report. No sleep target was unmasked, no suspend was triggered, and no kernel/boot/configuration was changed. This does not qualify sleep or authorize a test. Exact current candidate provenance is in [panel-candidate.json](../manifests/panel-candidate.json); the earlier preserved baseline remains unchanged.

## Comparison with the successful report

[webdevtodayjason's J514M report](https://github.com/omacom/linux-aurora/issues/333#issuecomment-6764685158) describes one successful suspend/resume, followed by functioning GPU compute. The owner explicitly says no logs were captured. Its wake source, sleep duration and repeatability are unspecified; it does not qualify our dock configuration.

| Component | Reported successful machine | Our reviewed installation |
| --- | --- | --- |
| Hardware | J514M/T6034, 36 GB | Mac15,10/J514M/T6034, 36 GB |
| Kernel | aurora15 local 1.2, upstream `49a8c150d6be00f11e27d39bbb6ba5a215cf1e68` plus panel changes | aurora16 local 1.2, upstream `bed544bdf93a496ebf70ba180923bab12b6e01cf` plus external-display and panel patches |
| Loader | `c6fef490e916f6254d491f1b97ce2f2650b0cb0c` | upstream `ba130ffbeeadaa35215ed88b07ebcee3199d0be7` plus J514M external handoff correction |
| Mesa | `b7b03c5b3b8` | Same source abbreviation in installed package version; full package provenance remains in manifests |
| Hyprland / Aquamarine | 0.56.2-7 / 0.15.1-1.3 | Same versions |
| OS / system firmware | 14.7 / 26.5 | 14.7 / 27.0, captured baseline evidence |
| External enablement | No m1n1.conf; no external stack qualification in the suspend report | Explicit T6034 external opt-in, Surface TB4 dock supported but sleep unqualified |

Direct raw-source comparison between the two kernel upstream pins found identical `drivers/gpu/drm/apple/dcp.c`, `drivers/pmdomain/apple/pmgr-pwrstate.c`, `arch/arm64/boot/dts/apple/t6034.dtsi` and `t6031-pmgr.dtsi`. `g15/glue.c` differed only in the J516M display-compatible selection. This is a focused comparison, not an assertion that both whole kernels are equivalent. Local external patches modify display handling further. The loader comparison showed later J516M handoff/GPU admission additions; our additional external patch also differs from the report. No reason to downgrade the working stack was established.

## Concrete findings in our source

**Attached external display veto.** In `drivers/gpu/drm/apple/dcp.c`, `dcp_external_sleep_vetoed()` returns a refusal when a native external processor has an active Type-C route or attached cable. `dcp_platform_prepare()` returns `-EBUSY` before suspend callbacks can tear down a working tunnel. Thus a refused docked attempt must not be counted as a resume pass. Turning the monitor dark alone does not remove the current attachment guard. Preserve it.

**Potential GPU power-retention gap.** `asahi_g15_hold_power()` takes a runtime-PM hold, but does not mark the GPU syscore or otherwise explicitly retain it through system sleep. The live device tree resolves GPU power to `soc/power-management@408e80000/power-controller@110` (GFX), then `power-controller@100` (AFR). AFR has `apple,always-on`; GFX has neither that property nor `apple,min-state`. An always-on parent alone does not establish that its child stays powered. The kernel's PMGR driver only gives `GENPD_FLAG_ACTIVE_WAKEUP` to an ordinary domain found active at probe. The privileged live genpd summary was inaccessible in this review, so actual flags/off counters were not established.

[PR #288](https://github.com/omacom/linux-aurora/pull/288) addresses this mechanism by adding a system-sleep hold for retained GPU firmware. It was tested on J516C/T6031 with other patches, not on our J514M. Importantly, its source predicate is `cfg.platform == hw::Platform::DeviceTree`, labelled `t6031`; our T6034 profile also uses that enum variant. The PR description's T6031-only scope cannot be assumed to remain T6031-only if rebased onto our newer tree. It needs exact chip/board admission review, tests and dependency analysis before any adaptation. The observed gap is a plausible risk, not proof of a J514M failure or confirmation that this patch is necessary.

**Native panel support is already materially different from the original failure.** The original failure occurred on the firmware framebuffer. Our native eDP panel, GPU acceleration, panel brightness and ordinary display wake work now. That makes the old failure insufficient evidence about the current stack, but successful DPMS/lid display restoration is not a system-suspend test.

## Candidate decisions

- [PR #283](https://github.com/omacom/linux-aurora/pull/283): M3 Pro DPMS and dark-external sleep work, tested on J514S. Not an approved T6034 fix; do not remove our external guard based on that result.
- [PR #401](https://github.com/omacom/linux-aurora/pull/401): PMP wakeup-path retention, tested on M1-family hardware. Not established as a missing dependency for our J514M; do not stack it speculatively.
- [PR #419](https://github.com/omacom/linux-aurora/pull/419): built-in DP2HDMI reconnect after sleep. Skips Type-C paths; does not solve our Thunderbolt dock case.
- [PR #274](https://github.com/omacom/linux-aurora/pull/274): merged M3 Pro power/RTC work. Its board-specific DT changes do not qualify a J514M RTC alarm. Available `/sys/power/mem_sleep` on our machine is only `s2idle`; no deep-sleep mode was advertised.

## Next decision

Before proposing an actual test, inspect live GFX genpd state through a separately authenticated read-only command, and finish a narrowly scoped T6034 retention assessment of PR #288. A patch or a test each requires its own concrete proposal and owner approval. Do not treat the single community pass as a safety guarantee.

Any later approved first test should use the internal panel with all external display cables/dock disconnected, saved work, verified remote access, captured private logs and exact recovery artifacts. Verify actual suspend entry/exit, wake source, GPU rendering and panel restoration; keep automatic/lid suspend disabled, restore protective masks afterward, and stop after a failure. RTC wake must not be assumed available. Do not perform this plan merely by reading this document. See [recovery.md](recovery.md) and [known limitations](known-limitations.md).
