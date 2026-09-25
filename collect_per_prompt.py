"""Collect the per-prompt evaluation record for every configuration in the paper.

Usage: python3 collect_per_prompt.py
Writes: results/per_prompt.csv  and  results/scores/*.json

Sources (cluster paths, not needed to read the CSV):

  generation logs   /rscratch/yuezhouhu/realtime-video/logs/<config>.log
                    /rscratch/yuezhouhu/realtime-video.hybrid/logs/eval_<config>.log
  VisionReward      /rscratch/yuezhouhu/VisionReward/eval_<config>_1003.json
                    /rscratch/yuezhouhu/realtime-video.hybrid/evals/eval_<config>_1003.json

Each log records, per prompt, every scored block's min-frame ImageReward and
the accept/reject decision, then the video's wall-clock time:

    INFO:release_server:Block 3: ImageReward avg=... min=1.9067 score(min)=... accept=True
    Sampling took 47.20s
    OK Video saved to outputs/<config>/prompt_000.mp4

Columns of per_prompt.csv:
    config   run name as it appears in the logs
    prompt   0-based prompt id, matching the "id" field of the score JSONs
    vr       VisionReward of the final video
    time_s   wall-clock seconds for that video
    s1..s8   min-frame ImageReward of blocks 1..8 (block 0 is force-rejected,
             so it is never scored)
    b1..b8   1 if the block was accepted, 0 if it was regenerated

All runs use the single random seed 42 and no human-preference study was run;
quality comes from VisionReward, a reward model trained on human preferences.
"""
import csv
import json
import os
import re
import shutil

REPO = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REPO, "results")

RUNS = []
for log_dir, eval_dir in [
    ("/rscratch/yuezhouhu/realtime-video/logs",
     "/rscratch/yuezhouhu/VisionReward"),
    ("/rscratch/yuezhouhu/realtime-video.hybrid/logs",
     "/rscratch/yuezhouhu/realtime-video.hybrid/evals"),
]:
    for fn in sorted(os.listdir(log_dir)):
        if not fn.endswith(".log") or fn == "cascade_calib.log":
            continue
        name = fn[:-4]
        for candidate in (f"eval_{name}_1003.json", f"{name}_1003.json"):
            path = os.path.join(eval_dir, candidate)
            if os.path.exists(path):
                RUNS.append((name, os.path.join(log_dir, fn), path))
                break

BLOCK = re.compile(r'Block ([1-8]): ImageReward .*?score\((?:min|avg)\)=([-\d.]+).*?accept=(True|False)')
SAVED = re.compile(r'Video saved to .*?/prompt_(\d+)\.mp4')
TOOK = re.compile(r'Sampling took ([\d.]+)s')


def parse_log(path):
    """Yield (prompt_id, time_s, scores, accepts) in the order the videos were saved."""
    pending_time, scores, accepts = None, {}, {}
    for line in open(path, errors="ignore"):
        m = BLOCK.search(line)
        if m:
            b = int(m.group(1))
            scores[b], accepts[b] = float(m.group(2)), m.group(3) == "True"
            continue
        m = TOOK.search(line)
        if m:
            pending_time = float(m.group(1))
            continue
        m = SAVED.search(line)
        if m:
            yield int(m.group(1)), pending_time, scores, accepts
            pending_time, scores, accepts = None, {}, {}


def main():
    os.makedirs(os.path.join(OUT, "scores"), exist_ok=True)
    rows = []
    for name, log_path, eval_path in RUNS:
        vr = {e["id"]: e["score"] for e in json.load(open(eval_path))}
        shutil.copyfile(eval_path, os.path.join(OUT, "scores", os.path.basename(eval_path)))
        run = []
        for pid, t, scores, accepts in parse_log(log_path):
            run.append({
                "config": name, "prompt": pid, "vr": f"{vr.get(pid, float('nan')):.6f}",
                "time_s": t,
                **{f"s{b}": scores.get(b) for b in range(1, 9)},
                **{f"b{b}": int(accepts.get(b, False)) for b in range(1, 9)},
            })
        if not run:
            # some logs under logs/ belong to the eval side only
            print(f"{name:34s} skipped (no generation records)")
            continue
        rows.extend(run)
        print(f"{name:34s} {len(run):5d} prompts")

    cols = ["config", "prompt", "vr", "time_s"] + [f"s{b}" for b in range(1, 9)] + [f"b{b}" for b in range(1, 9)]
    with open(os.path.join(OUT, "per_prompt.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} rows -> results/per_prompt.csv")


if __name__ == "__main__":
    main()
