# Agent（代理）详解

## 什么是 Agent？

**一句话定义**：Agent 就是具有特定"性格"和"能力"的 AI 助手。

### 生活类比

想象你去一家公司办事，会遇到不同类型的员工：

| 员工类型 | 特点 | 对应 Agent |
|---------|------|-----------|
| 前台接待 | 只能看信息，不能改系统 | Plan Agent |
| 开发工程师 | 可以写代码、改文件、跑命令 | Build Agent |
| 搜索助手 | 快速找到你要的文件 | Explore Agent |
| 项目经理 | 能调度多个助手完成复杂任务 | General Agent |

---

## Agent 的两种类型

```
┌─────────────────────────────────────────────────────────────────┐
│                       Agent 类型                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Primary Agents（主代理）                  │   │
│  │                                                          │   │
│  │  你直接对话的主角，可以用 Tab 键切换                        │   │
│  │                                                          │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐           │   │
│  │  │  Build   │    │   Plan   │    │ 自定义... │           │   │
│  │  │ 能改代码  │    │ 只能规划  │    │          │           │   │
│  │  └──────────┘    └──────────┘    └──────────┘           │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Subagents（子代理）                        │   │
│  │                                                          │   │
│  │  被主代理调用的专家，或者你用 @ 主动召唤                     │   │
│  │                                                          │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐           │   │
│  │  │  General │    │  Explore │    │ 自定义... │           │   │
│  │  │ 通用任务  │    │ 代码搜索  │    │          │           │   │
│  │  └──────────┘    └──────────┘    └──────────┘           │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Primary Agent（主代理）
- 你直接对话的对象
- 用 **Tab 键** 在不同主代理之间切换
- 默认有两个：Build 和 Plan

### Subagent（子代理）
- 专门处理特定任务的专家
- 主代理会在需要时自动调用它们
- 你也可以用 `@代理名` 主动召唤

---

## 内置 Agent 详解

### Build Agent（构建代理）

**特点**：全能选手，可以做任何事

```
能力：
✅ 读取文件 (read)
✅ 写入文件 (write)
✅ 编辑文件 (edit)
✅ 执行命令 (bash)
✅ 搜索文件 (grep/glob)
✅ 访问网页 (webfetch)
```

**适用场景**：
- 实现新功能
- 修复 Bug
- 重构代码
- 任何需要改动的工作

**使用方式**：
```
# 默认就是 Build 模式，直接说需求
Add a login function with email validation
```

---

### Plan Agent（规划代理）

**特点**：只看不动手，专注分析和规划

```
能力：
✅ 读取文件 (read)
✅ 搜索文件 (grep/glob)
❌ 写入文件 (write) - 需要确认
❌ 编辑文件 (edit) - 需要确认
❌ 执行命令 (bash) - 需要确认
```

**适用场景**：
- 分析代码架构
- 制定实现方案
- 代码审查
- 学习理解项目

**使用方式**：
```
# 按 Tab 切换到 Plan 模式
<Tab>

# 让它分析和规划
How would you implement a caching system for our API?
```

---

### Explore Agent（探索代理）

**特点**：快速搜索专家，专注代码探索

```
能力：
✅ 读取文件 (read)
✅ 搜索文件 (grep/glob)
❌ 写入文件 (write)
❌ 编辑文件 (edit)
```

**适用场景**：
- 查找特定函数
- 理解代码结构
- 定位文件位置

**使用方式**：
```
# 用 @ 召唤
@explore find all files related to authentication
```

---

### General Agent（通用代理）

**特点**：多面手，处理复杂的多步骤任务

**适用场景**：
- 需要多个步骤的研究任务
- 不确定结果的搜索
- 复杂的代码分析

**使用方式**：
```
# 用 @ 召唤
@general search for all usages of the deprecated API
```

---

## 如何切换 Agent

### 方法1：Tab 键切换主代理
```
# 按 Tab 键循环切换
Build → Plan → Build → ...

# 界面右下角会显示当前 Agent
```

### 方法2：@ 召唤子代理
```
# 直接在消息中 @ 子代理
@explore find the main entry point
@general help me understand the authentication flow
```

---

## 自定义 Agent

### 用 JSON 配置

在 `opencode.json` 中添加：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "专门做代码审查的代理",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "你是一个代码审查专家。关注安全性、性能和可维护性。",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

### 用 Markdown 配置

创建文件 `.opencode/agent/reviewer.md`：

```markdown
---
description: 专门做代码审查的代理
mode: subagent
tools:
  write: false
  edit: false
---

你是一个代码审查专家。

重点关注：
- 代码质量和最佳实践
- 潜在的 Bug 和边界情况
- 性能影响
- 安全考虑

只提供建设性反馈，不直接修改代码。
```

### 使用自定义 Agent
```
@code-reviewer review the changes in src/auth/login.ts
```

---

## Agent 配置选项详解

| 选项 | 说明 | 示例值 |
|------|------|--------|
| `description` | 描述什么时候用这个 Agent | "审查代码质量" |
| `mode` | `primary`（主）或 `subagent`（子） | "subagent" |
| `model` | 使用的 AI 模型 | "anthropic/claude-sonnet-4" |
| `prompt` | 系统提示词 | "你是一个专家..." |
| `tools` | 可用工具配置 | `{"write": false}` |
| `temperature` | 创造性程度（0-1） | 0.1 |
| `maxSteps` | 最大执行步数 | 10 |
| `permission` | 权限配置 | `{"edit": "ask"}` |

---

## 实用技巧

### 1. 先规划后执行
```
# 步骤1：切到 Plan 模式，让 AI 规划
<Tab>
I want to add user authentication to this app

# 步骤2：满意后切回 Build 模式
<Tab>
Go ahead and implement the plan
```

### 2. 让探索代理先侦查
```
# 先了解代码结构
@explore how is the database connection handled?

# 再做修改
Now update the connection pool size to 20
```

### 3. 用子代理分而治之
```
# 复杂任务分解
@general find all deprecated API usages
@code-reviewer check the security of auth module
Then fix the issues found
```

---

## 常见问题

### Q: Build 和 Plan 有什么区别？
**A:** Build 可以直接改代码，Plan 只能看和规划。就像施工队（Build）和设计师（Plan）的区别。

### Q: 什么时候用 @explore？
**A:** 当你需要快速找到某个文件或函数时。比 Build Agent 更快更专注。

### Q: 自定义 Agent 会影响内置 Agent 吗？
**A:** 不会。自定义的是新增的，内置的还是原来的样子。除非你明确禁用内置 Agent。

### Q: 如何禁用一个 Agent？
**A:** 在配置中设置 `"disable": true`：
```json
{
  "agent": {
    "explore": {
      "disable": true
    }
  }
}
```

---

## 下一步

- 了解 Agent 可以使用的 [Tools（工具）](./02-tools.md)
- 学习如何配置 [Provider（提供商）](./03-provider.md)
- 查看 [实战案例](./case-add-feature.md)
