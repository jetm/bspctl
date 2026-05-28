# bspctl clean

Remove the BSP-specific `build/` directory to force a from-scratch build.

## Synopsis

```text
bspctl clean [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--all` | Also remove the generated kas YAML (kas-nxp.yml / kas-ti.yml) |
| `--bsp` | BSP family to clean: `nxp` or `ti`. Auto-detected from cwd when omitted |
| `--manifest`, `-f` | Manifest filename (back-compat alias for `--bsp`) |
| `--workspace`, `-w` | Workspace root override |

## Examples

```bash
# Clean NXP build directory (auto-detected from cwd)
bspctl clean

# Clean explicitly specifying BSP family
bspctl clean --bsp nxp
bspctl clean --bsp ti

# Clean build/ and the generated kas YAML
bspctl clean --bsp nxp --all

# Clean from outside the workspace
bspctl clean --bsp nxp --workspace ~/bsp/my-workspace
```

## Notes

- `clean` removes `<bsp_root>/build/` which contains `tmp/`, `sstate-cache/`, `conf/`, and `runs/`. It does not remove `sources/` (synced layers).
- With `--all`, the generated `kas-<bsp>.yml` is also removed. The next `bspctl build` will regenerate it from the manifest.
- BSP family is auto-detected from cwd by looking for `nxp/` or `ti/` subdirectories.

## See also

- [build.md](build.md) - `--clean` flag runs clean as part of the build pipeline
