# sample_run.py
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

# Define prompts
prompts = [
    "A hyperrealistic close-up of ocean waves shimmering at sunset.",
    "A bustling neon-drenched alleyway with rain-soaked pavement.",
]

# Generate videos
sample_videos(
    prompts_list=prompts,
    config_path="configs/self_forcing_server_14b.yaml",
    output_dir="outputs/samples",
    params=params,
    save_videos=True,  # Requires ffmpeg
    fps=24,
)
