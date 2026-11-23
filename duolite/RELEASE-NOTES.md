Duo.2 keeps video inside Chromium's GPU compositor instead of delegating
Wayland overlays. This addresses the display path implicated by frozen video,
rising shared memory and blocked graphics-buffer cleanup in the first preview.
Adreno GPU compositing remains enabled.

A local 720p60 H.264 test presented roughly 56–60 FPS after startup, used about
115 MB of shared memory and returned cleanly to the launcher. Physical output
and actual Xbox streaming still need user verification; this remains a preview.

For top-screen touch, use BananaOS Duo Lite Alpha46 or newer. That firmware
initializes both touch controllers automatically and assigns their displays.
Greenlight itself remains independently installed and updated by Slopetanium.

Install the Linux ARM64 ZIP. The sources archive contains the fork snapshot
and corresponding bundled dependency sources. Settings and sign-in stay outside
the replaceable app directory.
