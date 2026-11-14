# Preparing native J514M builds

This bundle reconstructs the source changes used for the working native Omarchy J514M baseline. It does not establish bit-for-bit reproducibility. A complete clean rebuild of this public bundle has not yet been verified. No installation command is automated.

Use a native AArch64 Arch/Omarchy build environment. Review the patches and upstream recipes before running them. Install build dependencies separately using the pinned recipes' `makedepends`; recipe preparation requires network access for Git and Rust downloads. Preparation itself needs Python 3, `patch`, and Bash.

```sh
python3 build/prepare-build.py --check-only
python3 build/prepare-build.py --output /tmp/j514m-build-recipes
cd /tmp/j514m-build-recipes/linux-aurora
makepkg --verifysource
OMARCHY_BUILD_JOBS=8 makepkg
cd ../m1n1-aurora
makepkg --verifysource
OMARCHY_BUILD_JOBS=8 makepkg
```

Choose an unused output directory outside this checkout. The preparation tool downloads checksum-pinned upstream recipe files, including upstream loader artwork, into that directory; this repository does not redistribute artwork. Review its rights before redistributing the resulting package. The tool neither builds nor installs packages. Run makepkg without `--install` or `-i`; inspect the resulting packages before making a separate installation decision.

`build/sources.lock.json` pins recipe revisions, downloaded file hashes, expected modes, upstream source commits, local patches, and prepared PKGBUILD hashes. The normal makepkg Git fetch checks out the complete original upstream source tree, including ignored-but-tracked files. It does not reconstruct source using `git add`. Kernel preparation applies its patch through the upstream recipe's patch loop; loader preparation explicitly applies its patch. The patched loader retains the original Git HEAD and records its patch hash separately in candidate metadata. A fresh prepare directory is required for another build.

## Qualified toolchain and modes

The original kernel build used clang18 and llvm18 `18.1.8-2`, lld18 `18.1.6-2`, Rust `1.85.0` with rust-src, and private bindgen `0.73.2` built with Rust `1.99.0` and rustfmt. Preserve `/usr/lib/llvm18/bin/` and `/usr/lib/llvm18/lib`, or set `AURORA_LLVM` and `AURORA_LIBCLANG_PATH` to equivalent paths. The `_make` wrapper explicitly passes `BINDGEN`, because Kbuild overrides an environment-only value. `bindgen-kernel.py` must have executable mode `0755`; the preparation tool enforces it. `configure.sh` is sourced and can remain `0644`.

The loader uses Rust `1.89.0`, target `aarch64-unknown-none-softfloat`, system clang/lld `23.1.3-3`, `EXTRA_CFLAGS=-Os RELEASE=1 CHAINLOADING=1 USE_CLANG=1`. Its second build adds `ESP_STAGE2=1`; the ordinary update path does not enroll Stage 1. Other recorded tools include make `4.4.1-3`, dtc `1:1.8.1-1`, pahole `1:1.32-1`, and makepkg `7.1.0`. Versioned dependency archives and an isolated build environment have not been validated by this bundle.

## Configuration and output checks

`config/kernel/input.config` is the recipe input (SHA256 `98f76a885d81711013aad47e2ee13f000923191e43321738ec8f381690bf5160`). Upstream configuration merging produces `config/kernel/effective.config` (SHA256 `127a9570ea7c294621566e63b628bb4759ad71729b0148b2b8ca90d527dba903`). The effective CONFIG entries matched the running baseline kernel when captured. Compare CONFIG assignments and unset entries after preparation; comments and generated timestamps may differ. Preserve the `-ARCH` suffix required by boot bundle DTB discovery. Expected kernel release: `7.2.11-16-1.1-ARCH`.

Verify the J514M packaged DTB has `dcpext0` pointing to `/soc/dcp@306c00000` and leaves that node disabled until the opt-in handoff. Verify module vermagic matches the kernel release. The final loader patch must include the J514M `.ext=true` dispatcher fix. External output requires the separately documented `chosen.asahi,t6034-dispext=1` boot setting and a compatible native Mesa baseline.

The existing artifact hashes identify the tested packages; rebuilding from this bundle can produce different bytes. Build timestamps, SOURCE_DATE_EPOCH, checkout paths, compiler versions and package compression are not fully normalized. Source checksum verification is distinct from independent hardware qualification and binary reproducibility.
