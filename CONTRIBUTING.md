# Contributing

Start with the compatibility and regression issue templates. Include exact model identifier, board, SoC/chip variant, CPU/GPU bin, nominal RAM, kernel, loader, firmware and graphics package versions, connected monitor/dock/transport, observed behavior and reproducible steps. Marketing names and “works for me” are insufficient.

Run the hardware gate, inventory and relevant verifiers. Keep raw captures private; manually review allowlisted JSON too. Remove device/monitor/disk serials, UUIDs, usernames, emails, SSIDs, private hostnames/domains, MAC/private IP addresses, tokens and unrelated personal data before submission. Never attach boot images, firmware, package databases, keys or encryption recovery material.

Label submissions unverified until reviewed and reproduced. Do not reclassify another model based on this J514M result. Distinguish owner observation, automated probe, upstream report and inference. State what was not tested.

For code: use standard shell/Python tooling, meaningful tests (`python3 -m unittest discover -s tests -v`), no silent host modifications, and explicit PASS/FAIL/UNKNOWN semantics. Run `python3 scripts/audit-publication.py` and an independent secret scanner. Preserve SPDX/copyright and upstream licenses; do not attach binaries. Discuss boot/firmware/sleep changes before implementation. Prefer general fixes upstream and link the issue/commit here rather than growing unnecessary permanent forks.

No contributor should trigger suspend merely to reproduce a report without the machine owner's explicit approval and recovery plan.
