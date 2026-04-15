OUTPUT_DIR=outputs/reward_dynamic NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=2,3 nohup python -u sample_run.py > logs/dynamic.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed OUTPUT_DIR=outputs/reward_fixed NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=4,5 nohup python -u sample_run.py > logs/fixed.log 2>&1 &
