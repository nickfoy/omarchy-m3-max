# Third-party source notices

The original preparation script is MIT licensed. Patches and copied kernel configurations derive from upstream projects and retain their applicable upstream licenses; the repository's general license does not relicense third-party code.

Kernel changes derive from Linux/Aurora/Asahi work, including external display contributions by BTNG-studio and this repository's J514M adaptation by Nick Foy. Linux has file-specific SPDX licenses and exceptions; the kernel recipe declares GPL2. The GPL-2.0 license text and upstream identification notes are included in `patches/LICENSES/GPL-2.0`. Preserve the upstream COPYING, LICENSES, source copyright notices, and corresponding source/build scripts when redistributing a built kernel.

Loader changes derive from m1n1/Aurora work, including BTNG-studio's external handoff contribution and Nick Foy's J514M dispatch correction. m1n1 is a mixed-license project. The upstream recipe lists MIT, GPL-2.0-only, CC0-1.0, OFL-1.1-RFN, Zlib, BSD alternatives and MIT/Apache alternatives; its package installs LICENSE and third-party license texts. Preserve those texts and file-level notices in any redistribution. The modified handoff C source is MIT licensed (text in patches/LICENSES/m1n1-MIT); tests and other source retain upstream terms.

Recipe deltas are adaptations of omacom/omarchy-pkgs recipes, including the kernel packaging credited to Jos Dehaes and Matthias Kurz. The preparation tool fetches exact upstream recipes and supporting files; this repository does not redistribute upstream boot logos. Their licensing has not been independently resolved here. Downloading artwork for a private build does not establish permission to redistribute it.

No Apple firmware, calibration, device-specific dumps, boot images, package binaries, or upstream artwork is included. Obtain device firmware through the normal upstream installation process. Author names and source links provide credit without adding personal email addresses to generated patch envelopes. Existing notices embedded in upstream source must remain intact.

The firmware UUID-shaped constants retained in source patches identify public upstream firmware builds, not a host or device. They are required for the existing firmware identity checks. No per-machine hardware UUID is included.

The optional J514M panel patch derives from Scott Jones’s Aurora PR #457 (linked in the candidate documentation), including its upstream tests. It retains the kernel’s applicable licenses and is not relicensed under this repository’s MIT license.

## Attribution and provenance map

| Material in this repository | Upstream source and credit | License / local scope |
| --- | --- | --- |
| `patches/linux-aurora-j514m.patch` | [BTNG-studio’s kernel PR #406](https://github.com/omacom/linux-aurora/pull/406), adapted for J514M by Nick Foy; Linux, Asahi Linux and Aurora contributors | Original file-level SPDX terms remain authoritative. Includes GPL-only files and dual GPL/MIT files; the combined kernel is not relicensed MIT. |
| `patches/m1n1-aurora-j514m.patch` | [BTNG-studio’s loader PR #29](https://github.com/omacom/m1n1/pull/29); J514M dispatcher correction and regression test by Nick Foy | m1n1 / Asahi contributors; preserve file notices and applicable mixed-license terms. Included MIT text is in `patches/LICENSES/m1n1-MIT`. |
| `patches/linux-aurora-j514m-panel.patch` | [Scott Jones / scottjones, kernel PR #457](https://github.com/omacom/linux-aurora/pull/457); commits [0c6c113](https://github.com/omacom/linux-aurora/commit/0c6c113ac69cad1d233d7c8a0b545f1b699bbaea) and [cbe32f3](https://github.com/omacom/linux-aurora/commit/cbe32f37b285ecc0639a4dccc440ec325b55664b) | Modified files declare `GPL-2.0-only OR MIT`. Redistributed here as an upstream-derived kernel patch, with GPL text available; no claim of original authorship. Upstream commit records retain sign-offs and assisted/coauthor credits. |
| Kernel recipe delta and `config/kernel/input.config` | [Pinned omacom/omarchy-pkgs kernel recipe](https://github.com/omacom/omarchy-pkgs/tree/0d01c62212a3d5950647cbd4a779461288639f73/pkgbuilds/linux-aurora); recipe credits Jos Dehaes and Matthias Kurz for the Asahi package basis | Upstream-derived build material, outside the original-code MIT grant. Input config is copied; effective config is generated from the upstream tree and local build choices. Preserve source licenses when building/redistributing. |
| Loader recipe delta and qualification data | [Pinned omacom/omarchy-pkgs loader recipe](https://github.com/omacom/omarchy-pkgs/tree/00b66b0372fb8c5c216ec66400cdfdf314595ae4/pkgbuilds/m1n1-aurora) | Adapted packaging/qualification metadata; not a new license for the packaged loader or its bundled assets. |
| Configuration examples, diagnostic tools, documentation and agent prompts written here | omarchy-m3-max contributors; examples use Omarchy/Hyprland interfaces | Repository MIT license applies to original contributions only. Upstream API usage does not transfer ownership of upstream implementations. |

Immutable source and recipe pins, patch hashes and prepared-recipe hashes are in [build/sources.lock.json](build/sources.lock.json); the separately evaluated panel patch is in [manifests/panel-candidate.json](manifests/panel-candidate.json). These records distinguish imported changes from local adaptations. Public patch envelopes omit personal email addresses; this does not remove notices embedded in source, and linked upstream commits preserve original attribution records.

## Projects providing the working stack

Credit [Omarchy](https://github.com/omacom/omarchy), the [Apple Silicon installer](https://github.com/omacom/omarchy-mac-installer), [Omarchy Mac](https://github.com/omacom/omarchy-mac), [Aurora kernel](https://github.com/omacom/linux-aurora), [Asahi Linux](https://asahilinux.org/), [m1n1](https://github.com/AsahiLinux/m1n1), [Mesa](https://mesa3d.org/), [Hyprland](https://github.com/hyprwm/Hyprland), [Aquamarine](https://github.com/hyprwm/aquamarine), Linux and Arch Linux ARM contributors. Mesa, firmware and compositor packages are inventoried dependencies, not binaries redistributed by this repository. This project documents and adapts their work; it is not an official release or a claim to authorship of their drivers.

## Adding third-party material

Before adding another patch, copied configuration or build recipe, record its upstream URL, exact revision, author/project credit, license and local modifications here or in a linked artifact-specific notice. Preserve copyright, SPDX and license notices. Do not apply the repository MIT license to imported code. Before distributing binaries, separately review all package contents, provide required corresponding source/build material and retain bundled licenses; current source-patch publication does not establish rights to redistribute Apple firmware or upstream artwork.
