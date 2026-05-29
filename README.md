> **This project has been migrated to
> [bakar](https://github.com/jetm/bakar) and is no longer
> maintained here.**

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

## Documentation

Full command reference, workflow guides, and configuration: **[docs/index.md](docs/index.md)**
