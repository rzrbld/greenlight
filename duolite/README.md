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

- D-pad or left stick moves focus. Face buttons use Xbox positions: physical
  B sends Xbox A, A sends B, Y sends X and X sends Y. Thus physical B selects
  and physical A goes back in the app menus. This applies to the built-in
  controller in both menus and streams; external controllers keep their mapping.
- Press the built-in Home button to quit. Select + Start stays available to
  the Xbox stream and never quits Greenlight. External Guide buttons retain
  their normal Xbox behavior.
- Streaming uses Greenlight's existing controller input. The measured Retroid
  controller mapping is normalized inside this app; external standard
  controllers keep their mapping and native rumble interfaces.
- The top panel uses its full landscape area, rendered at logical 960×540.
  The bottom panel is disabled during the session. Orientation comes from OS
  hardware metadata, converted to Weston's inverse output transform.

## Validation status

Duo.4 uses Electron 42 ARM64 with ANGLE over the OS Turnip/Vulkan driver and
explicit 720p Xbox negotiation. On restored BananaOS Alpha46, the user confirmed
clean, responsive video and described it as the best result on this handheld.
The measured stream was 1280×720 H.264 at approximately 60 decoded frames/s.
Video decoding is explicitly software; Vulkan accelerates rendering/composition.
This is not a measurement of button-to-photon latency.

Earlier ANGLE OpenGL paths froze the physical image. Duo.3's CPU-rendering
fallback worked but was choppy. Experimental Venus hardware decoding produced
corruption and resets and is excluded from this app configuration. The complete
original Alpha46 kernel, device tree and root were restored and hash-verified
before the successful Duo.4 trial. Forced 1× scaling cropped the screen and
remains disabled. Physical orientation, top touch and controller operation have
been confirmed by the user.

Cloud streaming, analog trigger behavior and stream rumble still need separate
account-backed device tests.

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

## Stream resolution

Settings → Streaming now requests 720p, 1080p, 1440p or Auto. Duo Lite defaults
to 720p. This sends Xbox's `VideoPreference` and
`userRequestedResolutionUpdate` control messages and matching client dimensions;
it does not change the console's TV output or the app's display scaling. The
bitrate slider remains a separate bandwidth limit. Implementation adapted from
[upstream PR #1752](https://github.com/unknownskl/greenlight/pull/1752),
`iu5gal`, head `e4f8b3942e21a8b1a1b2aea1fea6fc63c40cf6c9`.

The isolated Duo test received 1280×720 H.264 after previously receiving 1440p.
Resolution negotiation is verified separately from acceleration: experimental
Venus/VA-API tests have shown corrupt frames and GPU-path resets. The production
launcher is not switched to those unvalidated configurations.
