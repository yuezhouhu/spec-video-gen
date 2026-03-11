# AGENTS.md - Developer Guide for Realtime Video Generation

## Project Overview

This is a **Krea Realtime 14B** video generation project - a real-time video diffusion model distilled from Wan 2.1 using Self-Forcing technique. The project uses Python 3.11+ with PyTorch for deep learning inference.

---

## Build, Lint, and Test Commands

### Setup and Dependencies
```bash
# Install all dependencies
uv sync

# Install attention backend (choose one):
# For NVIDIA B200 GPUs:
uv pip install flash_attn --no-build-isolation

# For H100/RTX 5xxx:
uv pip install libs/sageattention-2.2.1-cp311-cp311-linux_x86_64.whl
# Or: bash install_sage.sh
```

### Running the Server
```bash
# Real-time WebSocket server
export MODEL_FOLDER=wan_models
export CONFIG=configs/self_forcing_server_14b.yaml
export CUDA_VISIBLE_DEVICES=0
export DO_COMPILE=true
uvicorn release_server:app --host 0.0.0.0 --port 8000
```

### Running Offline Sampling
```bash
# Run sample script
python sample_run.py

# Or with custom settings
CUDA_VISIBLE_DEVICES=0 python sample.py
```

### Running Tests
There is no formal test framework. Manual test scripts exist:
```bash
# WebSocket client test
python test_client.py

# Socket.IO request test
python test_request.py --type start|update|stop
```

### Linting and Type Checking
```bash
# Run ruff linter
ruff check .

# Run pyright (type checking is disabled in config)
pyright
```

---

## Code Style Guidelines

### General Principles
- **Python Version**: 3.11+ (requires Python >=3.11, <3.12)
- Use **type hints** for function signatures and class attributes
- Keep inference code in `torch.no_grad()` or use `torch.set_grad_enabled(False)`
- Use `pydantic.BaseModel` for data validation (e.g., `GenerateParams`)

### Import Organization
Order imports as follows (per file):
1. Standard library imports (`asyncio`, `os`, `time`, etc.)
2. Third-party imports (`torch`, `fastapi`, `pydantic`, etc.)
3. Internal project imports (`from pipeline import ...`, `from utils import ...`)

```python
# Example import order
import asyncio
import logging
from typing import Optional, Dict, List

import torch
import numpy as np
from fastapi import FastAPI, WebSocket

from pipeline import CausalInferencePipeline
from utils.wan_wrapper import WanTextEncoder
from settings import MODEL_FOLDER
```

### Naming Conventions
- **Classes**: CamelCase (e.g., `WanTextEncoder`, `GenerateParams`, `ResidualBlock`)
- **Functions/methods**: snake_case (e.g., `load_merge_config`, `save_video_direct`)
- **Variables**: snake_case (e.g., `image_bytes`, `save_videos`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `CACHE_T`, `UUID_NIL`)
- **Private methods**: prefix with underscore (e.g., `_load_state_dict_auto`)

### Type Annotations
Use type hints consistently:
```python
def sample_videos(
    prompts_list: List[str],
    config_path: str | Path,
    output_dir: Path,
    params: GenerateParams,
    save_videos: bool = True,
    fps: int = 30,
) -> Optional[List[Path]]:
```

### Docstrings
Use simple docstrings for functions and classes:
```python
def resample_array(array, target_length):
    """Resample a list to the target length using linear interpolation of indices"""
    ...
```

### Error Handling
- Use try/except with specific exceptions
- Provide fallback patterns where appropriate
- Log errors with appropriate levels
```python
try:
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    process.stdin.write(video_np.tobytes())
    process.stdin.close()
    process.wait()
except Exception as e:
    print(f"Error creating video: {e}")
    return None
```

### Configuration
- Use `omegaconf.OmegaConf` for YAML config handling
- Use `pydantic.BaseModel` for API request/response validation
- Use environment variables via `python-dotenv` for runtime settings

```python
# Config loading
from omegaconf import OmegaConf

def load_merge_config(config_path: str | Path) -> OmegaConf:
    config = OmegaConf.load(config_path)
    default_config = OmegaConf.load("configs/default_config.yaml")
    return OmegaConf.merge(default_config, config)
```

### Logging
Use Python's logging module with appropriate levels:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)
```

### PyTorch Patterns
- Disable gradients for inference: `torch.set_grad_enabled(False)`
- Use `torch.compile()` for performance when `DO_COMPILE=true`
- Use `bfloat16` for model weights when possible
- Use `.eval()` and `.requires_grad_(False)` for inference models

### File Structure to Follow
```
realtime-video/
├── configs/           # YAML configuration files
├── demo_utils/        # VAE and utility functions
├── model/             # Model implementations
├── pipeline/          # Inference pipelines
├── utils/             # Helper utilities
├── wan/               # Wan model components
├── release_server.py  # WebSocket server (main entry)
├── sample.py          # Offline sampling
├── v2v.py             # Video-to-video utilities
├── settings.py        # Settings (environment variables)
└── pyproject.toml     # Project configuration
```

### Common Environment Variables
- `MODEL_FOLDER`: Path to model checkpoints (default: "Wan-2.1")
- `CONFIG`: Path to config YAML
- `CUDA_VISIBLE_DEVICES`: GPU device selection
- `DO_COMPILE`: Enable torch.compile (default: false)
- `USE_STATIC_ENCODER_COND_DICT`: Use static embeddings (dev only)
- `DIFFUSION_GPU`: GPU index for diffusion model (default: 0). Text encoder and VAE will be placed on DIFFUSION_GPU+1

### Multi-GPU Support
The code supports running on two GPUs:
- GPU 0 (DIFFUSION_GPU): Diffusion/transformer model
- GPU 1 (DIFFUSION_GPU+1): Text encoder and VAE

Example with specific GPUs:
```bash
# Use GPUs 6 and 7
CUDA_VISIBLE_DEVICES=6,7 python sample_run.py

# Or with DIFFUSION_GPU explicitly set
DIFFUSION_GPU=6 CUDA_VISIBLE_DEVICES=6,7 python sample_run.py
```

### Key Dependencies
- `torch` - Deep learning framework
- `fastapi` - Web framework
- `pydantic` - Data validation
- `omegaconf` - Config management
- `safetensors` - Model loading
- `transformers` - Hugging Face transformers
- `diffusers` - Diffusion models
- `PIL` / `Pillow` - Image processing
- `numpy` - Numerical computing
- `msgpack` - Binary serialization for WebSocket

---

## Important Notes for Agents

1. **No Formal Tests**: This project lacks automated tests. Test changes manually using `test_client.py` or `test_request.py`.

2. **Type Checking Disabled**: `pyrightconfig.json` has `typeCheckingMode: "off"`. Adding type hints is encouraged but won't be enforced.

3. **GPU Required**: Most code requires CUDA-enabled GPU. CPU-only testing is not supported.

4. **Model Checkpoints Required**: Running code requires downloading model weights from HuggingFace (see README.md).

5. **Large Dependencies**: This project has many heavy dependencies (torch, transformers, etc.). Use virtual environments (`.venv` or `myenv`).

6. **Mutable Global State**: Be careful with global variables like `session_frames_storage`, `DO_COMPILE` in `release_server.py`.