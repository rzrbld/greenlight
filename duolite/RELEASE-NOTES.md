Duo.4 defaults to explicit 720p Xbox negotiation and uses native OS Turnip/Vulkan
rendering through ANGLE. On restored BananaOS Alpha46, the user confirmed clean,
responsive console streaming: their best result on this handheld so far.

Video decoding stays in software. Experimental Venus hardware decoding is not
included: it produced corrupted frames and device resets. The successful test
received 1280×720 H.264 at approximately 60 decoded frames/s. This does not
establish end-to-end latency or cloud-streaming performance.

Settings → Streaming provides 720p, 1080p, 1440p and Auto requests; bitrate is a
separate setting. Resolution negotiation adapts upstream PR #1752 by iu5gal.
The native panel scaling, top touch and controller mapping are preserved.

Use BananaOS Duo Lite Alpha46 with its OS Turnip driver. Install/update the
Linux ARM64 ZIP through Slopetanium; settings and Microsoft sign-in stay outside
the replaceable app directory. Public assets are built by GitHub Actions.
