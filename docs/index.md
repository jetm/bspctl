# bspctl documentation

## Quick navigation

| Command | Doc | One-liner |
|---------|-----|-----------|
| `build` | [build.md](build.md) | Full pipeline: doctor, sync, gen-kas, kas-container build |
| `sync` | [sync.md](sync.md) | Sync sources without building |
| `gen-kas` | [gen-kas.md](gen-kas.md) | Regenerate kas YAML from manifest |
| `shell` | [shell.md](shell.md) | Interactive kas-container shell or one-shot command |
| `run` | [run.md](run.md) | Boot avocado-os image in QEMU (meta-avocado only) |
| `clean` | [clean.md](clean.md) | Remove the build directory |
| `doctor` | [doctor.md](doctor.md) | Run pre-flight checks |
| `triage` | [triage.md](triage.md) | Post-mortem a failed build |
| `report` | [report.md](report.md) | Summarize a completed build run |
| `log` | [log.md](log.md) | Tail a run log live |
| `layers` | [layers.md](layers.md) | Print layer git hashes and branches |
| `for-all` | [for-all.md](for-all.md) | Run a shell command in every source repo |
| `settings` | [settings.md](settings.md) | Read and write `~/.config/bspctl/config.toml` |
| `lock` | [lock.md](lock.md) | Pin floating layer SHAs |
| `diff` | [diff.md](diff.md) | Compare two manifest versions |
| `prefetch` | [prefetch.md](prefetch.md) | Pre-fetch recipe sources into DL_DIR |
| `dump` | [dump.md](dump.md) | Inspect the resolved kas YAML |
| `hashserv` | [hashserv.md](hashserv.md) | Manage the persistent bitbake-hashserv daemon |
| `bitbake-override` | [bitbake-override.md](bitbake-override.md) | Swap BSP-bundled bitbake for upstream |
| `stress-parse` | [stress-parse.md](stress-parse.md) | Stress-test bitbake parser fork race |
| Configuration | [configuration.md](configuration.md) | Env vars, config.toml, vendors.toml, telemetry layout |
| Workspace | [workspace.md](workspace.md) | Workspace detection, BSP families, directory layouts |

---

## Which command do I need?

**Starting a build:**
- First time with a manifest: [build.md](build.md)
- Already synced, just want to rebuild: `bspctl build --skip-sync`
- Only want to sync sources: [sync.md](sync.md)
- Only want to regenerate the kas YAML: [gen-kas.md](gen-kas.md)

**Build failed:**
- Find what went wrong: [triage.md](triage.md)
- Watch a running build: [log.md](log.md)
- Check if the environment is sane: [doctor.md](doctor.md)
- Force a from-scratch rebuild: [clean.md](clean.md) or `bspctl build --clean`

**After a successful build:**
- Summarize timing, image size, layer SHAs: [report.md](report.md)
- Inspect layer commits: [layers.md](layers.md)

**Reproducibility and snapshots:**
- Pin current SHAs: [lock.md](lock.md)
- See what changed between manifest versions: [diff.md](diff.md)
- Pre-fetch sources for an offline build: [prefetch.md](prefetch.md)
- Inspect the exact config kas will receive: [dump.md](dump.md)

**Exploring the source tree:**
- Interactive shell inside the kas environment: [shell.md](shell.md)
- Run a git or shell command in every layer: [for-all.md](for-all.md)

**Configuration:**
- Persist default machine/image/distro: [settings.md](settings.md)
- Tune sstate mirrors, DL_DIR, container image: [settings.md](settings.md)
- Understand env vars and priority order: [configuration.md](configuration.md)
- Workspace layout and BSP family auto-detection: [workspace.md](workspace.md)

**Advanced:**
- Swap BSP bitbake for a local upstream checkout: [bitbake-override.md](bitbake-override.md)
- Boot a QEMU image from the build directory: [run.md](run.md)
- Reproduce and measure the bitbake parser race: [stress-parse.md](stress-parse.md)
- Persistent hash equivalence across builds: [hashserv.md](hashserv.md)

---

## Command groups

### Build pipeline

```text
bspctl doctor    - pre-flight (runs automatically before build)
bspctl sync      - fetch/update sources
bspctl gen-kas   - translate manifest → kas YAML
bspctl build     - all of the above, then kas-container build
```

Related: [build.md](build.md), [sync.md](sync.md), [gen-kas.md](gen-kas.md), [doctor.md](doctor.md)

### Observability

```text
bspctl log       - tail a live build log
bspctl triage    - surface the failing step after a build exits non-zero
bspctl report    - summarize a completed run (timing, image size, layers)
bspctl layers    - print layer git hashes without running anything
```

Related: [log.md](log.md), [triage.md](triage.md), [report.md](report.md), [layers.md](layers.md)

### Reproducibility

```text
bspctl lock      - pin every floating layer SHA to an exact commit
bspctl diff      - compare old/new manifest or kas config
bspctl dump      - flatten kas YAML + overlay into a single resolved file
bspctl prefetch  - populate DL_DIR for offline builds
```

Related: [lock.md](lock.md), [diff.md](diff.md), [dump.md](dump.md), [prefetch.md](prefetch.md)

### Shell and scripting

```text
bspctl shell     - interactive or one-shot kas-container shell
bspctl for-all   - run a command in every source repo (parity with kas for-all-repos)
```

Related: [shell.md](shell.md), [for-all.md](for-all.md)

### Configuration

```text
bspctl settings  - CRUD interface for ~/.config/bspctl/config.toml
```

Related: [settings.md](settings.md), [configuration.md](configuration.md), [workspace.md](workspace.md)

### Advanced / specialized

```text
bspctl clean             - remove build/ to force a from-scratch build
bspctl hashserv          - manage the persistent bitbake-hashserv daemon
bspctl bitbake-override  - swap BSP-bundled bitbake for upstream
bspctl run               - boot avocado-os QEMU image (meta-avocado only)
bspctl stress-parse      - stress-test bitbake parser fork race
```

Related: [clean.md](clean.md), [hashserv.md](hashserv.md), [bitbake-override.md](bitbake-override.md), [run.md](run.md), [stress-parse.md](stress-parse.md)
