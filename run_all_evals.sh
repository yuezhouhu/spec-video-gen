#!/bin/bash
# Run VisionReward evaluation for all three modes with 200 prompts
# Requires all generation to be complete first
# Uses a single GPU for evaluation

cd /rscratch/yuezhouhu/realtime-video

echo "=== Checking video counts ==="
echo "Draft-only: $(ls outputs/draft_only/prompt_*.mp4 2>/dev/null | wc -l) videos"
echo "Reward: $(ls outputs/reward_v2/prompt_*.mp4 2>/dev/null | wc -l) videos"
echo "Target-only: $(ls outputs/target_only/prompt_*.mp4 2>/dev/null | wc -l) videos"

cd /rscratch/yuezhouhu/VisionReward

echo ""
echo "=== Evaluating Draft-only ==="
VIDEO_DIR=/rscratch/yuezhouhu/realtime-video/outputs/draft_only \
    NUM_PROMPTS=200 \
    EVAL_OUTPUT=eval_draft_only_200.json \
    CUDA_VISIBLE_DEVICES=${1:-6} \
    /rscratch/yuezhouhu/realtime-video/myenv/bin/python evaluate_batch.py

echo ""
echo "=== Evaluating Reward v2 ==="
VIDEO_DIR=/rscratch/yuezhouhu/realtime-video/outputs/reward_v2 \
    NUM_PROMPTS=200 \
    EVAL_OUTPUT=eval_reward_200.json \
    CUDA_VISIBLE_DEVICES=${1:-6} \
    /rscratch/yuezhouhu/realtime-video/myenv/bin/python evaluate_batch.py

echo ""
echo "=== Evaluating Target-only ==="
VIDEO_DIR=/rscratch/yuezhouhu/realtime-video/outputs/target_only \
    NUM_PROMPTS=200 \
    EVAL_OUTPUT=eval_target_only_200.json \
    CUDA_VISIBLE_DEVICES=${1:-6} \
    /rscratch/yuezhouhu/realtime-video/myenv/bin/python evaluate_batch.py

echo ""
echo "=== All evaluations complete ==="
