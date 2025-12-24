# Config（配置）详解

## 什么是 Config？

**一句话定义**：Config 是 OpenCode 的"设置面板"，用 JSON 文件控制 OpenCode 的各种行为。

### 生活类比

| Config | 类比 |
|--------|------|
| `opencode.json` | 手机的"设置" App |
| 配置项 | 各种开关和选项 |
| Schema | 说明书 |

---

## 配置文件位置

```
┌─────────────────────────────────────────────────────────────────┐
│                     配置文件优先级                               │
└─────────────────────────────────────────────────────────────────┘

  优先级从低到高（后面的会覆盖前面的）：

  1. 全局配置
     ~/.config/opencode/opencode.json
     ├── 应用于所有项目
     └── 存放通用设置（主题、快捷键等）

  2. 项目配置
     ./opencode.json （项目根目录）
     ├── 应用于当前项目
     └── 存放项目特定设置

  3. 环境变量指定
     OPENCODE_CONFIG=/path/to/config.json
     └── 临时覆盖配置
```

---

## 快速开始

### 创建配置文件

```bash
# 在项目根目录创建
touch opencode.json
```

### 基本模板

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4",
  "autoupdate": true
}
```

### 使用 Schema 获得智能提示

在 VS Code 等编辑器中，`$schema` 会提供：
- 自动补全
- 字段验证
- 悬停提示

---

## 完整配置结构

```json
{
  "$schema": "https://opencode.ai/config.json",

  // 基本设置
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4",
  "small_model": "anthropic/claude-haiku-4",
  "autoupdate": true,
  "share": "manual",
  "default_agent": "build",

  // Provider 配置
  "provider": {},
  "disabled_providers": [],
  "enabled_providers": [],

  // Agent 配置
  "agent": {},

  // 工具配置
  "tools": {},
  "permission": {},

  // MCP 配置
  "mcp": {},

  // 命令配置
  "command": {},

  // 快捷键配置
  "keybinds": {},

  // TUI 配置
  "tui": {},

  // 格式化配置
  "formatter": {},

  // 规则文件
  "instructions": []
}
```

---

## 常用配置项详解

### 1. 主题 (theme)

```json
{
  "theme": "opencode"
}
```

可用主题：
- `opencode` - 默认主题
- `catppuccin-latte` - 浅色
- `catppuccin-mocha` - 深色
- 更多主题见 `/docs/themes`

---

### 2. 模型 (model / small_model)

```json
{
  "model": "anthropic/claude-sonnet-4",
  "small_model": "anthropic/claude-haiku-4"
}
```

| 字段 | 用途 |
|------|------|
| `model` | 主要模型，用于复杂任务 |
| `small_model` | 轻量模型，用于标题生成等 |

格式：`provider/model-id`

---

### 3. 自动更新 (autoupdate)

```json
{
  "autoupdate": true
}
```

| 值 | 效果 |
|-----|------|
| `true` | 自动下载更新 |
| `false` | 禁用更新 |
| `"notify"` | 只通知不更新 |

---

### 4. 分享 (share)

```json
{
  "share": "manual"
}
```

| 值 | 效果 |
|-----|------|
| `"manual"` | 需手动执行 /share |
| `"auto"` | 自动分享新对话 |
| `"disabled"` | 完全禁用分享 |

---

### 5. 默认 Agent (default_agent)

```json
{
  "default_agent": "build"
}
```

启动时默认使用的 Agent，必须是 primary agent。

---

### 6. Provider 配置

```json
{
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com"
      }
    }
  },
  "disabled_providers": ["openai"],
  "enabled_providers": ["anthropic", "deepseek"]
}
```

---

### 7. Agent 配置

```json
{
  "agent": {
    "my-agent": {
      "description": "我的自定义 Agent",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4",
      "prompt": "你是一个代码审查专家...",
      "tools": {
        "write": false,
        "edit": false
      },
      "temperature": 0.1
    }
  }
}
```

---

### 8. 工具配置 (tools)

```json
{
  "tools": {
    "write": true,
    "edit": true,
    "bash": true,
    "webfetch": false,
    "mcp_*": false
  }
}
```

全局启用/禁用工具。

---

### 9. 权限配置 (permission)

```json
{
  "permission": {
    "edit": "ask",
    "bash": {
      "rm *": "deny",
      "git push *": "ask",
      "*": "allow"
    },
    "webfetch": "allow"
  }
}
```

| 值 | 效果 |
|-----|------|
| `"allow"` | 自动执行 |
| `"ask"` | 每次询问 |
| `"deny"` | 完全禁止 |

---

### 10. MCP 配置

```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

---

### 11. 命令配置 (command)

```json
{
  "command": {
    "test": {
      "template": "运行测试并分析结果",
      "description": "运行测试"
    }
  }
}
```

---

### 12. 快捷键配置 (keybinds)

```json
{
  "keybinds": {
    "switch_agent": "tab",
    "submit": "enter",
    "cancel": "escape"
  }
}
```

---

### 13. TUI 配置

```json
{
  "tui": {
    "scroll_speed": 3,
    "scroll_acceleration": {
      "enabled": true
    }
  }
}
```

---

### 14. 格式化配置 (formatter)

```json
{
  "formatter": {
    "prettier": {
      "disabled": false
    },
    "custom": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "extensions": [".js", ".ts", ".tsx"]
    }
  }
}
```

---

### 15. 规则文件 (instructions)

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md"
  ]
}
```

指定额外的规则文件，AI 会读取这些文件作为上下文。

---

## 变量替换

### 环境变量

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```

### 文件内容

```json
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

---

## 配置示例

### 最小配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4"
}
```

### 安全配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

### 开发者配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "catppuccin-mocha",
  "model": "anthropic/claude-sonnet-4",
  "small_model": "anthropic/claude-haiku-4",
  "autoupdate": true,
  "permission": {
    "edit": "allow",
    "bash": {
      "rm -rf *": "deny",
      "git push --force *": "ask",
      "*": "allow"
    }
  },
  "command": {
    "test": {
      "template": "npm test",
      "description": "运行测试"
    }
  },
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

### 团队共享配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "CONTRIBUTING.md",
    "CODE_STYLE.md"
  ],
  "command": {
    "lint": {
      "template": "npm run lint && 分析 lint 结果",
      "description": "运行代码检查"
    },
    "pr": {
      "template": "创建 PR 并填写描述",
      "description": "创建 Pull Request"
    }
  },
  "agent": {
    "reviewer": {
      "description": "代码审查",
      "mode": "subagent",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

---

## 配置调试

### 检查配置是否加载

```bash
# 查看当前使用的配置
opencode config
```

### 验证 JSON 语法

使用 VS Code 或其他编辑器，`$schema` 会自动验证。

### 常见错误

1. **JSON 语法错误**
   - 检查逗号、引号
   - 最后一项不要加逗号

2. **文件位置错误**
   - 确保在项目根目录
   - 文件名是 `opencode.json`

3. **Schema 不生效**
   - 检查 `$schema` URL 是否正确

---

## JSONC 支持

OpenCode 支持 JSONC（带注释的 JSON）：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // 使用 Claude Sonnet 作为主模型
  "model": "anthropic/claude-sonnet-4",

  /* 权限配置
     - edit: 编辑权限
     - bash: 命令权限
  */
  "permission": {
    "edit": "ask",  // 每次编辑都询问
    "bash": "allow" // 自动执行命令
  }
}
```

文件扩展名用 `.jsonc`：`opencode.jsonc`

---

## 常见问题

### Q: 项目配置和全局配置冲突怎么办？
**A:** 项目配置优先。两者会深度合并，冲突的键以项目配置为准。

### Q: 如何查看当前生效的配置？
**A:** 运行 `opencode config` 查看。

### Q: 配置改了不生效？
**A:**
1. 检查 JSON 语法
2. 重启 OpenCode
3. 确认文件位置正确

### Q: 可以用 YAML 吗？
**A:** 不行，只支持 JSON 和 JSONC。

---

## 下一步

- 了解 [Permission（权限）](./08-permission.md) 精细控制
- 查看 [实战案例](./case-add-feature.md)
