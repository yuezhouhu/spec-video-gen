# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Krea Realtime 14B — real-time video generation using a 14B diffusion model distilled from Wan 2.1 via the Self-Forcing technique. This is the **force-reject+random ablation** repo: block 0 always uses the transformer, remaining blocks randomly accept the drafter output at a configurable rate (default 70%). No ImageReward scoring. See `/rscratch/yuezhouhu/realtime-video.target` for target-only and `/rscratch/yuezhouhu/realtime-video.draft` for draft-only.

## Setup

```bash
# Activate virtual environment (uv-managed)
source myenv/bin/activate

# Or reinstall from scratch
uv sync
uv pip install libs/sageattention-2.2.1-cp311-cp311-linux_x86_64.whl  # H100/RTX
```

`MODEL_FOLDER` defaults to `Wan-2.1`. The base model weights and distilled checkpoint must be present:
- `$MODEL_FOLDER/Wan2.1-T2V-14B/` — base Wan 2.1 weights
- `checkpoints/krea-realtime-video-14b.safetensors` — distilled checkpoint

## Running sample_run.py

```bash
# Basic run (200 prompts from MovieGenVideoBench.txt, outputs to outputs/force_reject_random/)
CUDA_VISIBLE_DEVICES=4,5 python sample_run.py

# Custom number of prompts
NUM_PROMPTS=10 CUDA_VISIBLE_DEVICES=4,5 python sample_run.py

# Custom accept rate (default 0.7)
RANDOM_ACCEPT_RATE=0.5 NUM_PROMPTS=200 CUDA_VISIBLE_DEVICES=4,5 python sample_run.py

# With torch.compile (faster inference, ~100s warmup on first video)
DO_COMPILE=true NUM_PROMPTS=10 CUDA_VISIBLE_DEVICES=4,5 python sample_run.py
```

`sample_run.py` hardcodes `output_dir="outputs/force_reject_random"` and uses `configs/self_forcing_server_14b.yaml`. Videos are saved as `outputs/force_reject_random/prompt_NNN.mp4` at 24 fps.

## Key env vars

| Var | Default | Purpose |
|---|---|---|
| `MODEL_FOLDER` | `Wan-2.1` | Path to base model weights |
| `CUDA_VISIBLE_DEVICES` | — | GPU selection (needs 2 GPUs) |
| `DIFFUSION_GPU` | `0` | First visible GPU index for transformer; text encoder/VAE go to `+1` |
| `DO_COMPILE` | `false` | Enable `torch.compile` |
| `NUM_PROMPTS` | `200` | Number of prompts to read from prompt file |
| `PROMPT_FILE` | `MovieGenVideoBench.txt` | Prompt file (one prompt per line) |
| `CONFIG` | `configs/self_forcing_server_14b.yaml` | Active config YAML |
| `RANDOM_ACCEPT_RATE` | `0.7` | Target global accept rate (adjusted internally for force-reject first block) |

## Architecture

### Multi-GPU split
- `DIFFUSION_GPU` (default 0): transformer/diffusion model
- `DIFFUSION_GPU+1`: text encoder (UMT5-XXL) and VAE

### Data flow
1. `sample_run.py` calls `sample_videos()` from `sample.py`
2. Models loaded once via `load_all(config)` from `release_server.py` (transformer + drafter + text encoder + VAE)
3. For each prompt: a `GenerationSession` is created, `generate_block()` called `num_blocks` times (default 9)
4. Block 0: drafter runs, result always rejected, transformer re-generates (force-reject)
5. Blocks 1–8: drafter runs, result randomly accepted/rejected at adjusted rate; if rejected, transformer re-generates
6. All frames concatenated and saved via `save_video_direct()` (torchvision) with ffmpeg pipe fallback

### Key files
| File | Role |
|---|---|
| `sample_run.py` | Entry point: loads prompts, calls `sample_videos()` |
| `sample.py` | `sample_videos()`, `save_video_direct()`, `GenerationSession` loop, routing stats |
| `release_server.py` | `load_all()`, `GenerateParams`, `GenerationSession`, routing decision, `load_merge_config()` |
| `pipeline/causal_inference.py` | Block-by-block inference with KV cache |
| `utils/wan_wrapper.py` | `WanDiffusionWrapper`, `WanTextEncoder` — device placement, checkpoint loading |
| `demo_utils/vae_block3.py` | VAE encode/decode |
| `demo_utils/memory.py` | `DynamicSwapInstaller` — GPU↔CPU memory swapping |
| `configs/self_forcing_server_14b.yaml` | Timestep schedule, guidance scale, KV cache config |
| `settings.py` | `MODEL_FOLDER`, `COMPILE_SHAPES` |

### Configuration
Configs merge at load time: `default_config.yaml` → model-specific YAML via `load_merge_config()`. Key fields: `denoising_step_list`, `num_frame_per_block`, `timestep_shift`, `guidance_scale`, `causal`.
