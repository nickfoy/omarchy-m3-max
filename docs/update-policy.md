# Report-only update policy

Run `scripts/preflight-update.sh --json --scope pacman`. This reads cached repository metadata and uses a private copied package database. `--refresh` downloads fresh repository databases under private state using fakeroot; neither mode updates live sync databases, installs packages, executes package hooks, or changes pacman configuration. Network failure is BLOCKED. It needs the installed pacman/fakeroot tools and a populated `manifests/known-good.json` package map and hardware object. Hardware must pass `scripts/check-hardware.sh --json` as VERIFIED.

Exit codes: SAFE=0, REVIEW REQUIRED=2, BLOCKED=1. SAFE means a complete supplied scenario has no identified protected boundary. REVIEW REQUIRED means a protected boundary, stale repository metadata, or broader Omarchy work needs human assessment. BLOCKED means incomplete/invalid metadata, solver failure, unknown hardware, explicit incompatibility, or ignored packages. No status installs or approves anything.

**Runtime limitation:** pacman's print output cannot establish full removal operations, incoming file paths or scriptlets. Current runtime inspection returns REVIEW REQUIRED after a clean candidate solve, and BLOCKED on solver diagnostics or failure. It identifies candidate protected changes without claiming exact transaction verification. A future transaction-aware libalpm reader is needed before a runtime SAFE verdict or exact approval. It does not freeze packages or prevent unrelated updates.

## Simulated candidate plans

`--plan candidate.json` assesses a supplied simulation, independently of runtime hardware. Its output has `simulated: true`; it is never approval. Required schema:

```json
{
  "schema_version": 1,
  "hardware_status": "VERIFIED",
  "metadata_fresh": true,
  "complete": true,
  "solver_success": true,
  "ignored_packages": [],
  "incompatibilities": [],
  "transactions": [
    {
      "name": "example-editor",
      "old_version": "1",
      "new_version": "2",
      "operation": "upgrade",
      "depends": [], "provides": [], "conflicts": [], "replaces": [],
      "files": []
    }
  ]
}
```

Versions are strings (or null for the absent side of an install/remove). Operations: install, upgrade, remove, downgrade, reinstall. Dependency fields contain pacman-style package expressions, including versioned provides. Files are paths relative to installation root. Complete must mean the author supplied the whole solved transaction and relevant metadata; setting it true does not cause this tool to validate that assertion independently. Do not use arbitrary hand-written plans to authorize real updates.

Protection groups and reasons live in `config/pacman/protection-policy.json`: kernel/DTB/boot chain, graphics/display, and policy/update machinery. Direct dependencies, aliases, conflicts and replacements touching protected names require review, as do protected file prefixes. This is one-hop analysis, not full reverse-dependency/ABI closure. A future exact reader must resolve virtual/versioned providers, removals and dependency closure with reasons per boundary. New firmware/boot package names also require policy maintenance. No IgnorePkg policy or selective partial upgrade is introduced.

## Installed Omarchy scope

The observed installed updater snapshots, updates signing keys, upgrades system packages, runs migrations and orphan removals, hooks and AUR/tool updates, then checks boot content. Its keyring step refreshes live repositories before the main full transaction. Its boot lifecycle check can rebuild content after snapshot rollback. Therefore report-only mode does not invoke either updater or lifecycle verification. `--scope omarchy` always requires review for those outer actions; a package-only plan cannot approve the complete updater.

The installed direct-upgrade hook trusts `OMARCHY_UPDATE_PACMAN` and `OMARCHY_ALLOW_DIRECT_PACMAN`. These indicate routing/bypass only; they are not this project's approval mechanism. Direct `pacman -Syu`, Omarchy's keyring pre-step, full upgrade, package removals and AUR installs all need coverage in future enforcement.

The [upstream Omarchy entrypoint](https://github.com/omacom/omarchy/blob/master/bin/omarchy-update) was checked on 2026-11-14 and delegates to other updater helpers; it differs from the installed script. Treat installed source capture as machine evidence, and upstream as context rather than proof of installed behavior.

## Proposed guard: not installed

Activation is a separate approved change. An independent systemwide PreTransaction hook would cover Install, Upgrade and Remove, fail closed at protected boundaries, and preserve the existing Omarchy routing hook. [ALPM documentation](https://man.archlinux.org/man/alpm-hooks.5.en), checked 2026-11-14, specifies AbortOnFail only for pretransaction hooks and NeedsTargets as matched target names. Names alone omit versions, archive hashes and operation details, so a simple shell hook cannot deliver exact transaction-bound approval.

Before activation, implement a reviewed transaction-aware reader and root-controlled one-use approval record bound to operation/name/old/new versions, repository and archive hashes, installed/repository DB hashes, policy/hook/config digests, expiry and recovery receipt. Consume atomically on exact actual-transaction match. Environment overrides must never satisfy approval. Root can deliberately bypass local controls; this guards accidental changes rather than hostile administrators. Noncritical complete transactions should remain possible without permanently holding critical packages back.

## Ten-step approved upgrade workflow

1. Run `scripts/check-hardware.sh --json`; stop unless VERIFIED.
2. Use the installed boot-check procedure in recovery.md under maintainer supervision; it may need privilege and temporary mounts.
3. Review `manifests/known-good.json`, exact package versions, source commits, patch receipts and current local modifications.
4. Run `scripts/capture-baseline.sh` as documented by its `--help` and inspect its returned inventory; confirm backup permission and root/boot/ESP coverage.
5. Run `scripts/preflight-update.sh --refresh --json --scope omarchy`. Inspect candidate old/new versions, protected reasons, ignored-package blockers and local-newer comparisons.
6. Independently resolve incomplete transaction/file/scriptlet information and review Omarchy keyring steps, migrations, removals and AUR updates. A REVIEW REQUIRED result remains unapproved work.
7. Before any installation, obtain approval for the concrete exact transaction and verified recovery set. This project supplies no active transaction interception or approval token mechanism.
8. A maintainer executes only the manually approved operation, using the installed `omarchy update` workflow where applicable. This is a live system change; preflight never executes it. Do not bypass routing guards or use IgnorePkg to split the upgrade.
9. Check next-boot content with the installed procedure in recovery.md; then perform the approved controlled reboot and verify GPU/internal/external displays, networking and audio without changing suspend policy.
10. Promote a new baseline only after successful boot/runtime checks and owner acceptance: retain the previous private recovery set, capture new private inventory, review sanitized manifest diffs and artifact hashes, then update `manifests/known-good.json` with the newly observed versions/provenance. A successful package installation alone is insufficient for promotion.
