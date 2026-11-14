# J514M fixes under evaluation

These findings apply to Mac15,10 / apple,j514m / apple,t6034. They do not qualify other M3 Max models. The [known-good manifest](../manifests/known-good.json) remains authoritative; a candidate is not a replacement baseline.

## Panel brightness and real 120 fps presentation

[Aurora PR #457](https://github.com/omacom/linux-aurora/pull/457) addresses [issue #448](https://github.com/omacom/linux-aurora/issues/448). The J514M board record lacks `panel_nits` and `swap_timestamps`, and its machine is missing from the bounded panel-nits admission list. The patch enables these existing paths for the exact board. External processors retain their existing timestamp behavior. No firmware, loader, Mesa or suspend change is required by this patch.

The repository baseline exposes no `/sys/class/backlight` device. A reported 120 Hz mode is **not proof of 120 fps presentation**: upstream measurements found 60 fps without timestamps. Owners reported working brightness and approximately 120 fps with these changes in [hardware issue #333](https://github.com/omacom/linux-aurora/issues/333). Those reports are community evidence, not qualification of our candidate binary.

[Candidate metadata](../manifests/panel-candidate.json) pins both PR commits and the SHA256 of [the optional patch](../patches/linux-aurora-j514m-panel.patch). The existing source/build locks continue to reproduce the previous baseline. To prepare the candidate without installing:

1. Follow [building.md](building.md) to generate a fresh baseline recipe directory outside this checkout.
2. Copy the optional patch into that directory's `linux-aurora/` folder. Review it and verify its hash against candidate metadata.
3. In the prepared kernel PKGBUILD, change `pkgrel=1.1` to `pkgrel=1.2`. Append the optional patch filename to `source` and its actual SHA256 to the matching `sha256sums` array. Preserve all existing external-display source and recipe patches. The recipe's existing patch loop applies them in order.
4. Run `makepkg --verifysource`, then `OMARCHY_BUILD_JOBS=8 makepkg`, without `-i` or `--install`. Confirm `build/base/version` is `7.2.11-16-1.2-ARCH` and compare effective CONFIG assignments with the baseline.
5. Run the focused upstream host tests listed below. Inspect both package archives, dependency resolution, module vermagic and the J514M external-display DTB before presenting an installation transaction.

The local evaluation used the previous build directory incrementally; it does not establish a clean reproducible build. Preserve the exact previous kernel/headers, loader and boot/ESP recovery artifacts. Install only the approved matching kernel/headers candidate, not a stock PR test package that omits our external-display changes. Do not run `pacman -Syuu` as a generic rollback; it can downgrade unrelated packages. Follow [recovery.md](recovery.md) using the captured exact artifacts.

Focused tests: `tools/asahi/t6034-display-tests.py`, `dcp14-panel-tests.py`, `dcp14-backlight-tests.py`, `g15-display-order-tests.py`, `g15-t6034-profile-tests.py`, and `t6030-display-admission-tests.py --mutations --output <private-results.json>` (all under `tools/asahi/`). These passed on the candidate source; KUnit execution and hardware runtime checks are separate.

After an approved reboot, open the lid, check `uname -r`, run both repository GPU/display verifiers, and inspect `/sys/class/backlight`. If `apple-panel-bl` appears, record its maximum/current value, make a modest brightness change with `brightnessctl -d apple-panel-bl set 70%`, then restore the original value. Confirm visible panel dimming and keyboard controls with the owner. Measure presentation intervals on the internal panel rather than equating its mode with frame throughput. Check the external monitor and preserve all sleep masks/lid policy. No suspend test is included, despite the optional suspend suggestion upstream.

The owner-approved kernel/headers candidate is now installed. Package hooks regenerated the initramfs, unified kernel image and m1n1 bundle while retaining the external-display opt-in. The next-boot check passed, and all five sleep targets remained masked. Runtime tests still exercised the previous kernel; brightness and presentation are awaiting reboot validation. The baseline has not been promoted.

## Other community findings

| Candidate | Evidence and relevance | Decision |
| --- | --- | --- |
| Second external display processor | Issue #333 reports two simultaneous USB-C LG 4K60 monitors after J514M `dcpext1` device-tree, kernel power-domain and m1n1 changes. | Separate experimental project; no reviewed patch bundle or two-monitor qualification here. Do not apply another model's device tree. |
| External hotplug/reconnect | Our baseline has one successful reconnect and one connected-but-disabled compositor failure; issue #333 reports working direct USB-C reconnect on another configuration. | No confirmed fix identified for our dock case; retain the documented explicit-enable recovery. |
| GPU throughput / larger Vulkan heap | Issue #333 discusses an experimental inflight change and `HK_SYSMEM` overrides for large models. | Workload tuning, not a general desktop fix. No global memory/queue overrides proposed. |
| Suspend/resume | One owner reported an informal successful cycle, without logs. | Insufficient qualification; existing masks and lid policy remain untouched. |
| HDMI, HDR/10-bit, external DDC brightness | The cited J514M reports leave HDMI untested and report missing HDR/10-bit/DDC support. | No qualified fix identified in this review. External monitor controls remain the practical brightness route. |

Review date: 2026-11-14. Upstream status can change. Previously merged GPU/kernel/loader/Mesa enablement is already represented in the baseline; older stacked PRs are not additional fixes to apply wholesale.

## First candidate boot

The candidate booted as `7.2.11-16-1.2-ARCH`. GPU verification passed with the Apple M3 Max renderer, and the external ultrawide ran at 3840x1080@59.968. The new `apple-panel-bl` backlight device exposes a maximum of 500. All five sleep targets remain masked. The lid was closed during this check: visible internal-panel dimming, brightness keys and actual presentation frame rate remain unverified. No baseline promotion has occurred.
