# sample_run.py
import os
from pathlib import Path
from release_server import GenerateParams
from sample import sample_videos

# Configure generation parameters
params = GenerateParams(
    prompt="",  # Will be overwritten per prompt
    width=832,
    height=480,
    num_blocks=9,
    seed=42,
    kv_cache_num_frames=3,
)

# Load prompts from file
PROMPT_FILE = os.getenv("PROMPT_FILE", "MovieGenVideoBench.txt")
NUM_PROMPTS = int(os.getenv("NUM_PROMPTS", "100"))
with open(PROMPT_FILE, "r") as f:
    prompts = [line.strip() for line in f if line.strip()][:NUM_PROMPTS]
print(f"Loaded {len(prompts)} prompts from {PROMPT_FILE}")

# Generate videos
sample_videos(
    prompts_list=prompts,
    config_path="configs/self_forcing_server_14b.yaml",
    output_dir=os.getenv("OUTPUT_DIR", "outputs/samples"),
    params=params,
    save_videos=True,  # Requires ffmpeg
    fps=24,
)
