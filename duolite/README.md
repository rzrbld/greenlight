# Greenlight on Duo Lite

This fork targets BananaOS on Retroid Pocket Duo Lite, with an ARM64 Electron
app and its own small Weston session. The OS supplies the Adreno graphics
drivers, audio routing and device metadata. No firmware modification is needed.

## Install and update

Add `rzrbld/greenlight` as an app repository in Slopetanium. Select the
`Greenlight-Duo-<version>-linux-arm64.zip` release asset, not the source archive.
The ZIP has one launcher, `Greenlight Duo.sh`, and supports exFAT storage.
Open its tile from the BananaOS main menu.

Sign in using the Microsoft device-code URL and code displayed by the app.
Xbox Remote Play requires a configured Xbox console; cloud gaming requires
the appropriate Microsoft account access and service availability.

Code and desktop dependencies live inside the replaceable app directory.
Settings and authentication stay in `$XDG_CONFIG_HOME/greenlight-duo`
(normally `/data/home/.config/greenlight-duo`). Cache and startup logs live in
`$XDG_CACHE_HOME/greenlight-duo`. Slopetanium owns app updates; the upstream
desktop auto-updater is disabled on this device.

## Controls and display

- D-pad or left stick moves focus; A selects; B goes back.
- Hold Select + Start for 1.2 seconds to quit.
- Streaming uses Greenlight's existing controller input. The measured Retroid
  controller mapping is normalized inside this app; external standard
  controllers keep their mapping and native rumble interfaces.
- The top panel uses its full landscape area, rendered at logical 960×540.
  The bottom panel is disabled during the session. Orientation comes from OS
  hardware metadata, converted to Weston's inverse output transform.

## Validation status

On-device startup, inline device-code authentication, 960×540 viewport, native
Adreno FD610 rendering through ANGLE/GLES, and measured controller button
normalization have been checked. The initial upside-down display transform
has been corrected; physical confirmation is still pending.

The first two previews could freeze the physical image while decode counters
continued, then retain GPU buffers and hang during cleanup. Disabling delegated
overlays alone did not fix the real stream. Duo.3 disables Chromium GPU rendering
and keeps its buffers in shared memory; Weston still uses native Adreno for final
display composition. The user confirmed console-stream video, audio, controller
input and top touch with this setup. Playback remains choppy and performance
work is ongoing. A forced 1× device scale cropped the output and is not enabled.

Cloud streaming, analog trigger behavior and stream rumble still need separate
account-backed device tests. Hardware video
decoding is **not verified**: Chromium reports no decoding profiles in the
current probe. A working GPU renderer does not establish video decode support.

## Build

Use Node 24, Yarn 1.22.22, Python 3 and Docker on an x86-64 Linux host:

```sh
yarn install --frozen-lockfile --non-interactive
node --experimental-strip-types duolite/test-gamepad.mjs
cd packages/desktop
../../node_modules/.bin/nextron build --no-pack
../../node_modules/.bin/electron-builder --linux dir --arm64 --config ../../duolite/electron-builder.yml
cd ../..
docker build -t greenlight-duo-runtime -f duolite/Dockerfile.runtime .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/app" greenlight-duo-runtime python3 /app/duolite/extract-runtime.py --electron /app/duolite/build/electron/linux-arm64-unpacked --output /app/duolite/build/runtime
python3 duolite/package.py
python3 duolite/test-package.py duolite/build/Greenlight-Duo-*-linux-arm64.zip
```

The runtime collector checks ARM64 ELF dependencies and preserves the OS
glibc/GPU libraries. Debian package versions, copyright files and Electron's
licenses accompany the payload. CI also publishes exact Debian dependency
source packages, the pinned Electron FFmpeg source and a source snapshot.

Only CI publishes public app archives. Tags matching `v<version>` (for example
`v2.4.2-duo.1`) build and release; manual runs produce reviewable artifacts.
Inherited upstream workflows are retained as disabled reference files here.

## Upstream

Based on [unknownskl/greenlight](https://github.com/unknownskl/greenlight),
stable tag v2.4.2. Upstream MIT attribution is preserved in the repository and
installed package. The Duo-specific adapter, launcher and packaging live in
this directory; the original application stays under `packages/desktop`.
