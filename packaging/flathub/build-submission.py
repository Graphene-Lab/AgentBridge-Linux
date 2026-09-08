"""Build the Flathub submission manifest for AgentBridge (source build).

Regenerates packaging/flathub/io.github.graphene_lab.agentbridge/
io.github.graphene_lab.agentbridge.yml from:
  - the offline NuGet feed JSON (see make_feed.py / README in this folder)
  - the pinned hashes below

Run:
  python build-submission.py <nuget-sources.json> [--version 1.26.09.08]

The engine module compiles AgentBridge from the pinned git commit, offline, using the
official .NET SDK tarball; data that the source build cannot produce offline (Tools/
plugins, .playwright driver) is overlaid from the AgentBridge release archive of the
same version (archive source). Mirrors the validated sourcebuild-proof workflow.
"""
import argparse
import json
import pathlib
import yaml

APP_ID = "io.github.graphene_lab.agentbridge"
BRAND = pathlib.Path(__file__).resolve().parent / APP_ID


def main():
    p = argparse.ArgumentParser()
    p.add_argument("feed", type=pathlib.Path, help="generated nuget-sources.json")
    p.add_argument("--version", default="1.26.09.08")
    p.add_argument("--commit", default="d26952371b7eec6530ab7f439050dad30231763c")
    p.add_argument("--sdk-sha256", default="7ad9d2db01512e41fd580a0630321bb70cd062d7fe4c5badfb4ce81ec1eddbb8")
    p.add_argument("--kokoro-sha256", default="0cfd5e79aab70a3d8c1a57dc639835110ddb32c9f5ff4fdd1f4db202ea43bb05")
    p.add_argument("--engine-sha256", default="39b474528be79ba3aea00b0d7d625a5bb62eb91185b5cd462084044c2a8e80d7")
    p.add_argument("--client-version", default="3")
    p.add_argument("--client-sha256", default="322571e0f9053ca5406c4cacf14df99529a5c24c62a8126a0063a544c29ef6e0")
    a = p.parse_args()

    nuget = json.loads(a.feed.read_text())
    engine_commands = f"""set -e
export DOTNET_ROOT="$PWD/dotnet-sdk"
export PATH="$DOTNET_ROOT:$PATH"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
export DOTNET_CLI_HOME="$PWD/.dotnet" NUGET_PACKAGES="$PWD/.nuget"
export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
mkdir -p nuget-sources
find . -maxdepth 3 -name '*.nupkg' -exec cp -n {{}} nuget-sources/ \\; 2>/dev/null || true
dotnet publish AgentBridge.csproj -c Release -r linux-x64 \\
  --self-contained true \\
  -p:PublishSingleFile=true \\
  -p:IncludeNativeLibrariesForSelfExtract=true \\
  -p:DebugType=None -p:DebugSymbols=false \\
  -p:RestoreSources="$PWD/nuget-sources" \\
  -p:NuGetAudit=false \\
  -o publish-out
test -d publish-out || {{ echo 'ERROR: dotnet publish produced no publish-out' >&2; exit 1; }}
mkdir -p /app/lib/agentbridge
cp -a publish-out/. /app/lib/agentbridge/
printf '%s\\n' '{a.version}' > /app/lib/agentbridge/agentbridge-version.txt"""

    sdk = "https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.400/dotnet-sdk-10.0.400-linux-x64.tar.gz"
    doc = {
        "app-id": APP_ID,
        "runtime": "org.gnome.Platform",
        "runtime-version": "48",
        "sdk": "org.gnome.Sdk",
        "command": "agent-run",
        "finish-args": [
            "--share=ipc",
            "--share=network",
            "--socket=x11",
            "--socket=wayland",
            "--socket=fallback-x11",
            "--socket=pulseaudio",
            "--device=dri",
            "--filesystem=home",
            "--talk-name=org.freedesktop.Notifications",
            "--talk-name=org.freedesktop.secrets",
        ],
        "modules": [
            {
                "name": "agentbridge-source",
                "buildsystem": "simple",
                "build-commands": [engine_commands],
                "sources": [
                    {
                        "type": "git",
                        "url": "https://github.com/Graphene-Lab/AgentBridge",
                        "commit": a.commit,
                        "x-checker-data": {"type": "git", "tag-pattern": r"^v([\d.]+)$"},
                    },
                    {
                        "type": "archive",
                        "url": sdk,
                        "sha256": a.sdk_sha256,
                        "dest": "dotnet-sdk",
                        "only-arches": ["x86_64"],
                    },
                    {
                        # Seed kokoro.onnx at the repo root so the csproj target copies it
                        # (build commands have no network on the Flathub infra).
                        "type": "file",
                        "url": "https://github.com/Lyrcaxis/KokoroSharpBinaries/releases/download/v2.0.0/kokoro.onnx",
                        "sha256": a.kokoro_sha256,
                    },
                    *nuget,
                ],
            },
            {
                # Data the source build cannot produce offline (Tools/ plugins and the
                # .playwright driver), from the official release archive of this version.
                # Only data folders are copied — the engine itself is compiled from source.
                "name": "agentbridge-payload",
                "buildsystem": "simple",
                "sources": [
                    {
                        "type": "archive",
                        "url": f"https://github.com/Graphene-Lab/AgentBridge/releases/download/v{a.version}/agentbridge-linux-x64.tar.gz",
                        "sha256": a.engine_sha256,
                        "strip-components": 0,
                        "only-arches": ["x86_64"],
                    }
                ],
                "build-commands": [
                    "install -d /app/lib/agentbridge",
                    "cp -a Tools /app/lib/agentbridge/ 2>/dev/null || true",
                    "cp -a .playwright /app/lib/agentbridge/ 2>/dev/null || true",
                ],
            },
            {
                "name": "giraffeai-webclient",
                "buildsystem": "simple",
                "build-commands": [
                    "mkdir -p /app/lib/agentbridge/GiraffeAIWebClient",
                    "cp -a . /app/lib/agentbridge/GiraffeAIWebClient/",
                    f"printf '%s\\n' '{a.client_version}' > /app/lib/agentbridge/GiraffeAIWebClient/version.txt",
                ],
                "sources": [
                    {
                        "type": "archive",
                        "url": f"https://github.com/Graphene-Lab/GiraffeAI/releases/download/v{a.client_version}/giraffeai-{a.client_version}.zip",
                        "sha256": a.client_sha256,
                        "strip-components": 0,
                    }
                ],
            },
            {
                "name": "branding",
                "buildsystem": "simple",
                "sources": [
                    {"type": "dir", "path": "branding"},
                    {"type": "dir", "path": "icons"},
                ],
                "build-commands": [
                    "install -Dm755 agent-run /app/bin/agent-run",
                    "install -Dm755 agent-desktop /app/bin/agent-desktop",
                    f"install -Dm644 {APP_ID}.desktop /app/share/applications/{APP_ID}.desktop",
                    f"install -Dm644 {APP_ID}.Terminal.desktop /app/share/applications/{APP_ID}.Terminal.desktop",
                    f"install -Dm644 {APP_ID}.metainfo.xml /app/share/metainfo/{APP_ID}.metainfo.xml",
                    "for s in 64 128 256 512; do install -Dm644 icons/hicolor/${s}x${s}/apps/"
                    + f"{APP_ID}.png /app/share/icons/hicolor/${{s}}x${{s}}/apps/{APP_ID}.png; done",
                ],
            },
        ],
    }
    out = BRAND / f"{APP_ID}.yml"
    out.write_text(
        "# AgentBridge — Flathub manifest (source build, pinned). Generated by\n"
        "# build-submission.py — do not edit by hand; see packaging/flathub/README.md.\n"
        + yaml.safe_dump(doc, sort_keys=False, default_flow_style=False, width=1000000),
        encoding="utf-8",
    )
    print(f"wrote {out} (nuget sources: {len(nuget)})")


if __name__ == "__main__":
    main()
