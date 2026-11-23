Duo.3 fixes the frozen/black video path by disabling Chromium GPU rendering and
keeping client buffers in shared memory. Weston retains native Adreno display
composition. Disabling delegated Wayland overlays in Duo.2 was insufficient.

The user confirmed moving console-stream video, audio, controller input and top
touch with this setup. Playback is still choppy; performance work continues.
This is a functional bring-up preview, not a claim of smooth streaming or verified
hardware video decoding. Forced 1× device scaling is not used because it cropped
the output. Cloud streaming needs separate testing.

Use BananaOS Duo Lite Alpha46 or newer for automatic top-touch initialization.
Install/update the Linux ARM64 ZIP through Slopetanium; settings and Microsoft
sign-in stay outside the replaceable app directory.
