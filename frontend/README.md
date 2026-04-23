# BPM-Nova Frontend

基于 React + TypeScript + Vite 的前端应用，采用 Apple 风格设计。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **路由**: React Router v6
- **状态管理**: Zustand
- **样式**: Tailwind CSS
- **动画**: Framer Motion
- **HTTP客户端**: Axios

## 安装依赖

```bash
cd frontend
npm install
```

## 开发运行

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

## 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── pages/          # 页面组件
│   │   ├── LoginPage.tsx
│   │   └── HomePage.tsx
│   ├── stores/         # Zustand状态管理
│   │   ├── authStore.ts
│   │   └── sessionStore.ts
│   ├── components/     # 可复用组件（待创建）
│   ├── App.tsx         # 根组件
│   ├── main.tsx        # 入口文件
│   └── index.css       # 全局样式
├── public/             # 静态资源
└── index.html          # HTML模板
```

## 设计系统

### 颜色
- Primary: Blue (500-600)
- Secondary: Purple (500-600)
- Gray: 50-900

### 圆角
- `rounded-apple`: 12px
- `rounded-apple-lg`: 16px
- `rounded-apple-xl`: 20px

### 阴影
- `shadow-apple`: 标准阴影
- `shadow-apple-lg`: 大阴影
- `shadow-apple-xl`: 超大阴影

### 毛玻璃效果
- `glass-effect`: 背景模糊 + 半透明

## API代理配置

开发环境下，所有 `/api` 请求会被代理到 `http://localhost:8000`（FastAPI后端）

## 下一步

1. 安装依赖: `npm install`
2. 启动开发服务器: `npm run dev`
3. 访问 http://localhost:5173
4. 使用任意用户名和密码登录