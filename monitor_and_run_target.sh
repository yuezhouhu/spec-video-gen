#!/bin/bash
# Monitor draft_only completion and auto-start target_only on same GPUs

DRAFT_PID=$1
echo "Monitoring draft_only PID=$DRAFT_PID"

# Wait for draft_only to finish
while kill -0 $DRAFT_PID 2>/dev/null; do
    DRAFT_COUNT=$(ls outputs/draft_only/prompt_1*.mp4 2>/dev/null | wc -l)
    echo "$(date): draft_only has $DRAFT_COUNT/100 new videos, still running..."
    sleep 60
done

echo "$(date): draft_only finished!"
DRAFT_TOTAL=$(ls outputs/draft_only/prompt_*.mp4 2>/dev/null | wc -l)
echo "Draft-only total videos: $DRAFT_TOTAL"

# Now start target_only on the same GPUs (2,3)
echo "$(date): Starting target_only on GPU 2,3..."
ROUTING_MODE=target_only OUTPUT_DIR=outputs/target_only NUM_PROMPTS=200 CUDA_VISIBLE_DEVICES=2,3 \
    /rscratch/yuezhouhu/realtime-video/myenv/bin/python -u sample_run.py 2>&1 | tee logs/target_only_200.log

echo "$(date): target_only finished!"
TARGET_TOTAL=$(ls outputs/target_only/prompt_*.mp4 2>/dev/null | wc -l)
echo "Target-only total videos: $TARGET_TOTAL"
