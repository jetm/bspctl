# bspctl dump

Flatten the kas YAML plus tuning overlay into a single resolved YAML.

Runs `kas dump` on the build-YAML-plus-overlay argument. Useful for inspecting exactly what kas will receive before running a build, or for passing the resolved config to external tools.

## Synopsis

```text
bspctl dump [KAS_YAML] [OPTIONS]
```

## Options

| Flag | Short | Description |
|------|-------|-------------|
| `--manifest` | `-f` | Manifest filename for BSP family dispatch |
| `--output` | `-o` | Write the resolved YAML to this path (default: stdout) |
| `--workspace` | `-w` | Workspace root override |

## Examples

```bash
# Dump the resolved config to stdout
bspctl dump -f imx-6.12.49-2.2.0.xml

# Dump for a BYO build
bspctl dump my-project.yml

# Save to a file for inspection
bspctl dump my-project.yml -o /tmp/resolved.yml
cat /tmp/resolved.yml

# Pipe to yq for targeted queries
bspctl dump my-project.yml | yq '.repos | keys'
```

## Notes

- `dump` uses an ephemeral run directory so it does not pollute `build/runs/`.
- The output reflects the merged kas YAML plus the bspctl tuning overlay. This is the exact config that `bspctl build` would pass to kas-container.
- Without `--output`, the resolved YAML is printed to stdout. All other bspctl output (progress lines) goes to stderr, so piping works cleanly.

## See also

- [gen-kas.md](gen-kas.md) - generate the topology-only kas YAML (input to dump)
- [build.md](build.md) - the full pipeline that uses this config
