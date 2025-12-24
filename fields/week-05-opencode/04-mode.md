# Mode（模式）详解

## 什么是 Mode？

**一句话定义**：Mode 决定了 AI 能做什么——Build 模式能改代码，Plan 模式只能看和规划。

### 生活类比

| Mode | 类比 | 特点 |
|------|------|------|
| Build | 施工队 | 能动手干活，改造房子 |
| Plan | 设计师 | 只能画图纸，不动砖瓦 |

---

## Mode 工作流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Mode 工作流程                                │
└─────────────────────────────────────────────────────────────────┘

                        ┌───────────────┐
                        │   开始使用     │
                        └───────┬───────┘
                                │
                                ▼
            ┌──────────────────────────────────────┐
            │         你想让 AI 做什么？            │
            └──────────────────────────────────────┘
                      /                \
                     /                  \
                    ▼                    ▼
        ┌───────────────────┐  ┌───────────────────┐
        │  直接改代码/跑命令 │  │  先分析/规划方案   │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                      │
                  ▼                      ▼
        ┌───────────────────┐  ┌───────────────────┐
        │    Build Mode     │  │    Plan Mode      │
        │                   │  │                   │
        │  ✅ 读文件         │  │  ✅ 读文件         │
        │  ✅ 写文件         │  │  ⚠️ 写文件(需确认) │
        │  ✅ 编辑文件       │  │  ⚠️ 编辑(需确认)  │
        │  ✅ 执行命令       │  │  ⚠️ 命令(需确认)  │
        │  ✅ 搜索文件       │  │  ✅ 搜索文件       │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                      │
                  │      ┌───┐           │
                  │      │Tab│           │
                  └─────>│ 键 │<──────────┘
                         │切换│
                         └───┘
```

---

## Build Mode（构建模式）

### 特点
- **默认模式**
- 可以执行所有操作
- AI 会直接修改你的代码

### 能力清单

| 工具 | 状态 | 说明 |
|------|------|------|
| read | ✅ 可用 | 读取文件 |
| write | ✅ 可用 | 创建新文件 |
| edit | ✅ 可用 | 编辑现有文件 |
| patch | ✅ 可用 | 应用补丁 |
| bash | ✅ 可用 | 执行命令 |
| grep | ✅ 可用 | 搜索内容 |
| glob | ✅ 可用 | 搜索文件 |
| webfetch | ✅ 可用 | 访问网页 |

### 适用场景

- ✅ 实现新功能
- ✅ 修复 Bug
- ✅ 重构代码
- ✅ 运行测试
- ✅ 安装依赖

### 使用示例

```
# Build 模式下，直接说需求，AI 就会动手改
Add a logout button to the header component

# AI 会：
# 1. 找到 header 组件
# 2. 添加按钮代码
# 3. 可能还会添加相关的样式和逻辑
```

---

## Plan Mode（规划模式）

### 特点
- **只读模式**
- 不会直接修改代码
- 适合先规划再执行

### 能力清单

| 工具 | 状态 | 说明 |
|------|------|------|
| read | ✅ 可用 | 读取文件 |
| write | ⚠️ 需确认 | 创建新文件 |
| edit | ⚠️ 需确认 | 编辑现有文件 |
| patch | ⚠️ 需确认 | 应用补丁 |
| bash | ⚠️ 需确认 | 执行命令 |
| grep | ✅ 可用 | 搜索内容 |
| glob | ✅ 可用 | 搜索文件 |
| webfetch | ✅ 可用 | 访问网页 |

### 适用场景

- ✅ 分析代码架构
- ✅ 制定实现方案
- ✅ 代码审查
- ✅ 学习理解项目
- ✅ 评估技术方案

### 使用示例

```
# Plan 模式下，AI 只会分析和规划
How would you implement a caching system for our API?

# AI 会：
# 1. 分析现有代码结构
# 2. 提出几个可能的方案
# 3. 比较各方案的优缺点
# 4. 给出推荐的实现步骤
#
# 但不会直接改代码！
```

---

## 如何切换 Mode

### 方法 1：Tab 键（最常用）

```
按 Tab 键在 Build 和 Plan 之间切换

┌─────────────────────────────────────┐
│                                     │
│  界面右下角会显示当前模式：          │
│                                     │
│        [Build] 或 [Plan]            │
│                                     │
└─────────────────────────────────────┘
```

### 方法 2：快捷键配置

在 `opencode.json` 中自定义切换键：

```json
{
  "keybinds": {
    "switch_agent": "ctrl+m"
  }
}
```

---

## 推荐工作流：先规划后执行

```
┌─────────────────────────────────────────────────────────────────┐
│                    推荐的工作流程                                │
└─────────────────────────────────────────────────────────────────┘

  步骤 1                   步骤 2                   步骤 3
┌──────────┐            ┌──────────┐            ┌──────────┐
│ Plan 模式 │    Tab    │ 审查方案  │    Tab    │ Build 模式│
│          │ ────────> │          │ ────────> │          │
│ 让 AI 规划│            │ 你来确认  │            │ AI 执行   │
└──────────┘            └──────────┘            └──────────┘

具体操作：

1. 按 Tab 切换到 Plan 模式

2. 描述你的需求：
   "I want to add user authentication to this app"

3. AI 会给出详细的实现方案

4. 你审查方案，可以提出修改意见：
   "Let's use JWT instead of sessions"

5. 满意后按 Tab 切换回 Build 模式

6. 告诉 AI 开始执行：
   "Go ahead and implement the plan"

7. 如果不满意，随时 /undo
```

---

## 自定义 Mode

### 通过 JSON 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "model": "anthropic/claude-sonnet-4",
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "plan": {
      "model": "anthropic/claude-haiku-4",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    }
  }
}
```

### 通过 Markdown 配置

创建 `.opencode/agent/review.md`：

```markdown
---
mode: primary
model: anthropic/claude-sonnet-4
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---

你是代码审查模式。专注于：

- 代码质量和最佳实践
- 潜在的 Bug 和边界情况
- 性能影响
- 安全考虑

提供建设性反馈，不直接修改代码。
```

---

## Mode 配置选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `model` | 使用的 AI 模型 | `"anthropic/claude-sonnet-4"` |
| `temperature` | 创造性程度 (0-1) | `0.1`（更确定），`0.8`（更创造） |
| `tools` | 可用工具配置 | `{"write": false}` |
| `prompt` | 自定义系统提示 | `"{file:./prompts/plan.txt}"` |
| `permission` | 权限配置 | `{"edit": "ask"}` |

### Temperature 参数说明

| 值 | 效果 | 适用场景 |
|-----|------|---------|
| 0.0-0.2 | 非常确定，输出稳定 | 代码分析、规划 |
| 0.3-0.5 | 平衡创造性和确定性 | 日常开发 |
| 0.6-1.0 | 更有创造性，更多变 | 头脑风暴、探索 |

---

## 实用技巧

### 1. 复杂需求先用 Plan

```
# 不好的做法：直接让 Build 模式改
Add a complete authentication system with OAuth, session management,
and role-based access control

# 好的做法：先 Plan 再 Build
<Tab 切换到 Plan>
How would you implement a complete authentication system with OAuth,
session management, and role-based access control?

# 看完方案后
<Tab 切换到 Build>
Let's start with OAuth integration first
```

### 2. 给 Plan 模式配个快模型

Plan 模式不需要执行工具，可以用更快的模型：

```json
{
  "agent": {
    "plan": {
      "model": "anthropic/claude-haiku-4"
    }
  }
}
```

### 3. 创建专门的审查模式

```markdown
---
# .opencode/agent/review.md
mode: primary
tools:
  write: false
  edit: false
  bash: false
---

你是一个严格的代码审查者。

对每个改动：
1. 检查是否有安全漏洞
2. 检查性能问题
3. 检查代码风格
4. 给出改进建议
```

---

## Mode 对比表

| 特性 | Build Mode | Plan Mode |
|------|-----------|-----------|
| 读取文件 | ✅ | ✅ |
| 写入文件 | ✅ | ⚠️ 需确认 |
| 编辑文件 | ✅ | ⚠️ 需确认 |
| 执行命令 | ✅ | ⚠️ 需确认 |
| 搜索文件 | ✅ | ✅ |
| 访问网页 | ✅ | ✅ |
| 适合场景 | 执行改动 | 分析规划 |
| 风险等级 | 较高 | 较低 |

---

## 常见问题

### Q: 什么时候用 Plan 模式？
**A:** 当你想先看看 AI 打算怎么做，再决定是否执行时。特别是复杂的改动。

### Q: Plan 模式能执行命令吗？
**A:** 默认需要你确认才能执行。这是为了安全。

### Q: 可以创建其他模式吗？
**A:** 可以！通过自定义 Agent 实现。见上面的"自定义 Mode"部分。

### Q: Tab 键切换不灵怎么办？
**A:** 可能是快捷键冲突。检查 keybinds 配置，或者换个键：
```json
{
  "keybinds": {
    "switch_agent": "ctrl+m"
  }
}
```

---

## 下一步

- 了解 [MCP Server](./05-mcp.md) 扩展 AI 能力
- 学习 [Command（命令）](./06-command.md) 创建快捷操作
- 查看 [实战案例](./case-add-feature.md)
