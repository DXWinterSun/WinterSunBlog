# Sam quiz — character generator

The quiz at `/sam/quiz/` matches you against every Sam Rockwell character. It
ranks by **raw accumulated affinity** (the `chars:{}` map on each option),
tie-broken by how close your 6-axis profile sits to the character's. Those
affinity maps are **generated**, not hand-written, so that every character —
including a brand-new one — gets a fair, even niche and nobody dominates.

## Single source of truth

Everything lives in **`sam/quiz/index.html`**:

- `CHARS[]` — the roster and each character's `profile` (0–10 on guile / forbear
  / chaos / raw / romance / grace). Same data as the gallery
  (`sam/many-faces/index.html`), which is where you copy a new character from.
- `QUESTIONS[]` — the question text and each option's `dims` (+ optional `lineCN`
  for the English-quote question).

`forces.json` here pins specific characters onto specific options (signatures
that must hold regardless of the fit math): the quote lines belong to their
speakers, the colour question matches each character's colour card, and a few
"middling" characters get a guaranteed thematic niche.

## Adding a character

1. In `sam/quiz/index.html`, add the character to `CHARS[]` and `PALETTE_NAMES`
   (copy their fields — **including `profile`** — from `sam/many-faces/index.html`;
   `inscription.line/gloss` → `line/lineCN`, `accentNameCn` → `accentCN`, etc.).
   Bump the “N 个角色” count on the intro and on the Sam-tab card in
   `sam/index.html`.
2. *(optional)* Add 1–2 signatures for them in `forces.json` on options that fit
   their profile — otherwise the generator still gives them a niche automatically.
3. Regenerate:

   ```
   node tools/quiz-gen/build.js
   ```

4. Check the printed report (`reachable = N/N`, appearances even, everyone
   primary ≥ once), confirm the page still compiles, eyeball a couple of results,
   then commit + deploy (the site builds from `main`).

The question wording/dims are preserved by `build.js`; only the `chars:{}` maps
are rewritten.
