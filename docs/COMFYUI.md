# FTC × ComfyUI — cost matrix + recommendation

> Render 1000 designs photoreal for ~$2-3 (RunPod spot) or $0 (own GPU),
> vs ~$40 on Fal.ai. 15-30× cheaper. Uses our SVG silhouettes as
> ControlNet hints for fidelity.

## Cost matrix (1000 renders, Flux.1 Dev, 832×1024, 28 steps)

| Host | GPU | $/image | Total | Setup | Notes |
| :--- | :--- | ---: | ---: | :--- | :--- |
| Your machine | RTX 3090/4090/5090 | **$0** | **$0** | one-time hardware | best long-term ROI; ~25 s/image on a 4090 |
| RunPod spot | RTX 4090 24GB | **~$0.0024** | **~$2.40** | 5 min | recommended hosted path |
| RunPod spot | RTX 3090 24GB | ~$0.0017 | ~$1.70 | 5 min | cheapest acceptable |
| RunPod on-demand | RTX 4090 | ~$0.005 | ~$5 | 5 min | when spot is full |
| Vast.ai spot | RTX 4090 | ~$0.002 | ~$2 | 10 min | comparable, sometimes cheaper |
| Modal serverless | A100 | ~$0.003 | ~$3 | 30 min | nice if you want autoscale |
| ComfyDeploy | managed | ~$0.015 | ~$15 | 0 min | zero ops |
| RunComfy | managed | ~$0.02 | ~$20 | 0 min | zero ops |
| Replicate (ComfyUI image) | managed | ~$0.025 | ~$25 | 0 min | pay-per-second |
| Fal.ai Seedream-4 | managed | ~$0.04 | ~$40 | 0 min | current default in `render_worker.py` |

Costs are mid-2025 rates. Spot is volatile; on-demand is the safe budget.

## Recommended path

**RunPod spot, RTX 4090, Flux.1 Dev FP8, with our SVG silhouettes as
Canny ControlNet hints.** See [`ops/comfyui/runpod_template.md`](../ops/comfyui/runpod_template.md).

Why:
- Cheapest hosted path that runs real Flux Dev (not Schnell).
- ControlNet on our flats means the rendered garment **matches the
  silhouette we already designed**, not a hallucinated one.
- The FP8 build fits in 24 GB with room for the ControlNet model.

## Why not just buy a GPU?

If you'll render hundreds of variants per week (you will), payback on a
used RTX 3090 ($600-800) is ~6 months of RunPod spend. Buy if FTC is
your full-time business; rent if you're still validating.

## Drive it

```bash
# Local
python workers/comfyui_worker.py --limit 5 --dry-run
python workers/comfyui_worker.py --section accessory --limit 50

# Remote (RunPod)
COMFY_URL=https://abc123-8188.proxy.runpod.net \
  python workers/comfyui_worker.py --controlnet --section tracksuit

# Via Makefile
make render-comfy-dry            # plan
make render-comfy                # default
make render-comfy-cn             # with ControlNet from SVG silhouette
```

Renders land in `artifacts/collection_v1/renders/` and the catalog HTML
picks them up — no manual relink.

## What ships with this repo

- [`ops/comfyui/workflow_ftc_flat.json`](../ops/comfyui/workflow_ftc_flat.json) — Flux txt2img workflow tuned for FTC flats
- [`ops/comfyui/workflow_ftc_controlnet.json`](../ops/comfyui/workflow_ftc_controlnet.json) — adds Canny ControlNet on our silhouettes
- [`workers/comfyui_worker.py`](../workers/comfyui_worker.py) — Python driver, idempotent, batched
- [`ops/comfyui/runpod_template.md`](../ops/comfyui/runpod_template.md) — one-page RunPod setup
- [`ops/comfyui/README.md`](../ops/comfyui/README.md) — workflow + models reference

## Quality boosters worth $0

- **Use Flux Schnell first to triage** (4 steps, looks 80% as good). Render
  the whole 1000 in 5 minutes. Pick the top 200, re-render those with
  Flux Dev at 28 steps. Same final budget, much faster iteration.
- **2× upscale** to 1664×2048 with `4x-UltraSharp` or `RealESRGAN_x4plus`
  after Flux. Adds 10 s/image, gives you retina-grade hero shots.
- **LoRA stacking:** add a fashion-editorial LoRA (`flux-fashion-editorial`
  on Civitai) for cinematic lighting on the hero pass.

## When Fal still wins

- You're rendering < 20 images total — Fal's $1 of spend is faster than
  setting up RunPod.
- You want Seedream-4 specifically (it has a different aesthetic to Flux
  that the master context already calls for in some prompts).

`workers/render_worker.py` (Fal) and `workers/comfyui_worker.py` write to
the **same** output directory and are idempotent — use whichever fits the
moment.
