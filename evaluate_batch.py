import io
import os
import json
import numpy as np
import torch
from decord import cpu, VideoReader, bridge
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# 配置路径
MODEL_PATH = "THUDM/VisionReward-Video"
QUESTIONS_PATH = "VisionReward_Video/VisionReward_video_qa_select.txt"
WEIGHT_PATH = "VisionReward_Video/weight.json"
VIDEO_DIR = os.getenv("VIDEO_DIR", "/rscratch/yuezhouhu/realtime-video/outputs/samples")

# Load prompts from file
PROMPT_FILE = os.getenv("PROMPT_FILE", "/rscratch/yuezhouhu/realtime-video/MovieGenVideoBench.txt")
NUM_PROMPTS = int(os.getenv("NUM_PROMPTS", "100"))
with open(PROMPT_FILE, "r") as f:
    prompts = [line.strip() for line in f if line.strip()][:NUM_PROMPTS]
print(f"Loaded {len(prompts)} prompts from {PROMPT_FILE}")

# 加载元数据
with open(QUESTIONS_PATH, 'r') as f:
    questions = f.readlines()

with open(WEIGHT_PATH, 'r') as f:
    weight = np.array(json.load(f))

# 设备配置
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16

print(f"Loading model to {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=TORCH_TYPE,
    trust_remote_code=True
).eval().to(DEVICE)

def load_video(video_data, strategy='chat'):
    bridge.set_bridge('torch')
    num_frames = 24
    decord_vr = VideoReader(io.BytesIO(video_data), ctx=cpu(0))
    total_frames = len(decord_vr)
    
    if strategy == 'chat':
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
    else: # base
        frame_id_list = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
    video_data = decord_vr.get_batch(frame_id_list)
    video_data = video_data.permute(3, 0, 1, 2)
    return video_data

def inference(video_path, query):
    video_bytes = open(video_path, 'rb').read()              
    video = load_video(video_bytes, strategy='chat')
    
    inputs = model.build_conversation_input_ids(
        tokenizer=tokenizer,
        query=query,
        images=[video],
        history=[],
        template_version='chat'
    )
    inputs = {
        'input_ids': inputs['input_ids'].unsqueeze(0).to(DEVICE),
        'token_type_ids': inputs['token_type_ids'].unsqueeze(0).to(DEVICE),
        'attention_mask': inputs['attention_mask'].unsqueeze(0).to(DEVICE),
        'images': [[inputs['images'][0].to(DEVICE).to(TORCH_TYPE)]],
    }
    gen_kwargs = {
        "max_new_tokens": 2048,
        "pad_token_id": 128002,
        "do_sample": False,
        "top_k": 1,
    }
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]]
    
    return tokenizer.decode(outputs[0]).strip().lower()

def score_video(video_path, prompt):
    queries = [q.strip().replace('[[prompt]]', prompt) for q in questions]
    answers = []
    # 内部使用 tqdm 显示单个视频的 VQA 进度
    for query in tqdm(queries, desc=f"Evaluating {os.path.basename(video_path)}", leave=False):
        ans = inference(video_path, query)
        answers.append(1 if 'yes' in ans else -1)
    
    answers = np.array(answers)
    return np.mean(answers * weight).item()

if __name__ == "__main__":
    results = []
    print(f"Starting evaluation for {len(prompts)} videos...")
    
    for i in range(len(prompts)):
        video_filename = f"prompt_{i:03d}.mp4"
        video_path = os.path.join(VIDEO_DIR, video_filename)
        prompt = prompts[i]
        
        if not os.path.exists(video_path):
            print(f"Warning: {video_path} not found. Skipping.")
            continue
            
        reward_score = score_video(video_path, prompt)
        print(f"[{i:03d}] {video_filename} | Score: {reward_score:.4f}")
        results.append({
            "id": i,
            "video": video_filename,
            "score": reward_score
        })

    # 保存结果到 JSON
    output_file = os.getenv("EVAL_OUTPUT", "batch_evaluation_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nEvaluation complete! Results saved to {output_file}")
    avg_score = np.mean([r['score'] for r in results])
    print(f"Average Score: {avg_score:.4f}")
