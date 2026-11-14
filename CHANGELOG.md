# Changelog

## 2026-11-14 — candidate panel fix

- Preserved Aurora PR #457 as a separate optional patch with pinned upstream commits and checksum.
- Documented brightness, actual 120 fps presentation and other J514M community candidates without promoting untested changes.

## 2026-11-14 — initial captured baseline

- Documented the transition from disabled J514M GPU / llvmpipe to matched Aurora16, loader and Mesa hardware acceleration.
- Preserved the subsequent opt-in T6034 external-display kernel/loader backport and the exact J514M dispatcher correction.
- Recorded simultaneous displays, cold/startup external operation and clamshell close/open; kept the later reconnect failure visible.
- Added hardware gate, read-only inventory/verifiers, update preflight, private capture, recovery guidance and agent-neutral install/update prompts.
- Kept suspend protections unchanged; no graphics/boot/network update performed during repository preparation.

This records existing changes and this documentation/tooling mission. It does not claim this project authored the upstream GPU or DCP drivers.
