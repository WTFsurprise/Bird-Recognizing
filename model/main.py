import torch
import json
from PIL import Image
from model import SwinBirdModel
from perception_engine import BirdPerceptionEngine

# 1. 基础配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
WEIGHTS_PATH = 'swin_bird_stage2_best.pth' # 之前保存的 Stage 2 权重

# 2. 加载类别映射 
with open('class_mapping.json', 'r') as f:
    class_map = json.load(f)
    # 确保 class_names 的顺序与训练标签 [0, 1, 2...] 严格对应
    class_names = [class_map[str(i)] for i in range(len(class_map))]

# 3. 初始化引擎
model = SwinBirdModel(num_classes=len(class_names))
# 加载权重 (兼容带日志和纯权重的格式)
checkpoint = torch.load(WEIGHTS_PATH, map_location=DEVICE)
state_dict = checkpoint['model_state_dict'] if 'model_state_dict' in checkpoint else checkpoint
model.load_state_dict(state_dict)

engine = BirdPerceptionEngine(model, DEVICE, class_names)

# 4. 执行推理
test_img = Image.open("test_bird.jpg").convert('RGB')
result = engine.infer(test_img)

if result['suggestion']:
    print(f"提示用户: {result['suggestion']}")
else:
    print(f"识别结果: {result['top_3'][0]['species']} ({result['top_3'][0]['confidence']:.2%})")