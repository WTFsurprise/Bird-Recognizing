import torch
import torch.nn as nn
import timm

# 定义符合汇报要求的模型架构
class SwinBirdModel(nn.Module):
    def __init__(self, num_classes):
        super(SwinBirdModel, self).__init__()
        # 只构建网络结构，权重由本地 checkpoint 加载，避免运行时拉取外网预训练参数
        self.backbone = timm.create_model('swin_base_patch4_window12_384', pretrained=False, num_classes=0)
        self.embedding = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU()
        )
        self.classifier = nn.Linear(512, num_classes)

    def forward(self, x):
        features = self.backbone(x)
        embeds = self.embedding(features) # 512维特征向量
        logits = self.classifier(embeds)   # 分类概率
        return logits, embeds # 必须返回两个值