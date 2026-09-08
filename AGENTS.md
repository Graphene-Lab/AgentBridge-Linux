# AGENTS.md — AgentBridge-Linux (for AI coding agents)

This repo is the **automatic Linux desktop (Flatpak) distribution** of AgentBridge. It
does NOT contain the application source — the app lives upstream in
`Graphene-Lab/AgentBridge` (engine) and `Graphene-Lab/GiraffeAI` (the web client that
becomes the desktop GUI). This repo only packages those public release artifacts and
publishes the resulting Flatpak.

## How a release happens (no manual steps)

`.github/workflows/linux-release.yml` runs on a schedule (hourly, `:23`) plus
`workflow_dispatch`. It compares the latest `Graphene-Lab/AgentBridge` release tag with
this repo's latest release tag; when a new upstream version exists it:

1. reads the engine archive **sha256 digests** for BOTH architectures straight from the
   release API (no ~400 MB double downloads — flatpak-builder fetches the archive itself),
2. downloads the latest GiraffeAI web-client zip,
3. renders `packaging/agentbridge.yml` from `packaging/agentbridge.yml.tmpl`
   (placeholders `@@VERSION@@ @@SHA256_X86_64@@ @@SHA256_AARCH64@@ @@CLIENT_VERSION@@
   @@CLIENT_SHA256@@`),
4. generates launcher icons from `packaging/branding/giraffe.svg`,
5. **x86_64**: builds the Flatpak in the `ghcr.io/flathub-infra/...:gnome-48` container,
   smoke-checks with `agent-desktop --doctor`, creates the GitHub Release and uploads the
   x86_64 assets,
6. **aarch64** (separate host job, qemu-user + apt flatpak): appends the aarch64 bundle to
   the same release after the x86_64 job.

Stable asset names: `agentbridge-linux-x86_64.flatpak` / `agentbridge-linux-aarch64.flatpak`
(+ `.sha256` each). No secrets. No changes to the upstream AgentBridge repo are needed
(its release.ps1 / release.yml are untouched).

## Packaging model — read this before touching the manifest

- `/app/lib/agentbridge` is a **read-only image** = the exact contents of the AgentBridge
  linux-x64 release archive + `agentbridge-version.txt` marker + the pre-seeded
  `GiraffeAIWebClient/` (with `version.txt`).
- `/app` is read-only in Flatpak, but the engine persists its user config under
  `PersistentData/` NEXT TO the executable (AppConfig). The launchers
  (`packaging/branding/agent-run`, `agent-desktop`) therefore **materialize** the image
  into `$XDG_DATA_HOME/agentbridge/engine` on first launch and **overlay-refresh** it when
  the version marker changes (never deleting `PersistentData` — it is not part of any
  release archive). Keep this invariant: binaries/docs may refresh, user state must never
  be touched by a re-materialization.
- The engine is **version-pinned**: the launchers append `--no-update` when invoked with
  no arguments (distro-package semantics — updates arrive with the next Flatpak build).
- Both launcher scripts (shell + python) must stay mirror-synced on the materialization
  logic; `agent-desktop --doctor` is the CI smoke entry point and must stay runnable
  headless (no Gtk/WebKit construction in doctor mode).

## Conventions

- Changes to packaging behavior must keep the auto-publish workflow green: always run
  the build via `workflow_dispatch` after editing the manifest/branding and verify the
  doctor output and the release asset.
- Icons are generated in CI from `packaging/branding/giraffe.svg` (GiraffeAI brand):
  white giraffe on the `#6c5ce7 → #3b2f9e` gradient rounded square. Do not commit
  generated PNGs or the rendered `packaging/agentbridge.yml` (gitignored).
- Comments and documentation in English, as everywhere in this project family.
