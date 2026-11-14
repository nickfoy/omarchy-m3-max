# Initial validation receipt — 2026-11-14

This is evidence for one Mac15,10/J514M/T6034, not general model qualification.

- 37 automated tests passed, including unsupported/missing OS hardware gates, software-renderer failure, unknown evidence, disconnected/missing internal connectors, intentional disconnected external monitors, clamshell, private capture permissions and incomplete capture status, malformed update metadata and protected Aurora package scenarios.
- Hardware gate VERIFIED; public baseline package comparison PASS; live EGL/GLES hardware context plus asahi-g15 render node PASS; Vulkan loader enumerated Apple M3 Max (not compute qualification).
- Display verifier PASS with the owner's current clamshell arrangement. Earlier lid-open evidence recorded internal 120 Hz and external 60 Hz simultaneously; this mission did not force a lid/display change.
- Initial owner-confirmed startup external monitor, one hotplug and clamshell close/open results retained. Later reconnect needing output re-enable remains documented as a limitation.
- Real update preflight refreshed only a private copied DB/cache. Result REVIEW REQUIRED; candidate mise-bin application update; installed custom graphics components newer than stable. No package update occurred.
- Public build preparation checked pinned remote input hashes, recipe deltas and executable helper mode for both packages. Source diffs passed clean application checks against original baseline archive members. A fresh full build, binary equivalence and hardware boot of a clean rebuild were not performed.
- Agent install/update prompts were walked through with actual read-only host commands and existing manifests. Unsupported hardware simulation was blocked. Referenced paths and commands/flags were checked; no autonomous installer or critical update was run to test the prompts.
- Repository privacy scanner and independent Gitleaks v8.30.1 scan found no secrets; manual staged review is required before publication. Source patches retain only public upstream firmware build UUID constants, not per-machine UUIDs.
- Full private initial package DB/config/boot/EFI preservation exists; checksum and required-entry audit is separate from a disaster-recovery rehearsal. Offline recovery is documented, not claimed rehearsed.
- Existing sleep-family masks, ignored lid suspend and manual display-wake shortcut were preserved. No suspend experiment or graphics/boot/network modification occurred during this mission.

The first public baseline is an owner-requested snapshot of an already tested setup. Future baseline promotion still requires explicit approval. System-wide update interception remains a proposal and is not active.
