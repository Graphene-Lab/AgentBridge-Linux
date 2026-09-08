# Flathub submission — AgentBridge (source build)

This folder contains the **drop-in directory** for the Flathub repository
(`flathub/flathub/io.github.graphene_lab.agentbridge/`): manifest, branding, icons and
`flathub.json`. The engine is **compiled from source** inside the Flathub build (the
model validated by the `sourcebuild-proof.yml` workflow) — no prebuilt archive is
wrapped for the engine itself.

## Layout

```
packaging/flathub/
├── build-submission.py          regenerates the manifest below (pinned hashes)
├── make-feed.py                 regenerates nuget-sources.json from a `dotnet restore
│                                --packages <dir>` (run on LINUX with the SAME SDK as the
│                                build — 10.0.400; Windows resolves different packages)
├── README.md                    this file
└── io.github.graphene_lab.agentbridge/
    ├── io.github.graphene_lab.agentbridge.yml   ← the Flathub manifest
    ├── flathub.json                             skip-arches: [aarch64] (add later)
    ├── branding/                                agent-run, agent-desktop, desktop
    │                                             entries, metainfo, giraffe.svg
    └── icons/hicolor/<size>/apps/<appid>.png    launcher icons (giraffe on gradient)
```

## How a version is published on Flathub

1. AgentBridge releases a new version (tag `v1.yy.MM.dd`).
2. Update the pin in `build-submission.py` (defaults) for that version:
   - `--version`, `--commit` (`git ls-remote … refs/tags/vX`), `--engine-sha256`
     (release asset digest from the GitHub API),
   - `--client-version`/`--client-sha256` (GiraffeAI latest), `--sdk-sha256` (fixed
     10.0.400 tarball), `--kokoro-sha256` (KokoroSharpBinaries asset).
3. Regenerate the NuGet feed **on Linux with SDK 10.0.400**:
   ```bash
   git clone --depth 1 --branch v1.yy.MM.dd https://github.com/Graphene-Lab/AgentBridge src
   dotnet restore src/AgentBridge.csproj -r linux-x64 --packages pkg \
     -p:SelfContained=true -p:PublishSingleFile=true \
     -p:IncludeNativeLibrariesForSelfExtract=true -p:NuGetAudit=false
   python3 make-feed.py pkg nuget-sources.json
   python3 build-submission.py nuget-sources.json
   ```
   (Windows produces a different — broken — feed: it misses linux RID packages such as
   `Microsoft.ML.OnnxRuntime.Gpu.Linux` and `Microsoft.NET.ILLink.Tasks`.)
4. Copy the whole app directory into your `flathub/flathub` checkout on branch
   `new-pr` and open the PR ("Add io.github.graphene_lab.agentbridge").

## Why these design choices (read before touching)

- **Runtime `org.gnome.Platform//50`**: the WebKitGTK desktop GUI exists only in the
  GNOME runtime (verified in the doctor smoke test; 48 is EOL per the Flathub linter).
- **Official .NET SDK tarball as a module source** instead of
  `org.freedesktop.Sdk.Extension.dotnet10`: the extension belongs to the freedesktop
  SDK, not the GNOME SDK — the tarball works with any runtime and keeps the SDK version
  identical to the one that generated the feed (consistency = reproducible restore).
- **Offline NuGet feed** (nuget-sources.json entries merged inline in the manifest):
  Flathub build commands have no network.
- **`kokoro.onnx` as a file source at the repo root**: the csproj
  `DownloadKokoroModel` target then copies it instead of curling at build time.
- **`agentbridge-payload` module**: Tools/ plugins and the .playwright driver are
  prebuilt data (from their own releases); they are overlaid from the official
  AgentBridge release archive of the same version. The engine `agent` binary in that
  archive is never copied. Reviewers may ask for plugin source builds later.
- **No aarch64 yet** (`flathub.json`): the arm64 SDK tarball would need a second pinned
  feed; add it when requested.

Sandbox note: the store submission uses the **narrowed** finish-args the Flathub linter
requires (wayland + fallback-x11, xdg-documents/xdg-download only, no `--filesystem=home`,
no explicit X11, no xdg-cache RW) — this differs from the self-hosted release bundle,
which keeps the broader sandbox. Justify this difference in the PR description.
