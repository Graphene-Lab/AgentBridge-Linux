# AgentBridge for Linux — Flatpak desktop distribution

[![Latest Linux release](https://img.shields.io/github/v/release/Graphene-Lab/AgentBridge-Linux?style=for-the-badge&color=1f6feb&label=Linux%20Flatpak)](https://github.com/Graphene-Lab/AgentBridge-Linux/releases/latest)
[![Download](https://img.shields.io/badge/Download-238636?style=for-the-badge&logo=flatpak&logoColor=white)](https://github.com/Graphene-Lab/AgentBridge-Linux/releases/latest/download/agentbridge-linux-x86_64.flatpak)

This repository publishes **AgentBridge for Linux** as a proper **desktop application**:
the engine plus the **Giraffe AI** web client rendered in its own desktop window
(WebKitGTK) with an application icon in the launcher — a normal Linux desktop app, not a
console program.

Every **AgentBridge GitHub release** is picked up automatically (hourly check) and a new
Flatpak is built and published here, so the engine stays current without any manual step.

---

## What is AgentBridge?

> Replace employees with easy, autonomous and effective Personal AI Assistant.

AgentBridge is a self-hosted server that runs its own AI agents behind two primary
interfaces in a single process: a full-screen chat terminal (TUI) and an HTTP API that
speaks the standard OpenAI protocol, so any OpenAI-compatible client drives the same
agents.

Chat in the terminal (or in the desktop window, or with your own OpenAI client) while
scripts, bots, and apps use the same agents on the same port: same process, same
conversations, no bridges, no synchronization.

- **You, in the desktop** — the bundled **Giraffe AI** client opens in its own window,
  auto-connected to the local engine. Web apps run in "desktop mode": a web view with an
  application icon, not a browser tab.
- **You, in the terminal** — a modern full-screen chat UI (Terminal.Gui) with streaming
  replies, a `/` command palette, file attachments, voice dictation and in-process neural
  text-to-speech.
- **Any OpenAI-compatible client** — SDKs, bots and scripts talk plain
  `POST /v1/chat/completions` to the same agents.

The agent core is our own engine (AIOrchestrator): an agent's abilities are **compiled
.NET assemblies** loaded as plugins from the `Tools/` folder and driven in-process. The
agent drafts documents, works on spreadsheets and presentations, interacts with email and
Telegram, browses the web, produces podcasts and answers from your own knowledge base — a
plain folder on disk. **Your files never leave your machine.**

Everything runs on your own hardware, self-hosted. No cloud account, no uploads: connect
the agent to your preferred AI — a local model (Ollama, ExLlamaV2, …) or any
OpenAI-compatible provider.

> Full documentation: [graphenelab.it/AgentBridge](https://graphenelab.it/AgentBridge/) ·
> source: [Graphene-Lab/AgentBridge](https://github.com/Graphene-Lab/AgentBridge) ·
> license: **AGPL-3.0**

---

## Install

Requirements: [Flatpak](https://flatpak.org/setup/) with the **Flathub** remote
(first install also downloads the GNOME runtime from Flathub).

```bash
# one time: add the Flathub remote (needed for the shared runtime)
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# download + install the latest desktop bundle — x86_64 (Intel/AMD), or the
# aarch64 link below on ARM64 (Raspberry Pi 4/5, Apple-silicon Asahi, …)
flatpak install --user -y \
  https://github.com/Graphene-Lab/AgentBridge-Linux/releases/latest/download/agentbridge-linux-x86_64.flatpak

# ARM64:
# flatpak install --user -y \
#   https://github.com/Graphene-Lab/AgentBridge-Linux/releases/latest/download/agentbridge-linux-aarch64.flatpak
```

Launch it from your desktop environment (icon **AgentBridge**) or from the terminal:

```bash
flatpak run io.github.graphene_lab.agentbridge
```

**Update** — a new release appears here automatically at each AgentBridge release;
re-install with the same command (or `--reinstall`) to pick it up (use the `-aarch64`
asset URL on ARM64):

```bash
flatpak install --user -y --reinstall \
  https://github.com/Graphene-Lab/AgentBridge-Linux/releases/latest/download/agentbridge-linux-x86_64.flatpak
```

### What you get

| Launcher entry | What it does |
|---|---|
| **AgentBridge** | Desktop app: starts the engine (headless) if needed and opens the **Giraffe AI** chat client in its own window, already connected to the local engine |
| **AgentBridge (Terminal)** | The classic full-screen terminal UI (TUI) + local server, in a terminal |

The bundled client is the latest **Giraffe AI** release at build time; the engine is the
official self-contained AgentBridge **linux-x64 / linux-arm64** release of the same build.

## First start

1. Launch **AgentBridge**.
2. The window asks you to configure an **AI provider** — point it at your local model
   (`http://localhost:11434/` for Ollama) or at any OpenAI-compatible API you use.
   *(The AgentBridge engine itself is already pre-configured as a provider named
   "AgentBridge", selected by default.)*
3. Start typing: the agent runs on your machine and reads/writes your own files.

The engine is healthy when it answers on `http://localhost:5290/health` (the standard
port, configurable in `PersistentData/appsettings.json`).

## Configuration, data and updates

- **Per-app data** lives under `~/.var/app/io.github.graphene_lab.agentbridge/data/`:
  - `agentbridge/engine/` — the running engine copy (first launch materializes it from
    the read-only package; `PersistentData/` inside it holds all user-editable JSON
    config, exactly like a normal install).
  - `agentbridge/logs/` — engine logs (`desktop-headless.log` for the desktop mode).
- **Version pinning**: the packaged engine ships with updates disabled (`--no-update`) —
  the new version arrives with the next Flatpak build (automatic). Power users can pass
  explicit engine arguments, e.g.
  `flatpak run --command=agent-run io.github.graphene_lab.agentbridge --headless`,
  and manage in-app auto-updates themselves.
- **Sandbox**: this package keeps a deliberately broad sandbox (network, home folder,
  audio, GPU) — it is the Flatpak equivalent of the classic `~/.agentbridge` archive
  install of a self-hosted server, not a restricted store app.

## Repository layout

```
packaging/agentbridge.yml.tmpl   flatpak manifest template (rendered per release)
packaging/branding/              launcher scripts, .desktop entries, metainfo, giraffe.svg
.github/workflows/linux-release.yml  the automatic build + publication pipeline
```

Build and publication pipeline: see [.github/workflows/linux-release.yml](.github/workflows/linux-release.yml)
and [AGENTS.md](AGENTS.md).

## Trademark / credits

The desktop GUI is the **Giraffe AI** web client
([Graphene-Lab/GiraffeAI](https://github.com/Graphene-Lab/GiraffeAI)); the giraffe logo
asset is from that project.
