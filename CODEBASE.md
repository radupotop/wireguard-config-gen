# Code Overview

- `run.py` is the top-level CLI shim; it forwards arguments straight into `wgconf.run.runall()`.
- `wgconf/run.py` consumes YAML paths, merges overrides, resolves `Outdir`, and dispatches configuration generation.
- `wgconf/parseyamlconfig.py` owns the heavy lifting: it validates input through Pydantic models, auto-allocates IPs, issues keys, and writes both `result.yaml` and the peer `.conf` files.
- `wgconf/parsewgconfig.py` keeps the intermediary WireGuard view. It hydrates peer relationships (mesh vs. star, passive servers) and produces hand-crafted INI text with version/time headers.
- `wgconf/models.py` contains the Pydantic schemas used throughout, plus helpers such as `HostModel.is_server` and `TopologyType` to simplify topology checks.
- `wgconf/genkeys.py` wraps cryptography primitives for X25519 keypairs and preshared keys; no shelling out to `wg`.
- `wgconf/utils.py` is intentionally small: cached helpers for timestamps and reading the project version from `pyproject.toml`.

## Typical Flow
1. `run.py` receives one or more YAML templates; overrides are merged last-in.
2. The merged payload is validated into `YamlConfig`, `Outdir` is resolved, and dynamic defaults are filled.
3. For each machine, WireGuard peers are derived, preshared keys assigned, and configs serialized into `output/`.
4. The generator prints the destination so scripts can pick the path up.

## Notable Behaviors
- Universal PSK support reuses `_UNIVERSAL_`; otherwise keys are keyed by sorted name pairs.
- Passive servers automatically drop outbound endpoints so they wait for clients to dial in.
- DNS defaults to the global dynamic list and collapses to comma-separated strings when writing INI files.
