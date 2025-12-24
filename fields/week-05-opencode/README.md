# OpenCode 小白入门教程

> **终局定方向，流程搭骨架，单点打通关，类比挂认知。**

## 1. 终极目标

### 解决的问题
OpenCode 解决的核心问题是：**让 AI 直接帮你写代码、改代码、执行命令**。

想象一下，你有一个超级聪明的编程助手，它能：
- 理解你的代码仓库
- 帮你写新功能
- 帮你修 Bug
- 帮你执行终端命令
- 甚至能帮你分析和重构代码

### 最终交付物
- 一个能用自然语言操控的 **AI 编程助手**
- 支持终端 TUI、桌面应用、IDE 扩展三种使用方式
- 可以连接 75+ 种 LLM 提供商（OpenAI、Anthropic、Google 等）

### 评判标准
- 能否通过自然语言让 AI 完成编码任务
- 是否提高了编程效率
- 是否减少了重复性工作

---

## 2. 流程全景图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenCode 工作流程全景图                               │
└─────────────────────────────────────────────────────────────────────────────┘

  你（用户）                    OpenCode                     LLM（大语言模型）
     │                            │                              │
     │  1. 输入自然语言指令         │                              │
     │  "帮我写一个登录功能"   ────>│                              │
     │                            │                              │
     │                            │  2. 分析项目结构+构建提示词     │
     │                            │────────────────────────────>│
     │                            │                              │
     │                            │  3. LLM 返回代码和操作指令     │
     │                            │<────────────────────────────│
     │                            │                              │
     │                            │  4. 执行工具调用：              │
     │                            │     - 读取文件                 │
     │                            │     - 写入文件                 │
     │                            │     - 编辑代码                 │
     │                            │     - 执行 bash 命令          │
     │                            │                              │
     │  5. 展示结果，等待下一步指令  │                              │
     │<────────────────────────── │                              │
     │                            │                              │
     └────────────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            核心组件分解                                      │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌──────────────────┐
                          │    用户界面层      │
                          │  (TUI/Desktop/   │
                          │   IDE Extension) │
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │   Agent 代理层    │
                          │ (Build/Plan/     │
                          │  Explore 等)     │
                          └────────┬─────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
  ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
  │   工具层 Tools   │    │ Provider 提供商 │    │   会话管理层     │
  │ (read/write/    │    │ (OpenAI/Claude │    │  (Session)      │
  │  edit/bash等)   │    │  /Gemini等)    │    │                 │
  └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 3. 核心概念和关键流程解释

| 概念 | 一句话解释 | 教程链接 |
|------|-----------|---------|
| **Agent（代理）** | 就像不同性格的助手，有的能改代码，有的只能看 | [tutorials/01-agent.md](./01-agent.md) |
| **Tools（工具）** | AI 可以调用的能力，比如读文件、写文件、执行命令 | [tutorials/02-tools.md](./02-tools.md) |
| **Provider（提供商）** | 提供 AI 大脑的服务商，如 OpenAI、Anthropic | [tutorials/03-provider.md](./03-provider.md) |
| **Mode（模式）** | Build 模式可以改代码，Plan 模式只能规划 | [tutorials/04-mode.md](./04-mode.md) |
| **MCP Server** | 扩展 AI 能力的外部服务，如数据库访问 | [tutorials/05-mcp.md](./05-mcp.md) |
| **Command（命令）** | 预定义的快捷操作，如 /test 运行测试 | [tutorials/06-command.md](./06-command.md) |
| **Config（配置）** | OpenCode 的设置文件，控制各种行为 | [tutorials/07-config.md](./07-config.md) |
| **Permission（权限）** | 控制 AI 能做什么，不能做什么 | [tutorials/08-permission.md](./08-permission.md) |
| **SDK/API** | 程序化控制 OpenCode，实现自动化和集成 | [tutorials/09-sdk.md](./09-sdk.md) |
| **多 Agent 并行** | 多模型并行审查，实现交叉验证 | [tutorials/10-multi-agent-parallel-review.md](./10-multi-agent-parallel-review.md) |

---

## 4. 单点穿透案例

想要快速上手？从这个案例开始：

### [案例：用 OpenCode 给项目添加一个新功能](./case-add-feature.md)

这个案例会带你：
1. 安装和配置 OpenCode
2. 用 Plan 模式让 AI 先规划方案
3. 切换到 Build 模式让 AI 实现代码
4. 使用 /undo 撤销不满意的改动
5. 用自定义命令提高效率

---

## 5. 快速入门指南

### 安装
```bash
# 最简单的方式
curl -fsSL https://opencode.ai/install | bash

# 或者用 npm
npm install -g opencode-ai

# 或者用 Homebrew (macOS/Linux)
brew install opencode
```

### 配置 API Key
```bash
# 启动 opencode
opencode

# 在 TUI 中运行
/connect

# 选择提供商，输入 API Key
```

### 初始化项目
```bash
# 进入你的项目目录
cd /path/to/your/project

# 启动 opencode
opencode

# 初始化（生成 AGENTS.md 文件）
/init
```

### 开始使用
```
# 问问题
How is authentication handled in this project?

# 让它改代码（先用 Tab 切换到 Plan 模式规划）
<Tab>
Add a dark mode toggle to the settings page

# 满意后切换到 Build 模式执行
<Tab>
Go ahead and implement this

# 不满意就撤销
/undo
```

---

## 6. 目录结构

```
tutorials/
├── README.md                 # 本文件 - 学习框架总览
├── 01-agent.md              # Agent 代理详解
├── 02-tools.md              # Tools 工具详解
├── 03-provider.md           # Provider 提供商详解
├── 04-mode.md               # Mode 模式详解
├── 05-mcp.md                # MCP Server 详解
├── 06-command.md            # Command 命令详解
├── 07-config.md             # Config 配置详解
├── 08-permission.md         # Permission 权限详解
├── 09-sdk.md                # SDK/API 详解
├── 10-multi-agent-parallel-review.md  # 多 Agent 并行 Review 方案
└── case-add-feature.md      # 实战案例：添加新功能
```

---

## 7. 类比理解

把 OpenCode 想象成一个**编程界的美团外卖**：

| OpenCode 概念 | 类比 |
|--------------|------|
| OpenCode | 美团 App |
| Agent | 配送员（有的只送餐不做饭，有的全能） |
| Tools | 配送员的技能（骑车、开车、找路） |
| Provider | 餐厅（麦当劳、肯德基提供不同食物） |
| LLM Model | 具体的菜品（巨无霸、炸鸡） |
| Command | 快捷下单（"老样子"按钮） |
| MCP Server | 外挂服务（优惠券、会员积分） |
| Permission | 家长模式（限制配送范围和时间） |

---

## 8. 常见问题

### Q: OpenCode 和 GitHub Copilot 有什么区别？
**A:** Copilot 主要是代码补全，OpenCode 是一个完整的 AI 编程代理。它不只是补全代码，还能执行命令、管理文件、理解整个项目。

### Q: 我需要付费吗？
**A:** OpenCode 本身开源免费。但你需要有 LLM 提供商的 API Key（如 OpenAI、Anthropic），这些通常需要付费。

### Q: 支持哪些编程语言？
**A:** 所有语言！因为 AI 模型是通用的，理论上支持任何编程语言。

### Q: 安全吗？会不会把我的代码泄露？
**A:** 代码会发送给 LLM 提供商处理。如果担心，可以使用本地模型（如 Ollama）。

---

## 下一步

1. **完全没基础**：先看 [案例：添加新功能](./case-add-feature.md)
2. **想深入了解**：按顺序看核心概念教程（01-08）
3. **想快速上手**：看完本文的"快速入门指南"直接开干

祝你学习愉快！
