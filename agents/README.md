# FTC Agent Village

> 250 specialized agents that execute the FTC pipeline under the
> [FTC_MASTER_CONTEXT.md](../FTC_MASTER_CONTEXT.md) constitution.

## TL;DR

- **One source of truth:** every agent inherits from `FTC_MASTER_CONTEXT.md`.
- **One registry:** [`REGISTRY.yaml`](./REGISTRY.yaml) lists all 250 agents with
  role, model, tools, gates, handoffs, and a tight system prompt.
- **One gate:** `brand-steward` is the final yes/no on anything that leaves
  the building.
- **DeepSeek Flash v4** via OpenRouter routes all high-throughput concept, copy,
  scanning, and ranking tasks. Override slug via `DEEPSEEK_FLASH_MODEL` env var.
- **YouTube Intelligence Pod** (Tier 16) harvests transcripts from curated channels
  to synthesize brand-relevant style tokens. Run via `make youtube-harvest`.

## Tiers (29)

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
| 16 | YouTube Intelligence | 10 |
| 17 | DeepSeek Flash Research | 10 |
| 18 | OpenClaw / Hermes Execution | 10 |
| 19 | Cline AI Execution | 10 |
| 20 | Extended Market Intelligence | 10 |
| 21 | Demand & Retail Intelligence | 10 |
| 22 | Drop Strategy & FOMO | 10 |
| 23 | Lifestyle Brand Amplification | 10 |
| 24 | Faith Community Outreach | 10 |
| 25 | Generative Design Innovation | 10 |
| 26 | Wholesale & B2B | 10 |
| 27 | Cross-Platform Media | 10 |
| 28 | Data Science & ML Intelligence | 10 |
| | **Total** | **250** |

## Standard Lifecycle (one drop)

```
1. drop-architect          → drop_brief.yaml
2. youtube-intelligence    → youtube_synthesis.json (Tier 16)
3. reference scrapers      → reference_synthesis.json
4. theology-concept-arch.  → concepts/*.json
5. deepseek-flash pod      → fast concept / copy / scan throughput (Tier 17)
6. aesthetic-director      → art_direction/*.yaml
7. tier 2 specialists      → typography, layout, print, material, silhouette
8. tier 3 prompt engineers → prompts/seedream/*.txt, hero_shots/*.png
9. tier 4 mockups          → mockups/*.png
10. tier 5 video           → promos/*.mp4
11. openclaw/hermes        → multi-step research + refinement (Tier 18)
12. cline execution        → code, integrations, Shopify (Tier 19)
13. tier 7 QA              → qa_reports/*.json
14. quality-gate-keeper    → gate_results.json (PASS / FLAG / KILL)
15. brand-steward          → approval_ledger.json
16. tier 8 copy            → captions, drop story, PDP, microcopy
17. tier 9 distribution    → SKU, pricing, Shopify sync
18. drop-fomo-strategy     → countdown, scarcity, launch coord (Tier 22)
19. tier 10 marketing      → IG, TikTok, email, press
20. cross-platform media   → Substack, podcast, Discord, SMS (Tier 27)
21. data-science pod       → clusters, forecasts, health dashboard (Tier 28)
```

## Gates That Cannot Be Bypassed

- `forbidden_term_count == 0` (Section 1)
- `luxury_score >= 0.82` (Section 5)
- `theology_depth >= 0.75` (Section 5)
- `JSON schema valid` (Section 4)
- `negative_to_positive_ratio >= 0.5`
- `no key leakage in any artifact` (Section 6)

Anything in luxury_score `[0.75, 0.82)` is **flagged for human review**, not auto-killed.

## New Pods (v2.0)

### Tier 16 — YouTube Intelligence
Harvests transcripts from luxury streetwear and Christian culture channels. Synthesizes
style tokens (silhouette, material, color, mood, faith signals) that feed the drop architect.

```bash
make youtube-harvest        # dry-run synthesis
make youtube-harvest-real   # live transcript pull
```

Key agents: `youtube-transcript-harvester`, `youtube-style-synthesizer`, `youtube-culture-decoder`, `youtube-insight-reporter`

### Tier 17 — DeepSeek Flash Research
High-throughput fast-path for concept generation, color theory, theology checking, copy
blasting, and batch ranking. All via `deepseek/deepseek-chat` on OpenRouter.
Override model with `DEEPSEEK_FLASH_MODEL` env var.

Key agents: `deepseek-flash-concept-generator`, `deepseek-flash-batch-ranker`, `deepseek-flash-forbidden-scanner`

### Tier 18 — OpenClaw / Hermes Execution
Multi-step tool-call execution via `nousresearch/hermes-3-llama-3.1-405b` on OpenRouter.
Covers web research, browser automation, RAG retrieval, JSON schema enforcement, and
iterative refinement loops.

Key agents: `openclaw-task-orchestrator`, `hermes-json-schema-enforcer`, `openclaw-browser-agent`, `hermes-refinement-loop`

### Tier 19 — Cline AI Execution
Code generation, API integration building, Shopify theme editing, n8n workflow writing,
and CI/CD pipeline scripting via Cline.

Key agents: `cline-code-executor`, `cline-debug-agent`, `cline-shopify-theme-editor`, `cline-env-validator`

### Tiers 20–28 — Intelligence & Amplification
Market intelligence, demand/retail optimization, drop strategy, lifestyle amplification,
faith community outreach, generative design, wholesale/B2B, cross-platform media, and
data science — 90 agents covering every dimension of the brand's commercial and cultural operations.

## How To Invoke

This registry is framework-agnostic:

- **LangGraph:** each agent is a node; `handoff_to` → edges; gates → conditional edges.
- **CrewAI:** each agent is a `Crew` role; `consumes`/`produces` → task contracts.
- **OpenAI Agents SDK / Anthropic Agents:** `system_prompt` field → system message.
- **Manual / Cursor:** open `REGISTRY.yaml`, copy a `system_prompt`, paste into chat.

## Adding An Agent

1. Append to `REGISTRY.yaml` with the next `FTC-NNN` id (currently at FTC-250).
2. Choose a tier or create a new one (update `tiers:` block + this README's table).
3. Document `consumes`, `produces`, `gates`, `handoff_to`.
4. Write a 2-5 line `system_prompt` — sharp brief, not a tutorial.
5. Open a PR; `brand-steward` reviews.

## Interoperability Pod (Tier 14, v1.3)

17 agents for multi-agent collaboration and cross-model routing: `cline-execution-pilot`,
`openclaw-parallel-orchestrator`, `claude-consensus-lead`, `model-router-federator`,
`handoff-protocol-engineer`, `merge-readiness-auditor`, `alliance-telemetry-auditor`,
`langgraph-flow-compiler`, `crewai-mission-allocator`, `autogen-dialog-conductor`,
`openai-agents-sdk-bridge`, `anthropic-agent-bridge`, `cursor-cloud-executor`,
`branch-isolation-manager`, `prompt-regression-sentinel`, `replay-debug-coordinator`,
`ensemble-verdict-judge`.

## Cinematic Ad Pod (Tier 15, v1.3)

10 agents: `trap-cinema-creative-director`, `teen-hype-culture-calibrator`,
`boohooman-reference-harvester`, `christian-trap-symbolism-editor`,
`product-lineup-shot-planner`, `openrouter-multimodal-router`,
`visual-qwen-shot-generator`, `cinematic-video-prompt-engineer`,
`audio-speech-score-designer`, `ad-performance-rerank-analyst`.

Starter prompt pack: `agents/CINEMATIC_AD_CAMPAIGN_PLAYBOOK.md`.
Routing config: `agents/RUTHLESS_MULTI_LLM_ROUTING.yaml`.
Asset library: `agents/RUTHLESS_AD_ASSET_LIBRARY.md`.

## Cross-Pollination Note

This village was authored scoped to `calebhomwe/skydaze`. To fold in patterns
from your other repos, share the repo name or paste the agent file and it will
be integrated in the next pass.
