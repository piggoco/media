# piggo-media

Piggo's media library for organic social content.

1. Claude (or anyone) adds an entry to `wanted.yaml`: file name, download URL, source, credit, licence, people status.
2. On push, the **Fetch media** GitHub Action downloads new images into `media/` (long edge max 2160 px) and updates `media/CREDITS.md`.
3. Claude pulls the repo and uses the images in the ffmpeg renderer.

Rules (from the Organic Social project, 01-brand-voice.md "Images and people"):
- Sources: own photos, Unsplash/Unsplash+, Creative Commons with commercial use (credit required), licensed stock.
- Identifiable people only with a model release (`people: released`) or written consent.
- For Unsplash, use the URL from the connector's `download_asset` (it registers the download, as Unsplash requires).

Own photos can be committed straight into `media/` – add a row for them in `wanted.yaml` without a `url`, or note them in `media/CREDITS.md`.
