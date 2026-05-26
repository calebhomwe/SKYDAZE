# FTC × ComfyUI

> Two workflows, one worker. Drive ComfyUI from the FTC pipeline to render
> 1000 designs at ~$0.002/image on rented GPUs (or $0 on your own).

## Files

| File | Purpose |
| :--- | :--- |
| `workflow_ftc_flat.json` | Flux.1 Dev FP8 txt2img · 832×1024 (4:5) · the default |
| `workflow_ftc_controlnet.json` | Flux + Canny ControlNet · uses our SVG silhouette as a hint so the rendered garment matches the flat |
| `runpod_template.md` | One-page RunPod template recipe (cheapest hosted path) |
| `../../workers/comfyui_worker.py` | The Python driver that pipes each design through ComfyUI |

## Models you need (download once)

Put these into `ComfyUI/models/`:

```
unet/flux1-dev-fp8.safetensors                       (~12 GB) — Flux UNet, FP8
clip/t5xxl_fp8_e4m3fn.safetensors                    (~5 GB)
clip/clip_l.safetensors                              (~250 MB)
vae/ae.safetensors                                   (~330 MB)
controlnet/flux-canny-controlnet-v3.safetensors      (~3 GB) — only for the CN workflow
```

All available on Hugging Face (search "flux1-dev-fp8" and "flux canny controlnet").

## Drive it

### Local ComfyUI

```bash
# 1. Start ComfyUI (default port 8188)
cd /path/to/ComfyUI && python main.py

# 2. From this repo:
python workers/comfyui_worker.py --section accessory --limit 5 --dry-run   # plan
python workers/comfyui_worker.py --section accessory --limit 5             # go
python workers/comfyui_worker.py --controlnet --limit 20                   # CN mode
```

Renders land in `artifacts/collection_v1/renders/<id>.png` and the catalog
HTML picks them up automatically.

### Remote ComfyUI (RunPod, Vast, etc.)

```bash
COMFY_URL=https://abc123-8188.proxy.runpod.net \
  python workers/comfyui_worker.py --limit 200
```

The worker probes `/system_stats` first; if it can't reach the host it
exits before spending money.

## Two-pass strategy (recommended)

1. **Pass 1 — flat product** (`workflow_ftc_flat.json`)
   - Fast, no ControlNet. Use for the Shopify hero image.
2. **Pass 2 — on-model editorial**
   - Modify the prompt to insert "on a 6'1" model, north-window light,
     three-quarter view". Same workflow.

The render worker batches whatever's in `artifacts/collection_v1/concepts/`
that doesn't have a render yet, so you can mix passes freely — re-runs
are idempotent.

## Cost notes

See `../../docs/COMFYUI.md` for the full cost-vs-quality matrix. TL;DR:
spot RunPod 4090 → ~$2-3 to render the full 1000. Local on your own GPU
→ free.

## Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| `[error] ComfyUI unreachable` | Check `COMFY_URL`. RunPod URLs include the pod id and port. |
| `cairosvg not installed; skipping ControlNet hint` | `pip install cairosvg`. Or skip `--controlnet`. |
| Slow renders | Drop steps to 20, or switch to `flux1-schnell` (4 steps). Edit `workflow_ftc_flat.json` → `unet_name`. |
| OOM | Use FP8 weights (default in our workflow). Or smaller resolution. |
| Output looks generic | Use `--controlnet`. SVG silhouette locks the garment shape. |
