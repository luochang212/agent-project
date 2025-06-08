# CopilotKit

- GitHub: [CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit)
- Doc: [copilotkit](https://docs.copilotkit.ai/)

## 在 Ubuntu 上安装

参考：[quickstart](https://docs.copilotkit.ai/quickstart)

安装 node.js 和 npm

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install nodejs npm git -y
```

安装 CopilotKit

```bash
# 创建 Next.js 项目
npx create-next-app@latest my-copilot-app
cd my-copilot-app

# 安装 CopilotKit 核心包
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/backend

# 启动项目
npm run dev
```

在浏览器打开 [http://localhost:3000/](http://localhost:3000/)
