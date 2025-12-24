# MCP Server 详解

## 什么是 MCP？

**一句话定义**：MCP（Model Context Protocol）是给 AI 装"外挂"的协议，让 AI 能调用外部服务。

### 生活类比

| 概念 | 类比 |
|------|------|
| AI（无 MCP） | 只会说话的助手 |
| AI + MCP | 能打电话、发邮件、查数据库的超级助手 |
| MCP Server | 一个个"外挂技能" |

想象 AI 是一个聪明的大脑，MCP 就是给它接上了各种"接口"：
- 数据库接口 → 能查数据库
- GitHub 接口 → 能操作 GitHub
- 文档搜索接口 → 能搜索在线文档

---

## MCP 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                       MCP 工作原理                               │
└─────────────────────────────────────────────────────────────────┘

           ┌─────────────────────────────────────────┐
           │              OpenCode                    │
           │                                          │
           │  ┌────────────────────────────────────┐ │
           │  │         内置工具 (Tools)            │ │
           │  │  read | write | edit | bash | ...  │ │
           │  └────────────────────────────────────┘ │
           │                    +                     │
           │  ┌────────────────────────────────────┐ │
           │  │         MCP 工具 (扩展)             │ │
           │  │                                    │ │
           │  │  ┌──────────┐ ┌──────────┐        │ │
           │  │  │ 本地 MCP │ │ 远程 MCP │        │ │
           │  │  └────┬─────┘ └────┬─────┘        │ │
           │  └───────┼────────────┼──────────────┘ │
           │          │            │                 │
           └──────────┼────────────┼─────────────────┘
                      │            │
                      ▼            ▼
              ┌───────────┐  ┌───────────┐
              │ 本地服务   │  │ 云端服务   │
              │           │  │           │
              │ • 数据库   │  │ • 文档搜索 │
              │ • 文件系统 │  │ • API调用  │
              │ • 自定义   │  │ • 第三方   │
              └───────────┘  └───────────┘
```

---

## 两种 MCP 类型

### 本地 MCP（Local）

运行在你电脑上的服务。

**优点**：
- 安全，数据不出本机
- 可以访问本地资源

**适用场景**：
- 本地数据库访问
- 本地文件处理
- 自定义工具

### 远程 MCP（Remote）

运行在云端的服务。

**优点**：
- 无需本地安装
- 功能更丰富

**适用场景**：
- 在线文档搜索
- 第三方 API 调用
- 共享服务

---

## 快速开始

### 添加远程 MCP

最简单的方式，不需要安装任何东西：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

现在你可以这样使用：
```
use context7 to search React hooks documentation
```

### 添加本地 MCP

需要安装 Node.js：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "mcp_everything": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"]
    }
  }
}
```

---

## 常用 MCP Server

### Context7 - 文档搜索

**功能**：搜索各种技术文档

**配置**：
```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

**使用**：
```
use context7 to find how to configure Next.js middleware
```

---

### Grep by Vercel - 代码搜索

**功能**：在 GitHub 上搜索代码片段

**配置**：
```json
{
  "mcp": {
    "gh_grep": {
      "type": "remote",
      "url": "https://mcp.grep.app"
    }
  }
}
```

**使用**：
```
use gh_grep to find examples of implementing OAuth in Express.js
```

---

## 配置详解

### 本地 MCP 配置

```json
{
  "mcp": {
    "my-local-mcp": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-package"],
      "enabled": true,
      "environment": {
        "MY_API_KEY": "xxx"
      },
      "timeout": 5000
    }
  }
}
```

| 选项 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 必须是 `"local"` |
| `command` | ✅ | 启动命令，数组格式 |
| `enabled` | ❌ | 是否启用，默认 true |
| `environment` | ❌ | 环境变量 |
| `timeout` | ❌ | 超时时间（毫秒），默认 5000 |

### 远程 MCP 配置

```json
{
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://api.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      },
      "timeout": 5000
    }
  }
}
```

| 选项 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 必须是 `"remote"` |
| `url` | ✅ | MCP 服务地址 |
| `enabled` | ❌ | 是否启用 |
| `headers` | ❌ | HTTP 请求头 |
| `oauth` | ❌ | OAuth 认证配置 |
| `timeout` | ❌ | 超时时间 |

---

## 管理 MCP 工具

### 全局禁用 MCP 工具

```json
{
  "mcp": {
    "my-mcp": {
      "type": "remote",
      "url": "https://..."
    }
  },
  "tools": {
    "my-mcp*": false
  }
}
```

### 按 Agent 启用

```json
{
  "mcp": {
    "my-mcp": {
      "type": "local",
      "command": ["..."],
      "enabled": true
    }
  },
  "tools": {
    "my-mcp*": false
  },
  "agent": {
    "researcher": {
      "tools": {
        "my-mcp*": true
      }
    }
  }
}
```

这样只有 `researcher` Agent 能用这个 MCP。

---

## OAuth 认证

### 自动 OAuth

大多数远程 MCP 会自动处理认证：

```json
{
  "mcp": {
    "my-oauth-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

首次使用时会弹出浏览器让你登录。

### 手动认证

```bash
# 认证
opencode mcp auth my-oauth-server

# 查看所有 MCP 状态
opencode mcp list

# 登出
opencode mcp logout my-oauth-server
```

### 禁用 OAuth（使用 API Key）

```json
{
  "mcp": {
    "my-api-key-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

---

## 注意事项

### 1. Context 限制

MCP 会占用 AI 的上下文空间。

```
⚠️ 警告：
MCP 工具越多，可用于代码分析的上下文就越少！
```

**建议**：
- 只启用需要的 MCP
- 不用时禁用 MCP
- 使用 "按 Agent 启用" 方式

### 2. 性能考虑

- 远程 MCP 有网络延迟
- 本地 MCP 需要启动时间
- 设置合理的 timeout

### 3. 安全考虑

- API Key 不要硬编码，用 `{env:VAR}` 引用
- 本地 MCP 要注意命令注入风险
- 远程 MCP 注意数据隐私

---

## 实用技巧

### 1. 在 AGENTS.md 中说明

```markdown
# AGENTS.md

当需要搜索文档时，使用 `context7` 工具。
当需要查找代码示例时，使用 `gh_grep` 工具。
```

这样 AI 会自动知道什么时候用什么工具。

### 2. 组合使用

```
# 先用 context7 找文档
use context7 to find Next.js App Router documentation

# 再用 gh_grep 找实际代码
use gh_grep to find examples of Next.js App Router in open source projects

# 最后让 AI 结合两者来实现
Based on the documentation and examples, implement a similar routing structure
```

### 3. 临时禁用

```json
{
  "mcp": {
    "heavy-mcp": {
      "type": "remote",
      "url": "...",
      "enabled": false
    }
  }
}
```

---

## 常见问题

### Q: MCP 和内置工具有什么区别？
**A:** 内置工具是 OpenCode 自带的（如 read、write），MCP 是外部扩展的。内置工具处理本地操作，MCP 可以连接外部服务。

### Q: MCP 会让 AI 变慢吗？
**A:** 可能会：
1. 占用更多 context 空间
2. 网络请求有延迟

建议只启用需要的 MCP。

### Q: 我能自己写 MCP Server 吗？
**A:** 可以！MCP 是开放协议。查看 [MCP 官方文档](https://modelcontextprotocol.io/) 了解如何开发。

### Q: MCP 安全吗？
**A:** 取决于具体的 MCP Server：
- 官方和知名的 MCP 通常可信
- 第三方 MCP 需要自行评估
- 本地 MCP 更安全，但也要注意代码来源

---

## 下一步

- 学习 [Command（命令）](./06-command.md) 创建快捷操作
- 了解 [Config（配置）](./07-config.md) 完整配置
- 查看 [实战案例](./case-add-feature.md)
