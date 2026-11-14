# Source change history

The official installed starting points were kernel `omacom/linux-aurora@bed544bdf93a496ebf70ba180923bab12b6e01cf` (7.2.11.aurora16-1) and loader `omacom/m1n1@ba130ffbeeadaa35215ed88b07ebcee3199d0be7` (1.6.1.aurora23-2).

The kernel backport adapts the shared T6034 external display work from upstream PR406 to J514M: shared dcpext0 device-tree include, opt-in display gate, DCP, crossbar, PHY and Thunderbolt tunnel handling, with focused test updates. It does not change the J516M device tree or GPU implementation. Final local kernel source identity was `86e2f4c1992c4e168a38e2a324c64e556605d60e`; its functional backport was `568c6c4eac2af509e10942da188f3dead9cc0d4b`.

An initial source import omitted seven files matched by ignore patterns: `Documentation/.renames.txt`, four Apple KUnit configurations, and both private-bindgen patches. Those files already belong to the upstream baseline. The public build fetches the complete upstream Git tree and consequently does not publish a misleading patch adding them.

The loader backport adapts PR29's opt-in T6034 dcpext0 handoff and tests (`1dd2bd95097397e618b972a4849f485e8f507abb`). Final review caught a missing dispatcher flag: `9db1606265333ac0b20ba422c71b087ce3cab161` enables `.ext` on the exact J514M profile, removes an accidental J516M flag, and adds a regression test. The published loader patch includes both changes.

The original local package recipes pointed to local Git imports. Public recipe deltas instead pin original upstream Git commits and apply checksummed functional patches. They retain the tested package versions, kernel toolchain adaptation and honest `hardware_tested=false` promotion metadata. Candidate metadata identifies the upstream commit plus patch hash. These packaging adjustments require a clean rebuild before claiming equivalence to the existing artifacts.
