# RunPod recipe — cheapest ComfyUI for FTC

Total spend to render all 1000 designs: **~$2-3** on a spot RTX 4090.

## 1. Pod

| Setting | Value |
| :--- | :--- |
| GPU | RTX 4090 24GB (or RTX 5090 / 3090 24GB) |
| Pod type | **Spot** (cheapest; 50-70% off on-demand) |
| Region | EU-RO-1 or US-OR-1 (usually cheapest) |
| Container | `runpod/pytorch:2.4.0-py3.11-cuda12.4-devel-ubuntu22.04` |
| Container disk | 30 GB |
| Volume disk | 60 GB (Flux models are big) |
| Expose port | 8188 (ComfyUI) |
| Start command | (paste the script below) |

## 2. Start command (paste into "Container Start Command")

```bash
bash -c '
set -e
apt-get update && apt-get install -y git wget curl
cd /workspace
[ -d ComfyUI ] || git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
mkdir -p models/unet models/clip models/vae models/controlnet
cd models/unet
[ -f flux1-dev-fp8.safetensors ] || wget -q https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors
cd ../clip
[ -f t5xxl_fp8_e4m3fn.safetensors ] || wget -q https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors
[ -f clip_l.safetensors ] || wget -q https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors
cd ../vae
[ -f ae.safetensors ] || wget -q https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
'
```

First boot downloads the models (~17 GB). Boot 2 onward starts in 30 seconds.

## 3. Connect from your laptop

RunPod gives you a proxy URL like `https://<podid>-8188.proxy.runpod.net`.

```bash
# from this repo
export COMFY_URL=https://<podid>-8188.proxy.runpod.net
python workers/comfyui_worker.py --limit 5 --dry-run
python workers/comfyui_worker.py --section tracksuit --limit 50
```

## 4. Cost math (RTX 4090 spot)

| Item | Rate | Notes |
| :--- | ---: | :--- |
| GPU rental | ~$0.34/hr | spot price; varies by region |
| Render time | ~25 s / image | Flux Dev FP8, 28 steps, 832×1024 |
| **Per-image** | **~$0.0024** | 25s × $0.34/hr |
| **Per 1000** | **~$2.40** | + ~$0.30 model-download minutes once |

Cheaper still:
- RTX 3090 24GB spot: ~$0.21/hr → ~$1.50 / 1000
- Use Flux **Schnell** (4 steps instead of 28) → 5× faster, ~$0.50 / 1000

## 5. Don't forget

- **Stop the pod** when done. Spot pods that idle still bill you.
- Renders save to your laptop via the worker — they do NOT persist on the
  pod's ephemeral disk. (Volume disk persists; container disk doesn't.)
- If you'll re-render often, snapshot the model directory to a Network
  Volume to skip the download next time.
