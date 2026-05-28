[![CI](https://github.com/jetm/bspctl/actions/workflows/ci.yml/badge.svg)](https://github.com/jetm/bspctl/actions/workflows/ci.yml)

# bspctl

kas-based BSP build orchestrator for Yocto. Wraps `kas-container` with manifest-driven sync, pre-flight checks, structured telemetry, and post-mortem tooling. Works with NXP i.MX (repo XML), TI Sitara (oe-layertool), bitbake-setup workspaces, and any bring-your-own kas YAML.

## Install

```bash
uv tool install git+https://github.com/jetm/bspctl.git
```

## Quickstart

```bash
# NXP i.MX manifest-driven build
bspctl build -f imx-6.12.49-2.2.0.xml -m imx8mp-var-dart

# Bring-your-own kas YAML
bspctl build my-project.yml

# Post-mortem a failed build
bspctl triage
```

## Commands

| Command | Description |
|---------|-------------|
| [`build`](docs/build.md) | Full build pipeline: doctor, sync, gen-kas, kas-container |
| [`sync`](docs/sync.md) | Sync sources without building |
| [`gen-kas`](docs/gen-kas.md) | Regenerate kas YAML from manifest |
| [`shell`](docs/shell.md) | Interactive kas-container shell or one-shot command |
| [`run`](docs/run.md) | Boot avocado-os image in QEMU (meta-avocado only) |
| [`clean`](docs/clean.md) | Remove build directory |
| [`doctor`](docs/doctor.md) | Pre-flight checks |
| [`triage`](docs/triage.md) | Post-mortem a failed build run |
| [`report`](docs/report.md) | Summarize a completed build run |
| [`log`](docs/log.md) | Tail a run's log file live |
| [`layers`](docs/layers.md) | Print layer git hashes and branches |
| [`for-all`](docs/for-all.md) | Run a command in every source repo |
| [`settings`](docs/settings.md) | Read and write `~/.config/bspctl/config.toml` |
| [`lock`](docs/lock.md) | Pin floating layer SHAs |
| [`diff`](docs/diff.md) | Compare two manifest versions |
| [`prefetch`](docs/prefetch.md) | Pre-fetch recipe sources into DL_DIR |
| [`dump`](docs/dump.md) | Inspect the resolved kas YAML |
| [`bitbake-override`](docs/bitbake-override.md) | Swap BSP-bundled bitbake for upstream |
| [`stress-parse`](docs/stress-parse.md) | Stress-test bitbake parser fork race |

## Configuration

- [docs/configuration.md](docs/configuration.md) - env vars, config.toml, vendors.toml
- [docs/workspace.md](docs/workspace.md) - workspace detection, BSP families, directory layouts
