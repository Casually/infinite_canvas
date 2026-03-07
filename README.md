# 无限画布 (Infinite Canvas)

一个基于 Vue 3 和 Flask 构建的现代化协作式无限画布应用。它打破了传统文档的线性限制，提供了一个自由、无限的创作空间，支持富文本、代码运行、思维导图、多媒体等多种内容形式，适合知识管理、项目规划、头脑风暴等场景。

线上体验地址：[https://infinite-canvas.casually.cc/](https://infinite-canvas.casually.cc/) (示例地址)

![Screenshot](docs/imgs/image.png)

## ✨ 核心特性

- **♾️ 无限空间**：基于 Vue Flow 的无限画布，支持自由拖拽、缩放，内容展示无边界。
- **📝 富文本编辑**：内置强大的 Tiptap 编辑器，支持 Markdown 语法、表格、任务列表等。
- **🤝 实时协作**：支持多人同时在线编辑，光标实时同步，协同创作无延迟。
- **🧩 丰富的节点类型**：
  - **笔记节点**：基础富文本节点。
  - **多媒体**：支持图片、视频、音频（音乐播放器）。
  - **可视化**：Mermaid 图表（流程图、时序图等）、ECharts 图表、LaTeX 数学公式。
  - **生产力**：代码块（支持本地执行与结果回显）、网页卡片、日历、待办事项。
- **🔗 知识关联**：支持节点间连线，构建可视化的知识网络；支持节点分组管理。
- **🤖 智能辅助**：内置代码执行沙箱，支持 Python, JavaScript, Lua 等语言运行。
- **📂 数据管理**：支持画布数据的导出 (JSON) 与导入，本地备份更安心。

## 🛠️ 技术栈

### 前端 (Client)
- **框架**：Vue 3 + Vite + TypeScript
- **UI 库**：TailwindCSS + Lucide Icons
- **画布引擎**：@vue-flow/core
- **编辑器**：Tiptap (ProseMirror based)
- **可视化**：Mermaid, KaTeX, ECharts
- **通信**：Socket.IO Client

### 后端 (Server)
- **框架**：Flask (Python)
- **实时通信**：Flask-SocketIO
- **数据库**：SQLite (默认) / MySQL (支持) + SQLAlchemy
- **鉴权**：JWT (JSON Web Token)

## 🚀 快速开始

### 环境要求
- Node.js >= 16
- Python >= 3.10

### 1. 后端部署

```bash
cd server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建数据库目录 (SQLite)
mkdir -p instance

# 启动服务 (默认端口 5001)
./start.sh
# 或者
python app.py
```

### 2. 前端部署

```bash
cd client

# 安装依赖
npm install

# 启动开发服务器 (默认端口 5173)
npm run dev
```

访问 `http://localhost:5173` 即可开始使用。

## 📚 文档说明

项目包含详细的文档，位于 `docs/` 目录下：

- [📖 功能说明书 (Functional.md)](docs/Functional.md): 详细的功能列表和规格说明。
- [👩‍💻 用户操作指南 (UserGuide.md)](docs/UserGuide.md): 如何使用各个功能的详细教程。
- [⚙️ 开发文档 (Development.md)](docs/Development.md): 项目架构、目录结构和核心模块说明。
- [🚀 部署文档 (Deployment.md)](docs/Deployment.md): 生产环境部署指南。
- [🔄 更新日志 (Update.md)](docs/Update.md): 版本迭代记录。

## 📦 目录结构

```
.
├── client/                 # 前端项目源码
│   ├── src/
│   │   ├── components/     # Vue 组件 (节点、编辑器、弹窗等)
│   │   ├── utils/          # 工具函数
│   │   └── stores/         # Pinia 状态管理
│   └── ...
├── server/                 # 后端项目源码
│   ├── app.py              # Flask 应用入口
│   ├── instance/           # SQLite 数据库文件
│   └── uploads/            # 文件上传存储目录
└── docs/                   # 项目文档
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建新的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

[MIT](LICENSE)
