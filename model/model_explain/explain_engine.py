import numpy as np
import cv2
import torch
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image


class ExplainEngine:
    def __init__(self, model, device):
        """
        初始化可解释性引擎
        :param model: SwinBirdModel模型
        :param device: 运行设备
        """
        self.model = model.to(device)
        self.model.eval()
        self.device = device

    def _normalize_and_resize(self, heatmap, size):
        """热力图归一化+尺寸对齐"""
        heatmap = heatmap - np.min(heatmap)
        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)
        heatmap = cv2.resize(heatmap, (size[1], size[0]))
        return heatmap

    def grad_cam_plus_plus(self, image_tensor, target_layer, target_class):
        # 适配SwinTransformer的维度重塑函数
        def reshape_transform(tensor):
            h = w = int(np.sqrt(tensor.shape[1]))
            result = tensor.reshape(tensor.shape[0], h, w, tensor.shape[2])
            result = result.permute(0, 3, 1, 2)
            return result

        # 指定模型预测的目标类别，生成对应类别的热力图
        targets = [ClassifierOutputTarget(target_class)]
        cam = GradCAMPlusPlus(
            model=self.model,
            target_layers=[target_layer],  # 模型目标特征层（热力图生成来源）
            reshape_transform=reshape_transform,  # Swin/ViT模型专用维度适配
        )
        cam.aug_smooth = True  # 增强平滑，减少热力图噪声
        cam.eigen_smooth = True  # 特征值平滑，提升热力图清晰度与定位精度
        with torch.enable_grad():
            grayscale_cam = cam(input_tensor=image_tensor, targets=targets)[0]
        return grayscale_cam

    def generate_heatmaps(self, image_tensor, target_class):
        """生成热力图（固定Swin最优层）"""
        # SwinTransformer主干网最优热力图生成层
        target_layer = self.model.backbone.layers[1].blocks[-1].norm2
        gradcam_heatmap = self.grad_cam_plus_plus(image_tensor, target_layer, target_class)
        gradcam_heatmap = self._normalize_and_resize(
            gradcam_heatmap,
            size=(image_tensor.shape[-2], image_tensor.shape[-1])
        )
        return gradcam_heatmap

    def fuse_and_visualize(self, gradcam_heatmap, original_image, top_n=3, crop_size=(448, 448),
                           max_area_ratio=0.15):
        """
        可视化+多核心区域裁剪放大（无最小面积限制+非重叠非包裹+红度优先）
        :param gradcam_heatmap: 归一化后的热力图
        :param original_image: 原始图像（0-1范围）
        :param top_n: 提取前N个核心区域
        :param crop_size: 裁剪放大尺寸
        :param max_area_ratio: 矩形最大面积占比（15%，避免超大框）
        :return: overlay(叠加图), crop_imgs(放大图列表)
        """
        # 1. 阈值过滤
        top_percent = 0.15  # 百分比阈值：保留热力图中前X%高响应区域
        percentile_thresh = np.percentile(gradcam_heatmap, 100 * (1 - top_percent))
        abs_thresh = 0.3  # 绝对强度阈值，过滤分数低于X的低响应区域
        mask = (gradcam_heatmap >= percentile_thresh) & (gradcam_heatmap >= abs_thresh)  # 双重阈值过滤
        mask = mask.astype(np.uint8)

        # 2. 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # 3. 生成热力图
        overlay = show_cam_on_image(original_image, gradcam_heatmap, use_rgb=True)

        # 图像尺寸
        img_h, img_w = original_image.shape[:2]
        img_total_area = img_h * img_w
        max_allowed_area = img_total_area * max_area_ratio  # 单个框最大占比15%，防止超大框覆盖全局

        # 4. 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        crop_imgs = []
        if contours:
            # 第一步：仅过滤超大区域，保留微小区域（眼睛/喙）
            filtered_contours = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                rect_area = w * h
                # 仅判断最大面积，无最小面积限制
                if rect_area <= max_allowed_area:
                    filtered_contours.append(contour)
            if not filtered_contours:
                return overlay, crop_imgs

            # 第二步：热力图红度优先排序
            contour_info = []
            for contour in filtered_contours:
                single_mask = np.zeros_like(mask)
                cv2.drawContours(single_mask, [contour], 0, 1, -1)
                single_mask = single_mask.astype(bool)
                region_heat = gradcam_heatmap[single_mask]
                max_heat = np.max(region_heat)
                area = cv2.contourArea(contour)
                contour_info.append((-max_heat, -area, contour))
            contour_info.sort()
            sorted_candidates = [contour for (_, _, contour) in contour_info]

            # 第三步：标注框（非重叠+非包裹过滤）
            final_contours = []
            final_boxes = []

            for cnt in sorted_candidates:
                x, y, w, h = cv2.boundingRect(cnt)
                curr_x1, curr_y1 = x, y
                curr_x2, curr_y2 = x + w, y + h
                valid = True

                for (fx1, fy1, fx2, fy2) in final_boxes:
                    is_overlap = not (curr_x2 <= fx1 or curr_x1 >= fx2 or curr_y2 <= fy1 or curr_y1 >= fy2)
                    is_cover = (curr_x1 <= fx1 and curr_y1 <= fy1 and curr_x2 >= fx2 and curr_y2 >= fy2) or \
                               (fx1 <= curr_x1 and fy1 <= curr_y1 and fx2 >= curr_x2 and fy2 >= curr_y2)

                    if is_overlap or is_cover:
                        valid = False
                        break

                if valid:
                    final_contours.append(cnt)
                    final_boxes.append((curr_x1, curr_y1, curr_x2, curr_y2))
                    if len(final_contours) >= top_n:  # 仅保留前n个核心特征区域
                        break

            # 绘制与裁剪
            for i, contour in enumerate(final_contours):
                single_mask = np.zeros_like(mask)
                cv2.drawContours(single_mask, [contour], 0, 1, -1)
                single_mask = single_mask.astype(bool)

                y_coords, x_coords = np.where(single_mask)
                x1, y1 = x_coords.min(), y_coords.min()
                x2, y2 = x_coords.max(), y_coords.max()

                buffer = 3
                x1 = max(0, x1 - buffer)
                y1 = max(0, y1 - buffer)
                x2 = min(original_image.shape[1] - 1, x2 + buffer)
                y2 = min(original_image.shape[0] - 1, y2 + buffer)

                # 红色框标注
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(overlay, str(i + 1), (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                crop_img = original_image[y1:y2, x1:x2]
                crop_img = cv2.resize(crop_img, crop_size)
                crop_imgs.append(crop_img)

        return overlay, crop_imgs

    # 自注意力热力图
    def visualize_attention(self, attention_map, original_image):
        if attention_map.shape != (384, 384):
            attention_map = cv2.resize(attention_map, (384, 384))
        # 归一化到 0~1 范围（和 Grad-CAM++ 保持一致）
        attention_map = attention_map - np.min(attention_map)
        if np.max(attention_map) > 0:
            attention_map = attention_map / np.max(attention_map)
        return show_cam_on_image(original_image, attention_map, use_rgb=True)
