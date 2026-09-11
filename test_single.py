"""
Test script to evaluate VisionReward on prompt_000.mp4 for both draft_only and target_only.

Prints per-question answers and final scores to help diagnose why draft_only
scores might be unexpectedly high (or identical to target_only).

Usage:
    cd /rscratch/yuezhouhu/VisionReward
    conda activate /rscratch/yuezhouhu/realtime-video/myenv
    CUDA_VISIBLE_DEVICES=7 python test_single.py
"""

import io
import json
import numpy as np
import torch
from decord import cpu, VideoReader, bridge
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── Paths ──────────────────────────────────────────────────────────────
MODEL_PATH = "THUDM/VisionReward-Video"
QUESTIONS_PATH = "VisionReward_Video/VisionReward_video_qa_select.txt"
WEIGHT_PATH = "VisionReward_Video/weight.json"

DRAFT_VIDEO = "/rscratch/yuezhouhu/realtime-video/outputs/draft_only/prompt_000.mp4"
TARGET_VIDEO = "/rscratch/yuezhouhu/realtime-video/outputs/target_only/prompt_000.mp4"

PROMPT = (
    "A stylish woman walks down a Tokyo street filled with warm glowing neon "
    "and animated city signage. She wears a black leather jacket, a long red "
    "dress, and black boots, and carries a black purse. She wears sunglasses "
    "and red lipstick. She walks confidently and casually. The street is damp "
    "and reflective, creating a mirror effect of the colorful lights. Many "
    "pedestrians walk about."
)

# ── Load questions & weights ───────────────────────────────────────────
with open(QUESTIONS_PATH, "r") as f:
    questions = f.readlines()

with open(WEIGHT_PATH, "r") as f:
    weight = np.array(json.load(f))

print(f"Loaded {len(questions)} questions, {len(weight)} weights")
assert len(questions) == len(weight) == 29, "Expected 29 questions and 29 weights"

# ── Device setup ───────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TORCH_TYPE = (
    torch.bfloat16
    if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8
    else torch.float16
)
print(f"Device: {DEVICE}, dtype: {TORCH_TYPE}")

# ── Load model ─────────────────────────────────────────────────────────
print(f"Loading VisionReward model from {MODEL_PATH} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=TORCH_TYPE,
    trust_remote_code=True,
).eval().to(DEVICE)
print("Model loaded.\n")


# ── Video loading (identical to evaluate_batch.py) ─────────────────────
def load_video(video_data, strategy="chat"):
    bridge.set_bridge("torch")
    num_frames = 24
    decord_vr = VideoReader(io.BytesIO(video_data), ctx=cpu(0))
    total_frames = len(decord_vr)

    if strategy == "chat":
        timestamps = decord_vr.get_frame_timestamp(np.arange(total_frames))
        timestamps = [i[0] for i in timestamps]
        max_second = round(max(timestamps)) + 1
        frame_id_list = []
        for second in range(max_second):
            closest_num = min(timestamps, key=lambda x: abs(x - second))
            index = timestamps.index(closest_num)
            frame_id_list.append(index)
            if len(frame_id_list) >= num_frames:
                break
    else:  # base
        frame_id_list = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    video_data_out = decord_vr.get_batch(frame_id_list)
    video_data_out = video_data_out.permute(3, 0, 1, 2)
    return video_data_out, frame_id_list, total_frames


# ── Inference (identical to evaluate_batch.py, with extra diagnostics) ─
def inference(video_path, query, video_tensor):
    """Run VQA inference. Returns (decoded_answer, raw_token_id)."""
    inputs = model.build_conversation_input_ids(
        tokenizer=tokenizer,
        query=query,
        images=[video_tensor],
        history=[],
        template_version="chat",
    )
    inputs = {
        "input_ids": inputs["input_ids"].unsqueeze(0).to(DEVICE),
        "token_type_ids": inputs["token_type_ids"].unsqueeze(0).to(DEVICE),
        "attention_mask": inputs["attention_mask"].unsqueeze(0).to(DEVICE),
        "images": [[inputs["images"][0].to(DEVICE).to(TORCH_TYPE)]],
    }
    gen_kwargs = {
        "max_new_tokens": 2048,
        "pad_token_id": 128002,
        "do_sample": False,
        "top_k": 1,
    }
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        # NOTE: This line uses a single index (not a slice) to get the FIRST
        # generated token at position input_ids_length.  This is intentional —
        # for a yes/no question we only need the first token.
        first_new_token = outputs[:, inputs["input_ids"].shape[1]]

    raw_token_id = first_new_token[0].item()
    decoded = tokenizer.decode(first_new_token[0]).strip().lower()
    return decoded, raw_token_id


# ── Score one video with full diagnostics ──────────────────────────────
def score_video_verbose(video_path, prompt, label):
    print(f"{'=' * 70}")
    print(f"  Evaluating: {label}")
    print(f"  Path: {video_path}")
    print(f"{'=' * 70}")

    video_bytes = open(video_path, "rb").read()
    video_tensor, frame_ids, total_frames = load_video(video_bytes, strategy="chat")

    print(f"  Total frames in file: {total_frames}")
    print(f"  Sampled frame indices: {frame_ids}  ({len(frame_ids)} frames)")
    print(f"  Video tensor shape: {video_tensor.shape}")
    print()

    queries = [q.strip().replace("[[prompt]]", prompt) for q in questions]
    answers = []
    raw_tokens = []

    for i, query in enumerate(queries):
        decoded, token_id = inference(video_path, query, video_tensor)
        is_yes = "yes" in decoded
        answer_val = 1 if is_yes else -1
        answers.append(answer_val)
        raw_tokens.append(decoded)

        w = weight[i]
        contribution = answer_val * w
        flag = ""
        if decoded not in ("yes", "no"):
            flag = " *** UNEXPECTED TOKEN ***"

        print(
            f"  Q{i:02d} | ans={decoded:>6s} (tok={token_id:>6d}) | "
            f"val={answer_val:+d} | w={w:.4f} | contrib={contribution:+.4f}{flag}"
        )

    answers = np.array(answers)
    score = np.mean(answers * weight).item()

    print()
    print(f"  Answers vector:       {answers.tolist()}")
    print(f"  Weighted scores sum:  {np.sum(answers * weight):.6f}")
    print(f"  Weighted scores mean: {score:.6f}")
    print(f"  # yes: {int(np.sum(answers == 1))}, # no: {int(np.sum(answers == -1))}")

    # Check for unexpected tokens
    unexpected = [(i, t) for i, t in enumerate(raw_tokens) if t not in ("yes", "no")]
    if unexpected:
        print(f"\n  WARNING: {len(unexpected)} unexpected token(s):")
        for qi, tok in unexpected:
            print(f"    Q{qi:02d}: '{tok}'")

    print()
    return score, answers, raw_tokens


# ── Main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os

    for path, label in [(DRAFT_VIDEO, "draft_only"), (TARGET_VIDEO, "target_only")]:
        if not os.path.exists(path):
            print(f"ERROR: {path} does not exist, skipping {label}")
            continue

    # Evaluate both videos
    draft_score, draft_answers, draft_tokens = score_video_verbose(
        DRAFT_VIDEO, PROMPT, "DRAFT-ONLY (prompt_000)"
    )
    target_score, target_answers, target_tokens = score_video_verbose(
        TARGET_VIDEO, PROMPT, "TARGET-ONLY (prompt_000)"
    )

    # ── Comparison summary ─────────────────────────────────────────────
    print("=" * 70)
    print("  COMPARISON SUMMARY")
    print("=" * 70)
    print(f"  Draft-only  score: {draft_score:.4f}  (expected: 0.1751)")
    print(f"  Target-only score: {target_score:.4f}  (expected: 0.1751)")
    print(f"  Difference:        {abs(draft_score - target_score):.6f}")
    print()

    # Per-question diff
    diff_indices = [
        i for i in range(len(draft_answers))
        if draft_answers[i] != target_answers[i]
    ]
    if diff_indices:
        print(f"  Questions where answers DIFFER ({len(diff_indices)}):")
        for i in diff_indices:
            print(
                f"    Q{i:02d}: draft={draft_tokens[i]:>6s} vs target={target_tokens[i]:>6s}"
                f"  | weight={weight[i]:.4f}"
            )
    else:
        print("  All 29 answers are IDENTICAL between draft and target.")
        print(
            "  This means the model gives the same yes/no for every question, "
            "so scores must be equal."
        )
        print(
            "  Possible explanations:"
        )
        print(
            "    1. load_video() samples very few frames (check count above) — "
            "both videos look similar at that sampling rate."
        )
        print(
            "    2. VisionReward is not sensitive enough to quality differences "
            "at this resolution / frame count."
        )
        print(
            "    3. The first-token decoding may be collapsing answers "
            "(check for unexpected tokens above)."
        )
    print()
