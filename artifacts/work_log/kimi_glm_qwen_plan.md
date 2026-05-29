# Qwen-VL3 + 22 Kimi + GLM 4.6/4.5-Air → GPT Image 2 / Seedream-4 (DRY-RUN PLAN)

This file is produced when `OPENROUTER_API_KEY` is absent. It shows
exactly what the worker would do if the key were set.

## Pipeline
1. **22 Kimi K2 agents** brainstorm in parallel → 22 design briefs
2. **GLM 4.6** ranks the 22 briefs → top N
3. **GLM 4.5-Air** runs forbidden-term safety scan
4. **openai/gpt-image-1** generates 4:5 PNGs (832x1024)
5. Fallback if primary fails: **fal-ai/bytedance/seedream/v4/text-to-image**
6. **qwen/qwen3-vl-235b-a22b-instruct** reviews each PNG for brand alignment

## To run for real
```bash
export OPENROUTER_API_KEY=sk-or-...    # required
export FAL_KEY=...                      # optional (Seedream fallback)
FTC_RUN_MODE=real python3 workers/qwen_kimi_glm_design_worker.py
```

## The 22 briefs that would be submitted right now (dry-run stubs)

| # | Agent | Angle | Brief seed |
| ---: | :--- | :--- | :--- |
| 1 | `K-01` kimi-hymn-fragmentarian | Hymn fragments at Sermon volume | Pull a 2-4 word fragment from Wesley/Watts/Newton hymns; set in heavyweight serif at maximum scale; bone or onyx ground. |
| 2 | `K-02` kimi-augustine-curator | Augustine Confessions as graphic tee | Quote Augustine in fragment form (e.g. 'LATE HAVE I LOVED THEE'); hand-drawn marker treatment; CPFM naive-hand aesthetic; bone ground. |
| 3 | `K-03` kimi-greek-typographer | Greek NT words as decorative type | Single Greek word ΑΓΑΠΗ/ΛΟΓΟΣ/ΧΑΡΙΣ; massive grotesque weight; Cey Adams 3-color discipline; onyx ground. |
| 4 | `K-04` kimi-hebrew-typographer | Hebrew words at high contrast | Single Hebrew word שלום/חסד/אמונה; bold serif; Eric Haze graffiti weight without graffiti; bone ground. |
| 5 | `K-05` kimi-latin-formalist | Latin phrases in Trajan register | Latin phrase (SOLI DEO GLORIA, LUX MUNDI, PAX VOBISCUM); Trajan or Cinzel; circular emblem composition (Sk8thing); bone ground. |
| 6 | `K-06` kimi-diaspora-place-marker | Diaspora cities as primary content | Diaspora city name (DMV, BROOKLYN, PECKHAM, LAGOS); tour-poster layout (Awake NY); secondary line lists dates; onyx ground. |
| 7 | `K-07` kimi-historical-figure | Historical Christian figures | Name of historical figure (AUGUSTINE, BONHOEFFER, TUBMAN, THURMAN, DAY); halftone-portrait Pyer Moss aesthetic; bone ground. |
| 8 | `K-08` kimi-trinitarian-stacker | Trinitarian three-line phrases | Trinitarian stack (FATHER/SON/SPIRIT; MERCY/GRACE/PEACE); Cey Adams three-line stack discipline; onyx ground. |
| 9 | `K-09` kimi-cpfm-naive-hand | CPFM naive-hand discipline | Single hymn or Augustine fragment; deliberately wonky hand-drawn type; marker scribble accents; bone ground; CPFM grade. |
| 10 | `K-10` kimi-cey-adams-bold | Cey Adams 3-color discipline | Single Greek word centered; massive Helvetica Black; max 3 colors total; onyx ground. |
| 11 | `K-11` kimi-eric-haze-graffiti | Eric Haze graffiti weight without graffiti | Single Hebrew or Greek word at Impact 240pt with subtle drips; no actual graffiti; bone ground. |
| 12 | `K-12` kimi-sk8thing-emblem | Sk8thing layered-emblem aesthetic | Circular emblem with Latin phrase wrapping; Trajan inside; BAPE album-cover composition; onyx ground. |
| 13 | `K-13` kimi-brain-dead-halftone | Brain Dead halftone print discipline | Halftone dot field suggesting a portrait; Latin or Greek caption; newspaper register; bone ground. |
| 14 | `K-14` kimi-heron-preston-industrial | Heron Preston industrial typography | Vertical wheatpaste panel with Latin phrase; Impact 180pt; torn-edge marks; onyx ground. |
| 15 | `K-15` kimi-awake-ny-tour-poster | Awake NY tour-poster discipline | Hymn fragment as tour headline; city list below; thin horizontal rules; bone ground. |
| 16 | `K-16` kimi-pyer-moss-essay-tee | Pyer Moss historical-essay tee | Historical figure name + their tradition (AUGUSTINIAN/METHODIST/MYSTIC); halftone portrait above; bone ground. |
| 17 | `K-17` kimi-verdy-single-motif | Verdy single-motif discipline | One symbol (LAMP, VINE, STONE, OLIVE); hand-drawn; wonky caption below; bone ground. |
| 18 | `K-18` kimi-illuminated-mss | Medieval illuminated manuscript reference | Illuminated capital + Augustine quote in Cinzel; decorative border; bone ground. |
| 19 | `K-19` kimi-shout-tier-maximalist | Maximum intensity all-over-print | Greek or Hebrew word repeated 45+ times across the field; hero block over the top; onyx ground. |
| 20 | `K-20` kimi-quiet-statement | Statement tier at the quiet end | Three-line trinitarian phrase; sparse layout; thin underscore mark; bone ground. |
| 21 | `K-21` kimi-boohooman-mens-headline | BoohooMAN men's editorial headline pacing — restraint palette | Drop headline composition: top eyebrow rule, hero word at Impact 240pt, accent slash, sub-line, bottom rule with city roster. BoohooMAN edit |
| 22 | `K-22` kimi-boohooman-photo-overlay | BoohooMAN men's photo-overlay pacing — abstracted figure | Composition: top brand bar, suggested figure (halftone dot column, no actual photography), bottom hero word slab. BoohooMAN editorial 'model |