# Existing native Omarchy installation

This repository does not install an operating system or partition a disk. Begin with the [official Omarchy Mac installer](https://github.com/omacom/omarchy-mac-installer) and its current hardware guidance. Preserve macOS/Apple recovery and encryption. An installer allowing a model to boot is not proof of graphics qualification.

1. Read AGENTS.md and COMPATIBILITY.md; run `scripts/check-hardware.sh --json` before any workflow. Only Mac15,10/J514M/T6034 is verified here. Investigate similar variants independently; stop critical changes for unidentified/unsupported hardware.
2. Run `scripts/inventory.sh --json`, `scripts/compare-baseline.sh manifests --json`, `scripts/verify-gpu.sh --json` and `scripts/verify-displays.sh --json`. A differing working system should be preserved rather than replaced.
3. Review the exact sources, patches, dependencies, licenses and toolchain in [building.md](building.md). Do not fetch a moving `latest` kernel/loader pair or apply an M3 Pro/other M3 Max firmware override.
4. Establish private rollback artifacts and a working non-graphical recovery route using [recovery.md](recovery.md). Capture the current package database, root snapshot and separate boot/EFI archives. Confirm encryption access without publishing it.
5. Present exact candidate versions, dependent packages, package/hook effects and verification/recovery plan. Obtain explicit owner approval before boot/graphics changes. This document is not blanket approval to run root commands.
6. Build reviewed sources as a non-root user. Inspect resulting packages and perform a full dependency-consistent transaction check. Use platform package hooks to rebuild initramfs, UKI and Stage 2; avoid manually copying unrelated DTBs into a live boot chain.
7. After the approved transaction, use `OMARCHY_BOOT_CHECK_ALLOW_PENDING_REBOOT=1 omarchy-apple-silicon-boot-check --boot-chain` with appropriate privilege. This check uses temporary read-only ESP mounts. If it fails, resolve it before reboot. Request reboot approval separately.
8. On return run GPU/display checks and compare against the prior baseline. A visible desktop is insufficient. Test the intended dock arrangement without suspend. Promote the new baseline only with owner approval.

The earlier GPU enablement required Aurora16 plus matched m1n1 and Mesa T6034 support. External output additionally requires this project's reviewed local kernel/loader changes. Exact versions and hashes live in manifests; source references are in [upstream-references.md](upstream-references.md). This does not certify newer or older combinations.

Do not unmask sleep targets, alter lid behavior, overwrite monitor settings, change firmware/Stage 1, weaken encryption or erase macOS as part of installation. Raw backups and proprietary firmware must stay private.
