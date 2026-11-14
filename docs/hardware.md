# Hardware evidence

The verified host reports **Mac15,10** through the DMI product name and **apple,j514m / apple,t6034** in the live device tree. It is the 14-inch November 2023 M3 Max with 14 CPU / 30 GPU cores and 36 GB nominal unified memory (roughly 35 GiB usable). The internal SSD is nominally 1 TB; partition allocation is personal and is not a prerequisite recipe.

Use `scripts/check-hardware.sh --json`. Require agreement across model, board, SoC, architecture and OS. A missing identifier is UNKNOWN, not permission to guess. A J514C/J516C or J516M can have a different GPU bin, firmware pin, display graph or power profile despite sharing an M3 Max name. Community reports require their own profile and exact versions.

No device serial numbers, hardware UUIDs, Apple boot-policy identifiers or disk UUIDs are published. Firmware **build/version** references are software provenance, not device identity. See manifests/known-good.json and COMPATIBILITY.md.
