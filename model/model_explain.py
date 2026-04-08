import torch
import json
import cv2
import numpy as np
import os
import re
from PIL import Image
from torchvision import transforms
from model import SwinBirdModel
from perception_engine import BirdPerceptionEngine
from model_explain.explain_engine import ExplainEngine

# 配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
WEIGHTS_PATH = 'swin_bird_stage2_best.pth'
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(CUR_DIR, 'tests', 'model_explain')
TOP_N_CORE_FEATURES = 3  # 提取前3个核心特征区域
CROP_SIZE = (448, 448)  # 核心区域放大后的尺寸
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')  # 常规图片后缀
IMAGE_NAME_PATTERN = re.compile(r'^test(_\d+)?\.(jpg|jpeg|png|webp)$', re.IGNORECASE)  # 例：test.jpg / test_1.png等


# 0. 辅助函数：获取符合规则的测试图片列表
def get_valid_test_images(test_dir):
    """
    扫描TESTS_DIR，获取符合规则的测试图片路径列表
    规则：严格为 test.图片后缀 或 test_数字.图片后缀
    """
    valid_image_list = []
    os.makedirs(test_dir, exist_ok=True)  # 确保目录存在

    for filename in os.listdir(test_dir):
        file_path = os.path.join(test_dir, filename)
        # 过滤：仅文件 + 正则匹配文件名
        if os.path.isfile(file_path) and IMAGE_NAME_PATTERN.match(filename):
            valid_image_list.append(file_path)

    # 按文件名排序（test → test_1 → test_2...）
    valid_image_list.sort()
    return valid_image_list


# 1. 加载类别映射
with open('class_mapping.json', 'r') as f:
    class_map = json.load(f)
    class_names = [class_map[str(i)] for i in range(len(class_map))]
    # 反向映射：物种名 -> 类别编号
    species_to_classid = {v: int(k) for k, v in class_map.items()}


# 2. 图像预处理
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((384, 384)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(DEVICE)
    original_image = np.array(image.resize((384, 384))) / 255.0
    return image_tensor, original_image


# 3. 加载模型
def load_model():
    model = SwinBirdModel(num_classes=len(class_names))
    checkpoint = torch.load(WEIGHTS_PATH, map_location=DEVICE)
    state_dict = checkpoint['model_state_dict'] if 'model_state_dict' in checkpoint else checkpoint
    model.load_state_dict(state_dict)
    return model


if __name__ == "__main__":
    # 加载模型与推理引擎
    print("=== 加载模型与推理引擎 ===")
    model = load_model()
    perception_engine = BirdPerceptionEngine(model, DEVICE, class_names)
    explain_engine = ExplainEngine(model, DEVICE)

    # 获取符合规则的测试图片列表
    TEST_IMAGE_PATH_LIST = get_valid_test_images(TESTS_DIR)

    # 校验：无符合规则的图片则退出
    if not TEST_IMAGE_PATH_LIST:
        print(f"未在 {TESTS_DIR} 找到符合规则的测试图片！")
        exit()
    print(f"找到 {len(TEST_IMAGE_PATH_LIST)} 张符合规则的测试图片")
    print("-" * 50)

    # 遍历所有测试图片，批量处理
    for img_idx, img_path in enumerate(TEST_IMAGE_PATH_LIST, 1):
        print(f"开始处理第 {img_idx}/{len(TEST_IMAGE_PATH_LIST)} 张图片：{os.path.basename(img_path)}")

        # 提取原图片名（无后缀）
        img_filename = os.path.basename(img_path)
        img_name_prefix = os.path.splitext(img_filename)[0]

        # 加载当前图片
        image_tensor, original_image = preprocess_image(img_path)

        # 获取预测结果
        result = perception_engine.infer(image_tensor)
        pred_species = result['top_3'][0]['species']
        pred_conf = result['top_3'][0]['confidence']
        target_class = species_to_classid[pred_species]
        print(f"=== 模型预测结果 ===")
        print(f"鸟类种类: {pred_species} | 置信度: {pred_conf:.2%} | 类别ID: {target_class}")

        # 生成Grad-CAM++热力图
        print("\n=== 生成Grad-CAM++热力图 ===")
        heatmap = explain_engine.generate_heatmaps(image_tensor, target_class)

        # 可视化+裁剪多个核心特征
        overlay_img, crop_imgs = explain_engine.fuse_and_visualize(
            heatmap,
            original_image,
            top_n=TOP_N_CORE_FEATURES,
            crop_size=CROP_SIZE
        )

        # 保存热力图叠加图（原图片名前缀）
        overlay_path = os.path.join(TESTS_DIR, f"{img_name_prefix}_gradcam_heatmap.jpg")
        cv2.imwrite(overlay_path, cv2.cvtColor(overlay_img, cv2.COLOR_RGB2BGR))
        print(f"热力图保存：{os.path.basename(overlay_path)}")

        # 保存核心特征放大图
        if crop_imgs:
            for i, crop_img in enumerate(crop_imgs):
                save_path = os.path.join(TESTS_DIR, f"{img_name_prefix}_core_feature_crop_{i + 1}.jpg")
                cv2.imwrite(save_path, cv2.cvtColor((crop_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
                print(f"核心特征{i + 1}保存：{os.path.basename(save_path)}")
        else:
            print("未检测到有效核心特征区域")

        # 保存自注意力图
        print("\n=== 生成自注意力热力图 ===")
        attention_map = perception_engine._extract_attention_map(image_tensor)
        attention_overlay = explain_engine.visualize_attention(attention_map, original_image)
        attention_path = os.path.join(TESTS_DIR, f"{img_name_prefix}_attention_heatmap.jpg")
        cv2.imwrite(attention_path, cv2.cvtColor(attention_overlay, cv2.COLOR_RGB2BGR))
        print(f"注意力图保存：{os.path.basename(attention_path)}")
        print("-" * 50)

    print("=== 图片处理全部结束 ===")