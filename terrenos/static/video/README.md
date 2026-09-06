# Hero background videos

The landing page hero (`terrenos/templates/landing.html`) cross-fades through the
files listed below. **They are intentionally absent from the repo** — the page
falls back to `img/hero-poster.svg` when a file is missing, so the hero still
looks finished during review.

Expected filenames (add as many or as few as you have; the rotation adapts):

- `hero-01.mp4`
- `hero-02.mp4`
- `hero-03.mp4`

## Encoding guidance

| Setting  | Value                                                       |
|----------|-------------------------------------------------------------|
| Length   | 6–10 s, seamless loop                                       |
| Codec    | H.264 (`.mp4`) — add a `.webm` `<source>` above it if you have one |
| Size     | 1920×1080, target **under 3 MB each**                       |
| Audio    | None — strip the track entirely (the tag is `muted` anyway)  |
| Content  | Slow drone passes over the loteos; avoid fast pans or cuts   |

Keep frames mid-to-dark in the centre: the hero headline sits on top of a scrim
tuned for that range. A blown-out white sky behind the title will still pass
4.5:1 thanks to the scrim, but it looks washed out.

## Behaviour already handled in `landing.js`

- Autoplay is muted, `playsinline`, and loops.
- Playback pauses when the hero scrolls out of view or the tab is hidden.
- A pause/play control is rendered over the hero (bottom right).
- Under `prefers-reduced-motion: reduce` the `<video>` elements are removed
  before anything downloads, and the poster becomes the hero background.
- A missing or unplayable file drops out of the rotation silently.
