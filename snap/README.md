# Snap Store packaging (AgentBridge)

Classic-confinement snap built from the **official self-contained release archive**
(engine + voices + model), with a launcher that materializes the read-only snap payload
into the per-user `SNAP_USER_DATA` (the engine writes `PersistentData/` next to the
executable — same model as the Flatpak launchers).

## Layout

```
snap/
├── snapcraft.yml.in            versioned template (@@VERSION@@ / @@SHA256@@)
├── files/bin/agentbridge-launcher    materialize + exec engine
├── files/agentbridge-version.txt     marker (rewritten per version)
└── gui/agentbridge.{desktop,png}     desktop integration (classic snaps)
.github/workflows/snap-release.yml    dispatch build (+ store publish when credentials exist)
```

## First-time setup (account action, needed once)

1. Create an **Ubuntu SSO** account and install snapcraft locally (`sudo snap install
   snapcraft --classic`).
2. Register the name — must be globally unique on the Snap Store:
   ```bash
   snapcraft register agentbridge
   ```
3. Export the store login for CI and add it as the `SNAPCRAFT_STORE_CREDENTIALS`
   secret of this repo:
   ```bash
   snapcraft export-login --snaps=agentbridge - > credentials.txt
   ```

## Bumping a new AgentBridge version

Dispatch `snap-release.yml` with the new version (default `latest`): it renders
`snapcraft.yml.in`, builds the snap (docker `snapcore/snapcraft`), and — if the
credential secret exists — uploads it as `stable`.

Notes:
- x86_64 only for now (the template pins the x64 archive; add an arm64 part when needed).
- Classic confinement is required (broad permissions for a self-hosted assistant).
