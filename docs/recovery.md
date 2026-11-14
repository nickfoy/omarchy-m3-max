# Recovery boundaries and procedure

Recovery artifacts belong in private owner-controlled state, never this public repository. The current working stack is a locally built kernel/header pair and m1n1 build; the older signed official packages retained from before the display experiment restore a different GPU desktop baseline. They are not identical recovery choices. Record which baseline each archive, package hash and snapshot belongs to.

The observed root filesystem is Btrfs, `/boot` is separate ext4, and `/boot/efi` is a separate FAT ESP. A root snapshot excludes both boot filesystems. A coherent recovery set needs the root snapshot, package databases and archives, relevant configuration, separate boot files and ESP content from the same moment. Existing private boot/config archives are root-owned mode 600, but their completeness has not been certified here. Verify inventories, checksums and mount coverage before relying on them. Never publish filesystem identifiers, serials, boot archives, unlock material or unredacted logs.

The ESP carries m1n1 Stage 2, device trees, U-Boot, Limine, its menu and UKI. A single `boot.bin.old` is not a complete backup. Linux recovery of these files does not restore Apple Stage 1, Apple boot policy, macOS/recovery partitions or firmware. Preserve a working Apple recovery/macOS route and the owner's ability to authenticate it. Do not change Apple policy or the Stage 1 stub as routine Linux update recovery. [Asahi's boot process documentation](https://asahilinux.org/docs/platform/boot-process/) describes the Apple-to-Linux boundary; that page could not be retrieved during this review, so local installed source is the verified basis for the Stage 2 details here.

## Before an approved upgrade

1. Capture a private baseline, package manifest, configuration/hook digests and hardware report. Verify mounted boot filesystems rather than assuming an archive crosses their mountpoints.
2. Preserve exact current package archives, source/patch provenance and their checksums. Keep older official rollback packages separately labelled.
3. Create and verify a root snapshot plus matching `/boot` and ESP backups. Keep a second copy outside the filesystem being repaired. Confirm available storage and recovery access.
4. Run `scripts/preflight-update.sh --json --refresh --scope omarchy`. A clean runtime solve remains REVIEW REQUIRED because incoming paths/scriptlets and exact removal operations are not certified; solver diagnostics or failure produce BLOCKED. Review that limitation; do not treat the report as update authorization.

## If the running system still works

Stop update work and preserve failure evidence privately. Do not reboot while next-boot content is inconsistent. First identify whether the root/package state, kernel/initramfs, UKI/menu, or Stage 2 failed. Match the selected recovery baseline across all filesystems. Do not mix an arbitrary old root snapshot with unrelated newer ESP content and assume consistency.

A maintainer may conditionally run the installed read-only-content boot checker:

```sh
OMARCHY_BOOT_CHECK_ALLOW_PENDING_REBOOT=1 omarchy-apple-silicon-boot-check --boot-chain
```

This invokes sudo, creates temporary files and a private read-only ESP mount; it is not part of automated report-only inspection. Pending-reboot mode compares installed next-boot files, not successful runtime behavior. Do not invoke lifecycle updater checks as if they were pure inspection: they can rebuild boot files when rollback markers exist. Owner-managed-chain declarations or rollback ESP exceptions must be disclosed and must not stand in for verification.

Only after choosing a coherent baseline and reviewing exact package archives, mounts and configuration should a maintainer use manual repair commands such as:

```sh
sudo mkinitcpio -P
sudo update-m1n1
sudo omarchy-mac-boot-update
OMARCHY_BOOT_CHECK_ALLOW_PENDING_REBOOT=1 omarchy-apple-silicon-boot-check --boot-chain
```

These commands write boot files and require a separately approved recovery action; they are examples of the installed repair sequence, never automatic recommendations to execute. They regenerate from the currently installed packages, so restoring package/root state must come first when rolling back. Exact package reinstall commands must name the reviewed matched archive set; no wildcard installation command is provided.

## If Linux does not boot

Use the already established Apple recovery/boot selection path or an owner-prepared rescue environment. Unlock and mount only the intended root, boot and ESP; verify identities privately. Restore the chosen coherent set with a competent maintainer, including package state and matching boot artifacts. Root snapshot tooling may integrate kernel restoration but must be inspected for this installation before assuming ESP coverage. Restoring root alone does not establish Stage 2/UKI consistency.

After a controlled reboot, verify internal display, GPU rendering and the intended external connector path and examine fault logs. Boot-file agreement cannot prove display runtime behavior. Keep suspend, hibernate and lid policy unchanged throughout recovery; no suspend experiment is required by this procedure.

## Failure mapping

| Observed failure | Recovery boundary to inspect |
| --- | --- |
| Update metadata/solver fails | Repository/keyring/configuration; do not install a partial transaction |
| Package extraction fails | Installed package DB/root consistency before boot regeneration |
| Initramfs generation fails | Matching kernel modules, mkinitcpio config and unlock support |
| UKI hash/menu mismatch | `/boot`, ESP UKI and Limine configuration together |
| Stage 2 mismatch | m1n1, matched DTBs, U-Boot and m1n1 configuration on system ESP |
| Root snapshot restored | Root package state plus separate boot and ESP versions |
| GPU/internal display regresses | Matched kernel/Mesa/firmware baseline and source patches |
| External display regresses | Experimental external-display stack provenance and connector runtime evidence |
| Apple boot selection/recovery fails | Apple Stage 1/policy/macOS recovery; Linux Stage 2 repair is insufficient |

For an offline package reinstall, first mount the reviewed intended root, separate boot partition and ESP at their proper locations, and bind required rescue filesystems as appropriate for the rescue environment. After entering that mounted root, an approved maintainer can use an explicit matched archive set, for example:

```sh
# PLACEHOLDERS: replace every path/name with the reviewed private archive set.
# Run inside the intended mounted root, with its boot and ESP mounted.
pacman -U /PRIVATE_RECOVERY/linux-aurora-EXACT_VERSION-aarch64.pkg.tar.xz \
  /PRIVATE_RECOVERY/linux-aurora-headers-EXACT_VERSION-aarch64.pkg.tar.xz \
  /PRIVATE_RECOVERY/m1n1-aurora-EXACT_VERSION-aarch64.pkg.tar.xz
```

This is a manual destructive recovery operation, never executed by project tooling. Verify archive checksums/signatures as appropriate before installation; locally built artifacts require their retained provenance and reviewed hashes. Headers, kernel and boot stage packages must come from the same selected baseline. Follow with the installed regeneration/check procedure above only after successful package/root repair. Do not use package globs or blindly install an entire cache. Offline recovery environment setup and Apple recovery are deliberately not automated.
