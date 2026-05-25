# FTC Agent Village

> 120 specialized agents that execute the FTC pipeline under the
> [FTC_MASTER_CONTEXT.md](../FTC_MASTER_CONTEXT.md) constitution.

## TL;DR

- **One source of truth:** every agent inherits from `FTC_MASTER_CONTEXT.md`.
- **One registry:** [`REGISTRY.yaml`](./REGISTRY.yaml) lists all 120 agents with
  role, model, tools, gates, handoffs, and a tight system prompt.
- **One gate:** `brand-steward` is the final yes/no on anything that leaves
  the building.

## Tiers (16)

| Tier | Domain | Members |
| :--- | :--- | ---: |
| 0 | Orchestrators | 5 |
| 1 | Concept & Theology | 10 |
| 2 | Aesthetic Direction | 10 |
| 3 | Visual Production | 10 |
| 4 | Mockups | 5 |
| 5 | Video | 8 |
| 6 | Scraping & Research | 8 |
| 7 | Quality Assurance | 8 |
| 8 | Copy & Editorial | 6 |
| 9 | Distribution | 5 |
| 10 | Marketing & Promo | 5 |
| 11 | Ops & Compliance | 4 |
| 12 | Analytics | 4 |
| 13 | Infrastructure | 5 |
| 14 | Agent Interoperability | 17 |
| 15 | Cinematic Ads | 10 |
| | **Total** | **120** |

## Standard Lifecycle (one drop)

```
1. drop-architect          → drop_brief.yaml
2. reference scrapers      → reference_synthesis.json
3. theology-concept-arch.  → concepts/*.json (theological_core)
4. aesthetic-director      → art_direction/*.yaml
5. tier 2 specialists      → typography, layout, print, material, silhouette
6. tier 3 prompt engineers → prompts/seedream/*.txt, hero_shots/*.png
7. tier 4 mockups          → mockups/*.png
8. tier 5 video            → promos/*.mp4
9. tier 7 QA               → qa_reports/*.json
10. quality-gate-keeper    → gate_results.json (PASS / FLAG / KILL)
11. brand-steward          → approval_ledger.json
12. tier 8 copy            → captions, drop story, PDP, microcopy
13. tier 9 distribution    → SKU, pricing, Shopify sync
14. tier 10 marketing      → IG, TikTok, email, press
```

## Gates That Cannot Be Bypassed

- `forbidden_term_count == 0` (Section 1)
- `luxury_score >= 0.82` (Section 5)
- `theology_depth >= 0.75` (Section 5)
- `JSON schema valid` (Section 4)
- `negative_to_positive_ratio >= 0.5`
- `no key leakage in any artifact` (Section 6)

Anything in luxury_score `[0.75, 0.82)` is **flagged for human review**, not
auto-killed.

## How To Invoke

This registry is framework-agnostic. The same agent definitions can be
loaded into:

- **LangGraph:** each agent is a node; `handoff_to` becomes edges; gates
  become conditional edges.
- **CrewAI:** each agent is a `Crew` role; `consumes`/`produces` become
  task contracts.
- **OpenAI Agents SDK / Anthropic Agents:** each agent maps to a tool-using
  LLM with the `system_prompt` field as its system message.
- **Manual / Cursor:** open `REGISTRY.yaml`, copy a `system_prompt`, paste
  into a Cursor chat with the relevant inputs.

## Adding An Agent

1. Append to `REGISTRY.yaml` with the next `FTC-NNN` id.
2. Choose a tier or create a new one (update the `tiers:` block + this
   README's table).
3. Document `consumes`, `produces`, `gates`, `handoff_to`.
4. Write a 2-5 line `system_prompt` that reads like a sharp brief, not a
   tutorial.
5. Open a PR; `brand-steward` reviews.

## Interoperability Pod (expanded in v1.3)

Tier 14 now includes 17 agents for multi-agent collaboration and cross-model routing:

- `cline-execution-pilot`
- `openclaw-parallel-orchestrator`
- `claude-consensus-lead`
- `model-router-federator`
- `handoff-protocol-engineer`
- `merge-readiness-auditor`
- `alliance-telemetry-auditor`
- `langgraph-flow-compiler`
- `crewai-mission-allocator`
- `autogen-dialog-conductor`
- `openai-agents-sdk-bridge`
- `anthropic-agent-bridge`
- `cursor-cloud-executor`
- `branch-isolation-manager`
- `prompt-regression-sentinel`
- `replay-debug-coordinator`
- `ensemble-verdict-judge`

## Cinematic Ad Pod (new in v1.3)

Tier 15 adds ten agents for realistic trap-cinematic campaign production:

- `trap-cinema-creative-director`
- `teen-hype-culture-calibrator`
- `boohooman-reference-harvester`
- `christian-trap-symbolism-editor`
- `product-lineup-shot-planner`
- `openrouter-multimodal-router`
- `visual-qwen-shot-generator`
- `cinematic-video-prompt-engineer`
- `audio-speech-score-designer`
- `ad-performance-rerank-analyst`

This pod is OpenRouter-first and explicitly supports image, embeddings, audio, video, rerank, speech, and transcription workloads with Novita video fallback logic.

## Slots Reserved (room toward 130)

`REGISTRY.yaml` ends with an `OPEN SLOTS` block: livestream-drop-director,
ugc-remix-curator, creator-whitelist-manager, ad-fraud-signal-monitor,
motion-logo-microanimator, scent-and-space-retail-translator,
seasonal-lookbook-reconstructor, generative-casting-agent,
demand-spike-allocator, multilingual-hype-copy-localizer.

## Cross-Pollination Note

This village was authored without access to other repos in the
`calebhomwe/*` org (this sandbox is scoped to `calebhomwe/skydaze` only).
If you want patterns lifted from existing agents in your other repos, share
the repo name or paste the agent file and the next pass will fold them in.
