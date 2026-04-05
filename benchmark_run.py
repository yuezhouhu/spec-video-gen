# benchmark_run.py — timed run with 10 prompts for speed measurement
import os
import time
from release_server import GenerateParams
from sample import sample_videos

params = GenerateParams(
    prompt="",
    width=832,
    height=480,
    num_blocks=9,
    seed=42,
    kv_cache_num_frames=3,
)

prompts = [
    "A stylish woman walks down a Tokyo street filled with warm glowing neon and animated city signage. She wears a black leather jacket, a long red dress, and black boots, and carries a black purse. She wears sunglasses and red lipstick. She walks confidently and casually. The street is damp and reflective, creating a mirror effect of the colorful lights. Many pedestrians walk about.",
    "Several giant wooly mammoths approach treading through a snowy meadow, their long wooly fur lightly blows in the wind as they walk, snow covered trees and dramatic snow capped mountains in the distance, mid afternoon light with wispy clouds and a sun high in the distance creates a warm glow, the low camera view is stunning capturing the large furry mammal with beautiful photography, depth of field.",
    "A movie trailer featuring the adventures of the 30 year old space man wearing a red wool knitted motorcycle helmet, blue sky, salt desert, cinematic style, shot on 35mm film, vivid colors.",
    "Drone view of waves crashing against the rugged cliffs along Big Sur's garay point beach. The crashing blue waters create white-tipped waves, while the golden light of the setting sun illuminates the rocky shore. A small island with a lighthouse sits in the distance, and green shrubbery covers the cliff's edge.",
    "Animated scene features a close-up of a short fluffy monster kneeling beside a melting red candle. The art style is 3D and realistic, with a focus on lighting and texture.",
    "A gorgeously rendered papercraft world of a coral reef, rife with colorful fish and sea creatures.",
    "This close-up shot of a Victoria crowned pigeon showcases its striking blue plumage and red chest. Its crest is made of delicate, lacy feathers, while its eye is a striking red color.",
    "Photorealistic closeup video of two pirate ships battling each other as they sail inside a cup of coffee.",
    "A young man at his 20s is sitting on a piece of cloud in the sky, reading a book.",
    "Historical footage of California during the gold rush.",
]

output_dir = os.getenv("OUTPUT_DIR", "outputs/benchmark")

start = time.time()
sample_videos(
    prompts_list=prompts,
    config_path="configs/self_forcing_server_14b.yaml",
    output_dir=output_dir,
    params=params,
    save_videos=True,
    fps=24,
)
total = time.time() - start
print(f"\n{'='*60}")
print(f"BENCHMARK: {len(prompts)} videos in {total:.1f}s, avg {total/len(prompts):.2f}s/video")
print(f"{'='*60}")
