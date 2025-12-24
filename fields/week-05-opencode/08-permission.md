# Permission（权限）详解

## 什么是 Permission？

**一句话定义**：Permission 决定 AI 在执行危险操作前是否需要你确认。

### 生活类比

| 权限级别 | 类比 |
|---------|------|
| `allow` | 给助手一张全权委托书 |
| `ask` | 每次转账都要你签字 |
| `deny` | 这个抽屉不许碰 |

---

## 权限全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                     权限控制体系                                 │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │      AI 请求操作     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     检查权限配置     │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   allow     │    │    ask      │    │    deny     │
    │             │    │             │    │             │
    │  直接执行    │    │  弹窗询问   │    │  拒绝执行    │
    │             │    │             │    │             │
    │  ┌───────┐  │    │  ┌───────┐  │    │  ┌───────┐  │
    │  │ ✅ 执行│  │    │  │ 确认？ │  │    │  │ ❌ 拒绝│  │
    │  └───────┘  │    │  └───┬───┘  │    │  └───────┘  │
    │             │    │      │      │    │             │
    └─────────────┘    │   是 │ 否   │    └─────────────┘
                       │      ▼      │
                       │  ✅ 执行    │
                       │  或 ❌ 取消  │
                       └─────────────┘
```

---

## 可控制的操作

| 操作 | 说明 | 风险等级 |
|------|------|---------|
| `edit` | 编辑/写入文件 | 中 |
| `bash` | 执行 Shell 命令 | 高 |
| `webfetch` | 访问网络 | 低 |
| `external_directory` | 访问项目外目录 | 中 |
| `doom_loop` | 连续多次执行 | 中 |

---

## 权限级别

### allow - 允许

```json
{
  "permission": {
    "edit": "allow"
  }
}
```

- AI 直接执行，不询问
- 适合你信任的操作
- 效率最高

### ask - 询问

```json
{
  "permission": {
    "edit": "ask"
  }
}
```

- 每次执行前弹窗询问
- 你可以查看具体操作内容
- 选择允许或拒绝

### deny - 拒绝

```json
{
  "permission": {
    "bash": "deny"
  }
}
```

- 完全禁止该操作
- AI 会被告知无法执行
- 最安全

---

## 基本配置

### 全局权限

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

### 按 Agent 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "allow"
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny"
      }
    }
  }
}
```

Agent 级别的配置会覆盖全局配置。

---

## Bash 命令精细控制

Bash 权限支持按命令模式配置：

### 基本语法

```json
{
  "permission": {
    "bash": {
      "命令模式": "权限级别"
    }
  }
}
```

### 通配符

| 模式 | 匹配 |
|------|------|
| `*` | 任意字符（零个或多个） |
| `?` | 任意单个字符 |

### 示例

```json
{
  "permission": {
    "bash": {
      "git status": "allow",
      "git log*": "allow",
      "git diff*": "allow",
      "git push*": "ask",
      "git push --force*": "deny",
      "rm -rf *": "deny",
      "npm test": "allow",
      "npm run *": "ask",
      "*": "ask"
    }
  }
}
```

### 优先级规则

更具体的规则优先于通配符规则：

```json
{
  "permission": {
    "bash": {
      "git status": "allow",     // 具体命令，最高优先级
      "git *": "ask",            // 带通配符
      "*": "deny"                // 全局通配符，最低优先级
    }
  }
}
```

执行 `git status` → 匹配第一条 → `allow`
执行 `git push` → 匹配第二条 → `ask`
执行 `rm -rf /` → 匹配第三条 → `deny`

---

## 实用配置方案

### 1. 保守方案（新手推荐）

```json
{
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "ask"
  }
}
```

每个操作都需确认，最安全但效率较低。

### 2. 平衡方案（日常开发）

```json
{
  "permission": {
    "edit": "allow",
    "bash": {
      "git status": "allow",
      "git log*": "allow",
      "git diff*": "allow",
      "npm test*": "allow",
      "npm run lint*": "allow",
      "rm -rf *": "deny",
      "*": "ask"
    },
    "webfetch": "allow"
  }
}
```

### 3. 开放方案（信任 AI）

```json
{
  "permission": {
    "edit": "allow",
    "bash": {
      "rm -rf /": "deny",
      "rm -rf ~": "deny",
      "rm -rf /*": "deny",
      "sudo *": "ask",
      "git push --force *": "ask",
      "*": "allow"
    },
    "webfetch": "allow"
  }
}
```

### 4. 只读方案（代码审查）

```json
{
  "permission": {
    "edit": "deny",
    "bash": {
      "git status": "allow",
      "git log*": "allow",
      "git diff*": "allow",
      "cat *": "allow",
      "ls *": "allow",
      "*": "deny"
    },
    "webfetch": "allow"
  }
}
```

---

## 在 Agent 中使用

### Markdown Agent 配置

```markdown
---
# .opencode/agent/safe-coder.md
description: 安全编码代理
mode: subagent
permission:
  edit: ask
  bash:
    "git diff": allow
    "git log*": allow
    "*": ask
  webfetch: deny
---

你是一个安全的编码助手。
```

### JSON Agent 配置

```json
{
  "agent": {
    "safe-coder": {
      "description": "安全编码代理",
      "mode": "subagent",
      "permission": {
        "edit": "ask",
        "bash": {
          "git diff": "allow",
          "git log*": "allow",
          "*": "ask"
        }
      }
    }
  }
}
```

---

## 权限继承关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     权限继承链                                   │
└─────────────────────────────────────────────────────────────────┘

  全局配置 (opencode.json)
     │
     │  permission: { edit: "allow", bash: "*": "ask" }
     │
     ▼
  Agent 配置
     │
     │  plan.permission: { edit: "deny" }
     │
     ▼
  最终权限
     │
     │  edit: "deny" (被 Agent 覆盖)
     │  bash: "*": "ask" (继承全局)
     │
     └───────────────────────────────────────
```

---

## 交互体验

### 询问弹窗

当权限设为 `ask` 时：

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  OpenCode 请求执行以下操作：                                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  bash: npm install lodash                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [允许]  [拒绝]  [始终允许此命令]                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 被拒绝的反馈

当权限设为 `deny` 时：

```
AI 会收到提示：
"bash 工具已被禁用，无法执行命令。"

AI 可能会：
- 解释它想做什么
- 请求你手动执行
- 尝试其他方法
```

---

## 安全建议

### 1. 危险命令一定要禁止

```json
{
  "permission": {
    "bash": {
      "rm -rf /": "deny",
      "rm -rf /*": "deny",
      "rm -rf ~": "deny",
      "sudo rm -rf *": "deny",
      "> /dev/sda": "deny"
    }
  }
}
```

### 2. 敏感操作需要确认

```json
{
  "permission": {
    "bash": {
      "git push*": "ask",
      "npm publish*": "ask",
      "docker push*": "ask"
    }
  }
}
```

### 3. 项目外目录要谨慎

```json
{
  "permission": {
    "external_directory": "ask"
  }
}
```

### 4. 新项目先用保守配置

初次在一个项目使用 OpenCode，先用 `ask` 观察一段时间。

---

## 常见问题

### Q: 权限弹窗太烦了怎么办？
**A:** 根据你的使用习惯，把常用安全命令设为 `allow`：
```json
{
  "bash": {
    "npm test": "allow",
    "npm run lint": "allow",
    "git status": "allow"
  }
}
```

### Q: AI 说它不能执行某个操作？
**A:** 检查是否被 `deny` 了。查看配置文件中的权限设置。

### Q: 权限设置不生效？
**A:**
1. 检查 JSON 语法
2. 检查是否被 Agent 级配置覆盖
3. 重启 OpenCode

### Q: 如何临时允许一个被禁止的操作？
**A:** 你需要修改配置文件。或者让 AI 告诉你命令，你手动执行。

### Q: 多个 bash 规则冲突时谁优先？
**A:** 更具体的规则优先。`git status` 比 `git *` 优先，`git *` 比 `*` 优先。

---

## 下一步

- 查看 [实战案例](./case-add-feature.md) 综合运用所学
- 回顾 [Config（配置）](./07-config.md) 完整配置
- 了解 [Agent（代理）](./01-agent.md) 自定义代理
