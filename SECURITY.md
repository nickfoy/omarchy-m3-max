# Security and publication privacy

Do not file a public issue containing credentials or machine-private data. Use the repository's GitHub Security Advisory reporting if enabled; otherwise contact the maintainer through their public GitHub profile with a description that contains no secret. Do not invent a private reporting email or upload a secret while asking where to send it.

No firmware, binary packages, full disk images, encryption keys, SSH identities, Tailscale credentials, API/GitHub tokens, raw package databases or unredacted logs belong in this repository. Public inventory is allowlisted; arbitrary logs are not made safe by a regex. Raw captures and recovery artifacts must remain outside the checkout with restrictive permissions and an offline copy.

Before first commit/push: inspect every staged path/content, run the repository privacy audit, run an independent secret scanner, inspect licenses and verify there are no archive/binary artifacts. Delete sensitive content before the first commit. Never publish first and rely on later history rewriting. Automated scans are evidence, not guarantees.

The report-only update tools do not enforce a system policy. Never treat an environment variable as authorization for a protected transaction. Root can bypass package hooks; the proposed guard prevents accidents rather than defending against a malicious administrator.
