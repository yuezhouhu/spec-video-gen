#!/bin/bash
# Wait for target_only generation to finish, then run VisionReward eval

TARGET_PID=$1
echo "Monitoring target_only generation PID=$TARGET_PID (from monitor script)"

# Wait for all sample_run.py processes to finish (the one on GPU 2,3)
while true; do
    TARGET_COUNT=$(ls outputs/target_only/prompt_*.mp4 2>/dev/null | wc -l)
    echo "$(date): target_only has $TARGET_COUNT/200 videos"
    if [ "$TARGET_COUNT" -ge 200 ]; then
        echo "$(date): target_only generation complete!"
        break
    fi
    sleep 60
done

# Wait a bit for process cleanup
sleep 10

echo "$(date): Starting VisionReward evaluation for target_only..."
cd /rscratch/yuezhouhu/VisionReward
VIDEO_DIR=/rscratch/yuezhouhu/realtime-video/outputs/target_only \
    NUM_PROMPTS=200 \
    EVAL_OUTPUT=eval_target_only_200.json \
    CUDA_VISIBLE_DEVICES=4 \
    /rscratch/yuezhouhu/realtime-video/myenv/bin/python -u evaluate_batch.py

echo "$(date): target_only evaluation complete!"
