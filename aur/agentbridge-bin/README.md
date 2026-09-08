# AUR package: agentbridge-bin

Arch Linux binary package for AgentBridge (AGPL-3.0). It installs the official
self-contained release archive into `/usr/share/agentbridge` (read-only) and provides
`/usr/bin/agentbridge`, a launcher that materializes the payload into the user's
`~/.local/share/agentbridge/engine` on first run and refreshes it when the package's
version marker changes (the engine writes `PersistentData/` next to the executable).

## First-time publishing (account action, needed once)

1. Create an Arch Linux account at https://aur.archlinux.org and add your SSH public
   key (Settings → SSH keys).
2. The AUR package name is `agentbridge-bin`:
   ```bash
   git clone ssh://aur@aur.archlinux.org/agentbridge-bin.git /tmp/agentbridge-bin
   # copy PKGBUILD, .SRCINFO, agentbridge, agentbridge.desktop, agentbridge.png into it
   cd /tmp/agentbridge-bin
   makepkg --printsrcinfo > .SRCINFO   # keep in sync with PKGBUILD
   git add -A && git commit -m 'Initial release 1.26.9.8'
   git push
   ```

## Bumping for a new AgentBridge release

1. Update `pkgver`, the archive URLs and the `sha256sums_*` (use the asset `digest`
   from the GitHub release API) in `PKGBUILD`.
2. `makepkg --printsrcinfo > .SRCINFO`, commit and push both files.

Notes:
- Two architectures via `source_x86_64`/`source_aarch64` (official x64/arm64 archives).
- Runs from any terminal (`agentbridge`); launch in a terminal or use the
  "AgentBridge" desktop entry. The engine's in-app auto-update is not used from the
  package — the new version arrives with the package update.
