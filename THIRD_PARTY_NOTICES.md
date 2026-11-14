# Third-party source notices

The original preparation script is MIT licensed. Patches and copied kernel configurations derive from upstream projects and retain their applicable upstream licenses; the repository's general license does not relicense third-party code.

Kernel changes derive from Linux/Aurora/Asahi work, including external display contributions by BTNG-studio and this repository's J514M adaptation by Nick Foy. Linux has file-specific SPDX licenses and exceptions; the kernel recipe declares GPL2. The GPL-2.0 license text and upstream identification notes are included in `patches/LICENSES/GPL-2.0`. Preserve the upstream COPYING, LICENSES, source copyright notices, and corresponding source/build scripts when redistributing a built kernel.

Loader changes derive from m1n1/Aurora work, including BTNG-studio's external handoff contribution and Nick Foy's J514M dispatch correction. m1n1 is a mixed-license project. The upstream recipe lists MIT, GPL-2.0-only, CC0-1.0, OFL-1.1-RFN, Zlib, BSD alternatives and MIT/Apache alternatives; its package installs LICENSE and third-party license texts. Preserve those texts and file-level notices in any redistribution. The modified handoff C source is MIT licensed (text in patches/LICENSES/m1n1-MIT); tests and other source retain upstream terms.

Recipe deltas are adaptations of omacom/omarchy-pkgs recipes, including the kernel packaging credited to Jos Dehaes and Matthias Kurz. The preparation tool fetches exact upstream recipes and supporting files; this repository does not redistribute upstream boot logos. Their licensing has not been independently resolved here. Downloading artwork for a private build does not establish permission to redistribute it.

No Apple firmware, calibration, device-specific dumps, boot images, package binaries, or upstream artwork is included. Obtain device firmware through the normal upstream installation process. Author names and source links provide credit without adding personal email addresses to generated patch envelopes. Existing notices embedded in upstream source must remain intact.

The firmware UUID-shaped constants retained in source patches identify public upstream firmware builds, not a host or device. They are required for the existing firmware identity checks. No per-machine hardware UUID is included.

The optional J514M panel patch derives from Scott Jones’s Aurora PR #457 (linked in the candidate documentation), including its upstream tests. It retains the kernel’s applicable licenses and is not relicensed under this repository’s MIT license.
