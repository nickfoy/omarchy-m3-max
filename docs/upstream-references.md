# Upstream references

- [Aurora kernel baseline](https://github.com/omacom/linux-aurora/tree/bed544bdf93a496ebf70ba180923bab12b6e01cf).
- [Aurora loader baseline](https://github.com/omacom/m1n1/tree/ba130ffbeeadaa35215ed88b07ebcee3199d0be7).
- [Kernel recipe revision](https://github.com/omacom/omarchy-pkgs/tree/0d01c62212a3d5950647cbd4a779461288639f73/pkgbuilds/linux-aurora).
- [Loader recipe revision](https://github.com/omacom/omarchy-pkgs/tree/00b66b0372fb8c5c216ec66400cdfdf314595ae4/pkgbuilds/m1n1-aurora).
- [Kernel PR406](https://github.com/omacom/linux-aurora/pull/406), contributed by BTNG-studio; reviewed source head `66d6c1b1a52abd2815abb48a1f0dcc2a9a8a6be9`, base `e585531e0ba61a26d7e5e844ac938db310034435`. Its J516M target is distinct from this J514M adaptation.
- [Loader PR29](https://github.com/omacom/m1n1/pull/29), contributed by BTNG-studio; reviewed head `939c1a43398ba28bc55ba2a19e694b5618b6ef34`, base `9488b7b7733190a5f1ceeb34d35120a090e420c6`.
- [J514M hardware discussion, kernel issue333](https://github.com/omacom/linux-aurora/issues/333).
- [Native Mesa source](https://github.com/omacom/mesa), baseline package version `1:26.3.0_devel.20261107.231485.b7b03c5b3b8-1`; this bundle does not rebuild Mesa or claim the abbreviated package revision is a verified full source pin.

References record evidence inspected during baseline preparation; later upstream changes are not automatically incorporated. The lock file provides immutable recipe URLs and checksums. Plain diffs deliberately omit patch email envelopes; upstream source copyright, license and attribution notices remain intact.

- [J514M panel brightness and timestamps, Scott Jones’s PR #457](https://github.com/omacom/linux-aurora/pull/457); exact candidate commits and patch checksum are recorded separately from the original baseline.

See the [attribution and licensing map](../THIRD_PARTY_NOTICES.md) for imported artifacts, local adaptations and redistribution boundaries.
