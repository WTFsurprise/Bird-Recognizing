# 鸟类识别平台 - 前端应用

React + Tailwind CSS 构建的现代化鸟类识别Web应用

## 🚀 快速开始

### 环境要求
- Node.js >= 16
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

注意：开发模式会自动代理 `/api/*` 请求到 `http://localhost:8000`(后端API)

### 生产构建

```bash
npm run build
```

输出目录: `dist/`

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── UploadZone.jsx  # 文件上传区域
│   │   ├── ResultCard.jsx  # 识别结果展示
│   │   ├── HistoryPanel.jsx # 历史记录面板
│   │   └── Alerts.jsx      # 提示和加载组件
│   ├── context/
│   │   └── AppContext.jsx  # 全局状态管理
│   ├── api/
│   │   └── birdService.js  # API 调用层
│   ├── styles/
│   │   └── index.css       # 全局样式
│   ├── App.jsx             # 主应用组件
│   └── main.jsx            # 应用入口
├── index.html              # HTML 入口
├── vite.config.js          # Vite 配置
├── tailwind.config.js      # Tailwind CSS 配置
├── postcss.config.js       # PostCSS 配置
└── package.json            # 项目配置
```

## 🎨 功能特性

- ✅ **拖拽上传** - 支持拖拽或点击上传鸟类图片
- ✅ **实时识别** - 上传后立即进行识别
- ✅ **热力图可视化** - 显示模型关注的区域
- ✅ **Top-3 结果** - 展示最可能的三个物种及置信度
- ✅ **历史记录** - 保存所有识别记录，支持删除和清空
- ✅ **置信度警告** - 低置信度时提醒用户
- ✅ **响应式设计** - 完全适配各种屏幕尺寸

## 🔧 配置

### 环境变量

复制 `.env.example` 为 `.env.local`:

```bash
cp .env.example .env.local
```

编辑 `.env.local`:

```
VITE_API_URL=http://localhost:8000
```

### 后端 API 地址

默认连接到 `http://localhost:8000`

在开发环境中，Vite 会自动转发 `/api` 请求到后端

在生产环境中，需要配置 CORS 或反向代理

## 📦 依赖说明

- **react** - UI 框架
- **react-dom** - React DOM 渲染
- **axios** - HTTP 客户端
- **tailwindcss** - CSS 框架
- **vite** - 构建工具

## 🚀 部署

### 基于 Node.js 的生产部署

```bash
npm run build
npm install -g serve
serve -s dist -p 3000
```

### 基于 Nginx 的部署

```bash
npm run build

# 配置 Nginx
location / {
    root /path/to/dist;
    try_files $uri /index.html;
}

location /api/ {
    proxy_pass http://localhost:8000;
}
```

### Docker 部署

详见项目根目录的 `docker-compose.yml`

```bash
docker-compose up
```

访问 http://localhost

## 🛠️ 开发

### 添加新组件

在 `src/components/` 创建新的 `.jsx` 文件，示例：

```jsx
export const MyComponent = () => {
  return <div className="...">组件内容</div>
}

export default MyComponent
```

### 使用全局状态

在组件中导入并使用 `useApp`:

```jsx
import { useApp } from '@/context/AppContext'

export const MyComponent = () => {
  const { loading, error } = useApp()
  // 使用状态...
}
```

### 调用 API

使用 `birdService`:

```jsx
import { birdService } from '@/api/birdService'

const result = await birdService.predict(file)
```

## 📝 自定义样式

样式位置：`src/styles/index.css`  
Tailwind 配置：`tailwind.config.js`

所有样式都是通过 Tailwind CSS 的 utility classes 或自定义 CSS 编写

## 🐛 常见问题

**Q: 连接不到后端？**
A: 确保后端 API 运行在 `http://localhost:8000`，检查 CORS 配置

**Q: 样式加载不正确？**
A: 清除 `node_modules` 和 `dist` 目录，重新执行 `npm install` 和 `npm run build`

**Q: 开发模式下 API 代理不工作？**
A: 检查 `vite.config.js` 中的 proxy 配置，且后端必须运行

## 📞 支持

如有问题，请检查：
1. 后端 API 是否正在运行
2. 环境变量配置是否正确
3. 网络连接是否正常

## 📄 许可证

MIT License
