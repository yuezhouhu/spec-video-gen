# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VisionReward is a fine-grained, multi-dimensional reward model for evaluating human preferences in images and videos. It uses CogVLM2-based models (Llama3 backbone) to answer 58–64 yes/no questions per input, then combines answers with learned linear weights to produce a scalar reward score.

## Common Commands

### Image Inference
```bash
# Score an image (requires --model_path)
python inference-image.py --score --image_path asset/test/test1.jpg --prompt "your prompt" --model_path /path/to/model

# Answer a specific VQA question
python inference-image.py --question "Is the image sharp?" --image_path asset/test/test1.jpg --model_path /path/to/model
```

### Video Inference
```bash
# Score a video
python inference-video.py --score --video_path asset/test/test.mp4 --prompt "your prompt" --model_path /path/to/model

# Compare two videos
python inference-video.py --compare --video_path asset/test/test1.mp4 --video_path2 asset/test/test2.mp4 --prompt "your prompt" --model_path /path/to/model

# Answer a specific question about a video
python inference-video.py --question "Is the video smooth?" --video_path asset/test/test.mp4 --model_path /path/to/model
```

### Batch Evaluation
```bash
python evaluate_batch.py  # Evaluates 38 videos, outputs batch_evaluation_results.json
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Scoring Pipeline

```
Input (Image/Video)
  → Frame Extraction (PIL for images; Decord extracts 24 frames for video)
  → Vision Encoder: EVA2 ViT (utils/models/eva_clip_model.py)
  → Language Model: CogVLM2/Llama3 (utils/models/cogvlm2_model.py)
  → Multi-dimensional QA: 58 questions (image) / 63 questions (video)
      Each returns yes/no token probabilities → converted to [-1, +1]
  → [Image only] VQAScore: CLIP-FlanT5 alignment score (VisionReward_Image/t2v_metrics/)
  → Linear combination: score = dot(answers, weights) + intercept
      Weights loaded from VisionReward_{Image,Video}/weight.json
      [Image] Masking applied when body/face/hands not detected
```

### Key Files

| File | Role |
|------|------|
| `inference-image.py` | Image scoring entry point; `cal_score()` implements the full pipeline |
| `inference-video.py` | Video scoring/comparison entry point; `score()` and `compare_two_videos()` |
| `evaluate_batch.py` | Batch evaluation over a list of videos |
| `utils/models/cogvlm2_model.py` | `VisualLlamaEVA` — main VLM with EVA2 image encoder + Llama3 decoder |
| `utils/utils/chat.py` | `chat()`, `chat_batch()`, `chat_prob_batch()` — core generation and token-prob extraction |
| `utils/utils/language.py` | Tokenizers (llama2/llama3), prompt-history converters for base/chat/vqa modes |
| `VisionReward_Image/t2v_metrics/vqascore.py` | CLIP-FlanT5 VQAScore for image-text alignment |
| `VisionReward_Image/weight.json` | 58 learned coefficients + intercept for image scoring |
| `VisionReward_Video/weight.json` | 29 learned weights for video scoring |
| `VisionReward_Image/VisionReward_image_qa.txt` | 58 yes/no questions for image assessment |
| `VisionReward_Video/VisionReward_video_qa.txt` | 63 yes/no questions for video assessment |

### Model Architecture

- **Mixin-based design** using SwissArmyTransformer (SAT): `VisualLlamaEVA` composes `ImageMixin` (EVA2 ViT encoder + GLU projection) with `CachedAutoregressiveMixin` for efficient decoding.
- **Token probability extraction**: For yes/no QA, `chat_prob_batch()` extracts logits for the "Yes"/"No" tokens directly, avoiding full autoregressive generation.
- **Masking logic** (image only): Dimensions related to body, face, or hands are zeroed when those elements are absent, preventing spurious signals.

### Module Layout

- `VisionReward_Image/` — Image-specific question set, weights, and `t2v_metrics/` (VQAScore, CLIPScore, ITMScore with BLIP/BLIP2/LLaVA backends)
- `VisionReward_Video/` — Video-specific question set and weights (model itself comes from `transformers` CogVLM2-Video)
- `utils/models/` — Model class definitions (CogVLM2, EVA-CLIP, base CogVLM)
- `utils/utils/` — Inference helpers: `chat.py`, `language.py` (tokenization), `vision.py` (image preprocessing), `dataset.py`, `template.py`
- `asset/test/` — Sample inputs: `test1.jpg`, `test2.jpg`, `test.mp4`, `test1.mp4`, `test2.mp4`
