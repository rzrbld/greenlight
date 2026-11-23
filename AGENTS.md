# Greenlight Duo Lite app

This branch adapts upstream Greenlight v2.4.2 for Retroid Pocket Duo Lite running
BananaOS. It is a separately installed Slopetanium app, not firmware content.

- Keep app/runtime sources and CI here; do not modify BananaOS, vanilla PortMaster
  or another installed app to make this package work.
- Preserve upstream MIT attribution and both Xbox Remote Play and xCloud paths.
- Bundle required ARM64 desktop dependencies on writable app storage. Use the OS
  Adreno EGL/GLES/GBM drivers; do not replace system graphics or audio libraries.
- Store settings/authentication/cache outside the replaceable code directory.
  Never commit, print or publish credentials, auth tokens or user recordings.
- Use OS display orientation metadata. Do not assume both screens are 4:3.
- Public app assets are built and published by CI, never uploaded manually.
  Inherited upstream desktop/web publication is outside this fork's scope.
- Co-author every authored commit with:
  Co-authored-by: Codex <noreply@openai.com>
- Record build, startup, controls and actual streaming verification separately.
  A login screen is not evidence of working streaming or hardware video decode.
