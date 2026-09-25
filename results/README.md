# Per-prompt evaluation record

`per_prompt.csv` holds one row per (configuration, prompt): 35 configurations
× 1003 MovieGenVideoBench prompts. It is the raw material behind every table
and figure in the paper, collected by `../collect_per_prompt.py`.

## Columns

| column | meaning |
|---|---|
| `config` | run name exactly as it appears in the generation logs |
| `prompt` | 0-based prompt id, matching the `id` field of the score JSONs |
| `vr` | VisionReward of the final video |
| `time_s` | wall-clock seconds to generate that video |
| `s1`…`s8` | min-frame ImageReward of blocks 1–8 |
| `b1`…`b8` | 1 if the block's draft was accepted, 0 if the target regenerated it |

Block 0 is always force-rejected and is never scored, so it has no column.

## Where the numbers come from

- Generation logs (`Block N: … accept=…`, `Sampling took`, `Video saved to`):
  - `/rscratch/yuezhouhu/realtime-video/logs/<config>.log` — the SDVG runs
  - `/rscratch/yuezhouhu/realtime-video.hybrid/logs/eval_<config>.log` — the hybrid runs
- VisionReward scores: `scores/` in this directory holds those files verbatim
  (`{id, video, score}` per prompt), copied from the two evaluation trees.

Both log families were produced by the same server, so one parser covers them.
Regenerate everything with `python3 collect_per_prompt.py` on a machine that
can read `/rscratch/yuezhouhu/`.

## Caveats worth knowing before reusing this

- **Single seed.** Every run used random seed 42, fixed in the benchmark
  client. There are no repeated-seed runs, so per-prompt differences between
  configurations mix configuration effects with run-to-run stochasticity.
- **No human study.** Quality is measured by VisionReward, a reward model
  trained on human preferences, plus the automatic EvalCrafter metrics. No new
  human-preference evaluation was collected for this paper.
- **Timings are wall-clock on shared machines.** Cross-machine deviation was
  measured at ≤1.3% on matched prompt/config pairs, but per-prompt timing noise
  is larger than the configuration differences at close thresholds; the paper
  reports means over 1003 prompts for this reason.
