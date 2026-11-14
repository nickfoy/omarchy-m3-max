# Native Omarchy on the 14-core M3 Max

A reproducibility, verification and recovery reference for **Mac15,10 / J514M / T6034**: the 14-inch MacBook Pro with 14 CPU cores, 30 GPU cores and 36 GB memory. This is a community project, not an official Omarchy, Aurora or Asahi distribution. Other M3 Max variants need their own evidence.

The current configuration is experimental. The [versioned baseline](manifests/known-good.json) is authoritative; [compatibility](COMPATIBILITY.md) separates measured results from untested features.

## What works

- Native boot and Apple M3 Max GPU acceleration, replacing `llvmpipe` software rendering.
- Internal 3024×1964 display at 120 Hz.
- Samsung C49J89x ultrawide at 3840×1080, about 60 Hz, through a Microsoft Surface Thunderbolt 4 Dock.
- Internal/external simultaneous operation; clamshell close/open with external keyboard and mouse.
- Owner-confirmed Wi-Fi, keyboard, trackpad, speakers/audio, Tailscale and SSH.

**Limits:** the original baseline lacks brightness support; the installed [panel candidate](docs/j514m-candidates.md) now has owner-verified brightness from both keyboards when the internal screen is focused; suspend/resume is unqualified and deliberately disabled; HDMI and multiple external displays are untested. One later reconnect left the external output disabled until explicitly re-enabled: hotplug is **partially working**, not fully qualified. External 120 Hz was advertised but never applied or tested. See [limitations](docs/known-limitations.md).

## Start with verification

```sh
git clone https://github.com/nickfoy/omarchy-m3-max.git
cd omarchy-m3-max
./scripts/check-hardware.sh --json
./scripts/compare-baseline.sh manifests --json
./scripts/verify-gpu.sh --json
./scripts/verify-displays.sh --json
```

Read [installation](docs/installation.md) before any package changes. **A working system that differs from this baseline is not automatically broken.** No script here repartitions a disk, installs a graphics stack, enables sleep, or activates an update guard.

## Install with an AI Agent

1. Open Codex, Claude Code, or another coding agent on the target machine.
2. Give it this repository URL: https://github.com/nickfoy/omarchy-m3-max.
3. Copy the complete [installation prompt](prompts/install.md).
4. Review its hardware evidence, recovery route and proposed changes; explicitly approve disruptive work.
5. Let the agent apply only that approved plan and run verification.

The prompt helps investigate an experimental Apple Silicon configuration; it does not guarantee compatibility. Agents first read [AGENTS.md](AGENTS.md), identify the exact board/SoC, and stop before critical changes on unsupported or unidentified hardware. No agent-specific plugins are required.

## Update with an AI Agent

Copy [prompts/update.md](prompts/update.md) into your agent. It preserves the installed baseline, runs preflight and reviews candidates before requesting approval for critical changes. The repository provides reporting, **not active update interception**.

```sh
./scripts/preflight-update.sh --json
./scripts/preflight-update.sh --refresh --scope omarchy --json
./scripts/capture-baseline.sh --output "$HOME/.local/state/omarchy-m3-max/baseline-$(date -u +%Y%m%dT%H%M%SZ)" --json
```

`--refresh` refreshes only a private staging database. It does not update live pacman metadata or install packages. SAFE means no identified protected boundary; it is never a guarantee. Read [update policy](docs/update-policy.md) for coverage limits, critical approvals and the proposed enforcement design.

## Reproduce and recover

- [Known-good baseline](docs/known-good-baseline.md), [change history](docs/change-history.md), [build instructions](docs/building.md).
- [GPU checks](docs/gpu-acceleration.md), [external displays](docs/external-displays.md), [troubleshooting](docs/troubleshooting.md).
- [Recovery](docs/recovery.md): a root snapshot alone does **not** restore separate `/boot`, the EFI partition or Apple's boot policy. Keep exact packages and private backups offline.
- [Upstream references](docs/upstream-references.md), [contributing](CONTRIBUTING.md), [security/privacy](SECURITY.md).

Original scripts/docs are MIT; upstream work retains its own licenses. Credit and redistribution boundaries are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). No firmware, binary packages, credentials or private recovery images are published.

## J514M fixes under evaluation

[Panel brightness](docs/j514m-candidates.md) is verified on the installed candidate with both the built-in and external keyboard when the MacBook screen is focused. Actual 120 fps presentation remains unmeasured on this machine. Candidate patches are not part of the known-good baseline until hardware validation and owner approval.

Upstream driver and bootloader work is credited in the [artifact-by-artifact attribution map](THIRD_PARTY_NOTICES.md#attribution-and-provenance-map), including BTNG-studio’s external-display patches and Scott Jones’s J514M panel fix. This community repository preserves and adapts that work; it is not an official Omarchy, Aurora or Asahi distribution.

Built-in keyboard illumination is verified using Omarchy’s existing **Ctrl + display-brightness up/down** shortcuts; see [keyboard-backlight troubleshooting](docs/troubleshooting.md#macbook-keyboard-backlight). No additional patch is needed.
