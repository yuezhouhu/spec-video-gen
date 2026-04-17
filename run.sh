OUTPUT_DIR=outputs/reward_dynamic NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=2,3 nohup python -u sample_run.py > logs/dynamic.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed OUTPUT_DIR=outputs/reward_fixed NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=4,5 nohup python -u sample_run.py > logs/fixed.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed REWARD_FIXED_THRESHOLD=-2.5 OUTPUT_DIR=outputs/reward_fixed_-2.5 NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=0,4 nohup python -u sample_run.py > logs/fixed_-2.5.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed REWARD_FIXED_THRESHOLD=-0.5 OUTPUT_DIR=outputs/reward_fixed_-0.5 NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=0,3 nohup python -u sample_run.py > logs/fixed_-0.5.log 2>&1 &

OUTPUT_DIR=outputs/reward_dynamic_avg NUM_PROMPTS=1003 REWARD_SCORE_MODE=avg CUDA_VISIBLE_DEVICES=1,3 nohup python -u sample_run.py > logs/dynamic_avg.log 2>&1 &

REWARD_THRESHOLD_MODE=fixed REWARD_FIXED_THRESHOLD=-0.5 REWARD_SCORE_MODE=avg OUTPUT_DIR=outputs/reward_fixed_-0.5_avg NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=4,5 nohup python -u sample_run.py > logs/fixed_-0.5_avg.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed REWARD_FIXED_THRESHOLD=-0.2 REWARD_SCORE_MODE=avg OUTPUT_DIR=outputs/reward_fixed_-0.2_avg NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=6,7 nohup python -u sample_run.py > logs/fixed_-0.2_avg.log 2>&1 &
REWARD_THRESHOLD_MODE=fixed REWARD_FIXED_THRESHOLD=-0.7 REWARD_SCORE_MODE=avg OUTPUT_DIR=outputs/reward_fixed_-0.7_avg NUM_PROMPTS=1003 CUDA_VISIBLE_DEVICES=4,5 nohup python -u sample_run.py > logs/fixed_-0.7_avg.log 2>&1 &
