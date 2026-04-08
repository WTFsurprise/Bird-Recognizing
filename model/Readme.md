# 使用说明

1）模型是在kaggle上训练的，8016project.ipynb为包括数据集划分、模型训练以及简单效果测试的完整代码，在kaggle上可运行。
2）main.py、model.py、perception_engine.py是训练结束后考虑到后续流程的需要从8016project.ipynb中拆分出来的，能否正常运行未知，可按需进行修改。
3）数据集来源如下，训练集与验证集按照8：2划分，没有单独的测试集。
4）验证部分为从划分验证集中随机选取图片，返回top3可能物种数与置信分数，详见8016project.ipynb
5）目前的最佳结果为val acc=65.43%，如需更高准确度可继续尝试使用8016project.ipynb训练
6）训练时只使用了Train Mini Images [42GB]与Train Mini Annotations [45MB]，链接在下面

一切代码以8016project.ipynb为准！！！

## 数据集信息
选定的前 5 个科及其物种数:
 - Anatidae: 90 种
 - Accipitridae: 74 种
 - Scolopacidae: 53 种
 - Laridae: 49 种
 - Parulidae: 47 种
目标类别数: 313
总图片张数: 15650

 - 训练集样本数: 12520
 - 验证集样本数: 3130
 - 覆盖物种数: 313

## 数据集来源
Train Mini Images [42GB]
下载链接：
https://ml-inat-competition-datasets.s3.amazonaws.com/2021/train_mini.tar.gz
Train Mini Annotations [45MB]
下载链接：
https://ml-inat-competition-datasets.s3.amazonaws.com/2021/train_mini.json.tar.gz
附（可按需使用）：
Test Images [43GB]
https://ml-inat-competition-datasets.s3.amazonaws.com/2021/public_test.tar.gz
Test Info [21MB]
https://ml-inat-competition-datasets.s3.amazonaws.com/2021/public_test.json.tar.gz

## 项目简介
本项目旨在通过深度学习模型实现鸟类图像的分类和识别。主要功能包括：
- 加载预训练的Swin Transformer模型。
- 使用感知引擎对输入图像进行推理。
- 提供分类结果和置信度。

---

## 模型可解释性与可视化扩展

### model_explain 层

- `explain_engine.py`：实现了Grad-CAM++和自注意力两种可解释性方法，并支持多区域核心特征提取与可视化。
- 该层与原有模型结构解耦，便于独立测试和扩展。

### tests 层

- `tests/model_explain/`：用于存放可解释性分析的测试图片和输出结果。

### model_explain.py

- 该脚本为可解释性分析的主入口，支持一键生成推理结果、两种热力图、核心特征放大图等。
- 所有输入输出均在 `tests/model_explain/` 目录下，便于统一管理和复现。

### perception_engine 的修改

- 新增了 `_extract_attention_map` 方法，用于提取Swin Transformer模型的自注意力权重，并生成可视化热力图。
- 保持与原有推理流程兼容，便于主流程直接调用。

---

## 可解释性输出说明

### 1. Grad-CAM++ 热力图（`test_gradcam_heatmap.jpg`）

- 该热力图基于模型最后一层特征的梯度信息，突出显示了对模型分类决策贡献最大的图像区域。
- 叠加在原图上，红色/黄色区域表示模型最关注的“核心视觉特征”。

### 2. 自注意力热力图（`test_attention_heatmap.jpg`）

- 该热力图基于Swin Transformer的自注意力机制，反映模型在不同空间位置的关注分布。
- 可用于分析模型是否聚焦于鸟类本体或被背景干扰。

### 3. 核心特征放大图（`test_core_feature_crop_*.jpg`）

- 自动从Grad-CAM++热力图中提取前N个最大连通域（高贡献区域），并裁剪、放大为独立图片。
- 便于直观观察模型判别时最依赖的细节特征（如鸟头、翅膀、花纹等）。

---

## 文件结构
- `main.py`：主程序文件，负责加载模型和执行推理。
- `model.py`：定义了Swin Transformer模型的结构。
- `perception_engine.py`：实现了感知引擎，用于处理图像和生成推理结果。
- `model_explain.py`：可解释性分析主程序。
- `class_mapping.json`：存储类别映射关系。
- `swin_bird_stage1_best.pth` 和 `swin_bird_stage2_best.pth`：预训练模型权重文件。
- `model_explain/`：可解释性分析相关模块。
- `tests/model_explain/`：可解释性分析的输入输出目录。

## 环境配置
1. 安装必要的Python库：
   ```bash
   pip install torch torchvision timm pillow numpy opencv-python pytorch-grad-cam
   ```

2. 确保您的设备支持CUDA（可选）。

## 使用方法

### 主程序 main.py
1. 准备输入图像：
   将待识别的鸟类图像命名为`test_bird.jpg`并放置在项目根目录。

2. 运行主程序：
   ```bash
   python main.py
   ```

3. 查看输出结果：
   - 如果置信度较低，程序会提示用户重新拍摄更清晰的图像。
   - 如果置信度较高，程序会输出识别的鸟类名称及其置信度。

### 解释性分析 model_explain.py
1. 准备输入图像：
   将待识别的鸟类图像命名为`test.jpg`或`test_*.jpg`并放置在`model/tests/model_explain/`目录下。

2. 运行解释性分析程序：
   ```bash
   python model_explain.py
   ```
   
3. 查看输出结果：
   - `tests/model_explain/` 目录下将根据所有符合条件的测试图片，生成多张可视化图片。

## 注意事项
- 请确保输入图像为RGB格式。
- 如果需要识别其他类别，请更新`class_mapping.json`并重新训练模型。
- 可解释性分析依赖于`pytorch-grad-cam`等库，请提前安装。

## 参考
- Swin Transformer: https://github.com/microsoft/Swin-Transformer
- PyTorch: https://pytorch.org/
- Grad-CAM++: https://arxiv.org/abs/1710.11063
- pytorch-grad-cam: https://github.com/jacobgil/pytorch-grad-cam
