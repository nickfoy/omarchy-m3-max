# Known-good baseline

The authoritative initial public record is [known-good.json](../manifests/known-good.json). All installed package names/versions are in [packages.txt](../manifests/packages.txt); critical classifications are in [versions.json](../manifests/versions.json). These are observations from one host, not a universal compatible version range.

The current custom kernel and loader replace the earlier official edge packages. The public OS repository remains stable; Mesa/Vulkan came from a matched official edge candidate. The original Aurora14 / older loader had no enabled J514M GPU node. Aurora16 plus matched loader/Mesa enabled native graphics; the subsequent local backport added external output. See [change history](change-history.md).

Baseline preservation performed before this repository's implementation:

- Full installed package database and installed package version list captured privately.
- Critical configuration plus independent `/boot` and mounted EFI partition archives captured privately with owner/root-only permissions.
- Boot-chain consistency check passed. It proves next-boot file agreement, not universal runtime reliability.
- Exact installed custom kernel/headers/loader packages and matching Mesa/Vulkan archives copied to private storage and hashed. The custom packages existed in the local build directories, not the normal pacman cache. Public manifests contain hashes, not binaries.
- Source checkouts, diffs, recipes, build logs and prior captures remain private. Public build references/patches reconstruct their technical changes without publishing personal build paths.

Package integrity checks report generated kernel depmod metadata timestamp/size differences; these are not evidence of source changes. The installed loader package files matched their package manifest. Runtime driver/renderer checks passed. The effective kernel CONFIG entries match the running `/proc/config.gz`; input and effective config files differ because Kconfig resolves the source fragment.

Restoration gaps: local binary hashes identify exact artifacts, not guaranteed byte-for-byte reproducible builds. Full clean rebuild and disaster recovery have not been rehearsed. Stage 1's inherited dirty build lacks complete source provenance. Apple proprietary firmware and boot-policy material cannot be reconstructed merely from this repository; keep owner-accessible recovery and private copies. Do not delete local artifacts after publication.

Future captures use `scripts/capture-baseline.sh --output <private-new-directory> --json`; they do not automatically replace this file or become approved baselines.
