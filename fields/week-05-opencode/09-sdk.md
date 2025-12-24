# SDK/API 详解

## 什么是 SDK/API？

**一句话定义**：SDK/API 让你可以通过代码程序化控制 OpenCode，实现自动化和集成开发。

### 生活类比

| 概念 | 类比 |
|------|------|
| OpenCode Server | 外卖平台的后台系统 |
| SDK | 外卖平台官方提供的 App SDK |
| HTTP API | 直接调用外卖平台的接口 |
| TUI | 外卖 App 的用户界面 |

---

## 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenCode 架构                                │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   终端 TUI    │  │  VS Code     │  │  自定义客户端 │
│  (官方界面)   │  │   插件       │  │  (你开发的)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │      HTTP/SSE   │                 │
       └────────────────┬┴─────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   OpenCode Server   │
              │   (localhost:4096)  │
              │                     │
              │  - 会话管理          │
              │  - AI 对话          │
              │  - 文件操作          │
              │  - 工具执行          │
              └─────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   LLM Provider      │
              │ (Anthropic/OpenAI)  │
              └─────────────────────┘
```

**核心理念**：当你运行 `opencode` 时，实际启动了两个东西：
1. **Server** - 后台 HTTP 服务（默认端口 4096）
2. **TUI** - 终端用户界面（作为 Server 的一个客户端）

这种架构让你可以：
- 同时有多个客户端连接
- 程序化控制 OpenCode
- 构建自己的 UI

---

## 快速开始

### 安装 SDK

```bash
npm install @opencode-ai/sdk
```

### 方式一：创建完整实例（Server + Client）

```typescript
import { createOpencode } from "@opencode-ai/sdk"

const { client, server } = await createOpencode({
  hostname: "127.0.0.1",
  port: 4096,
  config: {
    model: "anthropic/claude-sonnet-4",
  },
})

console.log(`Server running at ${server.url}`)

// 使用 client 进行操作...

// 使用完毕后关闭
server.close()
```

### 方式二：连接已有 Server

```typescript
import { createOpencodeClient } from "@opencode-ai/sdk"

// 假设你已经在终端运行了 opencode
const client = createOpencodeClient({
  baseUrl: "http://localhost:4096",
})
```

### 方式三：直接启动 Server（无 TUI）

```bash
# 启动无头服务
opencode serve --port 4096 --hostname 127.0.0.1
```

---

## 核心 API 分类

### 1. 会话管理 (Session)

| 方法 | 说明 |
|------|------|
| `session.create({ body })` | 创建新会话 |
| `session.list()` | 列出所有会话 |
| `session.get({ path })` | 获取会话详情 |
| `session.delete({ path })` | 删除会话 |
| `session.abort({ path })` | 中止运行中的会话 |
| `session.share({ path })` | 分享会话 |
| `session.fork({ path, body })` | 分叉会话 |

```typescript
// 创建会话
const session = await client.session.create({
  body: { title: "My session" },
})

// 发送消息并获取 AI 响应
const result = await client.session.prompt({
  path: { id: session.data.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-sonnet-4" },
    parts: [{ type: "text", text: "Hello!" }],
  },
})
```

### 2. 文件操作 (File)

| 方法 | 说明 |
|------|------|
| `find.text({ query })` | 搜索文件内容 |
| `find.files({ query })` | 按名称查找文件 |
| `find.symbols({ query })` | 查找代码符号 |
| `file.read({ query })` | 读取文件内容 |
| `file.status()` | 获取文件状态 |

```typescript
// 搜索文件内容
const results = await client.find.text({
  query: { pattern: "function.*opencode" },
})

// 读取文件
const content = await client.file.read({
  query: { path: "src/index.ts" },
})
```

### 3. 实时事件 (Event)

```typescript
// 订阅服务器事件流 (SSE)
const events = await client.event.subscribe()

for await (const event of events.stream) {
  switch (event.type) {
    case 'message.created':
      console.log('新消息')
      break
    case 'tool.started':
      console.log('工具开始执行:', event.properties.name)
      break
    case 'tool.completed':
      console.log('工具完成')
      break
  }
}
```

### 4. TUI 控制

| 方法 | 说明 |
|------|------|
| `tui.appendPrompt({ body })` | 向输入框追加文字 |
| `tui.submitPrompt()` | 提交当前输入 |
| `tui.clearPrompt()` | 清空输入框 |
| `tui.showToast({ body })` | 显示通知 |
| `tui.executeCommand({ body })` | 执行斜杠命令 |

```typescript
// 向 TUI 输入框追加文本
await client.tui.appendPrompt({
  body: { text: "帮我分析这段代码" },
})

// 提交
await client.tui.submitPrompt()

// 显示 Toast 通知
await client.tui.showToast({
  body: { message: "任务完成", variant: "success" },
})
```

---

## 关键概念：noReply

### 什么是 noReply？

当调用 `session.prompt()` 时：

| 模式 | 效果 |
|------|------|
| `noReply: false`（默认） | 发送消息 → AI 生成响应 |
| `noReply: true` | 发送消息 → 只加入对话历史，AI 不响应 |

### 为什么需要 noReply？

**场景：预注入上下文**

```typescript
// 插件先注入当前文件内容（不触发 AI）
await client.session.prompt({
  path: { id: sessionId },
  body: {
    noReply: true,
    parts: [{ type: "text", text: `当前文件内容:\n${fileContent}` }],
  },
})

// 用户后续提问时，AI 已经知道文件内容了
await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "这个函数有什么问题？" }],
  },
})
```

**好处**：
- 节省 API 调用次数
- 降低成本
- 让 AI 拥有更多上下文

### 类比理解

| 模式 | 类比 |
|------|------|
| `noReply: false` | 发微信消息，等对方回复 |
| `noReply: true` | 在群里发个文件，不需要别人回应，只是让大家知道 |

---

## 四大应用场景

### 场景一：IDE 集成

**目标**：让用户在 IDE 中无缝使用 OpenCode，无需切换到终端。

```
┌─────────────────────────────────────────────────────────────┐
│                        VS Code                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │ 代码编辑器  │    │ 右键菜单    │    │ OpenCode 面板   │  │
│  │             │    │ - Ask AI    │    │                 │  │
│  │  [选中代码] │───►│ - Fix Bug   │───►│  [AI 回复]      │  │
│  │             │    │ - Explain   │    │                 │  │
│  └─────────────┘    └─────────────┘    └────────┬────────┘  │
└────────────────────────────────────────────────┬────────────┘
                                                  │ HTTP
                                                  ▼
                                    ┌─────────────────────────┐
                                    │    OpenCode Server      │
                                    └─────────────────────────┘
```

#### VS Code 插件示例

```typescript
// extension.ts - VS Code 插件入口

import * as vscode from 'vscode'
import { createOpencodeClient } from '@opencode-ai/sdk'

let client: ReturnType<typeof createOpencodeClient>

export function activate(context: vscode.ExtensionContext) {
  // 连接到 OpenCode Server
  client = createOpencodeClient({
    baseUrl: 'http://localhost:4096'
  })

  // 注册命令：解释选中代码
  context.subscriptions.push(
    vscode.commands.registerCommand('opencode.explainCode', async () => {
      const editor = vscode.window.activeTextEditor
      if (!editor) return

      const selection = editor.document.getText(editor.selection)
      const fileName = editor.document.fileName

      // 方式1：直接驱动 TUI（终端界面同步显示）
      await client.tui.appendPrompt({
        body: { 
          text: `请解释 ${fileName} 中的这段代码:\n\`\`\`\n${selection}\n\`\`\`` 
        }
      })
      await client.tui.submitPrompt()
    })
  )

  // 注册命令：修复 Bug（直接调用 Session API）
  context.subscriptions.push(
    vscode.commands.registerCommand('opencode.fixBug', async () => {
      const editor = vscode.window.activeTextEditor
      if (!editor) return

      const selection = editor.document.getText(editor.selection)
      
      // 方式2：直接调用 Session API（不经过 TUI）
      const session = await client.session.create({
        body: { title: 'Fix Bug from VS Code' }
      })

      const result = await client.session.prompt({
        path: { id: session.data.id },
        body: {
          parts: [{ 
            type: 'text', 
            text: `修复这段代码中的 bug:\n\`\`\`\n${selection}\n\`\`\`` 
          }]
        }
      })

      // 在 VS Code 中显示结果
      vscode.window.showInformationMessage('修复建议已生成')
    })
  )
}
```

#### 实时事件同步

```typescript
// 监听 OpenCode 事件，在 IDE 中实时显示进度
async function subscribeToEvents(sessionId: string) {
  const events = await client.event.subscribe()
  
  for await (const event of events.stream) {
    switch (event.type) {
      case 'message.created':
        updatePanel(event.properties)
        break
      
      case 'message.updated':
        // AI 正在生成，流式更新
        appendToPanel(event.properties.content)
        break
      
      case 'tool.started':
        showStatus(`执行中: ${event.properties.toolName}`)
        break
      
      case 'tool.completed':
        showStatus(`完成: ${event.properties.toolName}`)
        break
    }
  }
}
```

---

### 场景二：CI/CD 自动化

**目标**：在代码提交或 PR 时自动执行 AI 代码审查。

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   GitHub    │────►│  CI Runner  │────►│ OpenCode Server │
│   PR/Push   │     │  (Actions)  │     │   (Headless)    │
└─────────────┘     └──────┬──────┘     └────────┬────────┘
                           │                      │
                           │◄─────────────────────┘
                           │    Review Results
                           ▼
                    ┌─────────────┐
                    │ PR Comment  │
                    └─────────────┘
```

#### GitHub Actions 配置

```yaml
# .github/workflows/ai-review.yml

name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install OpenCode
        run: npm install -g opencode-ai

      - name: Start OpenCode Server
        run: |
          opencode serve --port 4096 &
          sleep 3
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Run AI Review
        run: node .github/scripts/ai-review.js
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
```

#### 审查脚本

```typescript
// .github/scripts/ai-review.js

import { createOpencodeClient } from '@opencode-ai/sdk'
import { execSync } from 'child_process'

const client = createOpencodeClient({
  baseUrl: 'http://localhost:4096'
})

async function runReview() {
  // 1. 获取 PR 的 diff
  const diff = execSync('git diff origin/main...HEAD').toString()
  
  // 2. 获取变更的文件列表
  const changedFiles = execSync('git diff --name-only origin/main...HEAD')
    .toString()
    .split('\n')
    .filter(Boolean)

  // 3. 创建审查会话
  const session = await client.session.create({
    body: { title: `PR #${process.env.PR_NUMBER} Review` }
  })

  // 4. 注入审查规范（不触发响应）
  await client.session.prompt({
    path: { id: session.data.id },
    body: {
      noReply: true,
      parts: [{ 
        type: 'text', 
        text: `你是一个严格的代码审查员。请检查以下方面：
1. 代码质量和可读性
2. 潜在的 Bug 和边界情况
3. 性能问题
4. 安全漏洞
5. 是否符合项目规范

输出格式：
## 总体评价
[概述]

## 问题列表
- **严重**: [问题描述] (文件:行号)
- **建议**: [改进建议] (文件:行号)

## 优点
[值得肯定的地方]` 
      }]
    }
  })

  // 5. 发送 diff 进行审查
  const result = await client.session.prompt({
    path: { id: session.data.id },
    body: {
      parts: [{ 
        type: 'text', 
        text: `请审查以下代码变更：

变更文件: ${changedFiles.join(', ')}

\`\`\`diff
${diff}
\`\`\`` 
      }]
    }
  })

  // 6. 提取审查结果并发布到 GitHub PR
  const reviewContent = extractTextContent(result.data)
  await postGitHubComment(reviewContent)

  // 7. 根据审查结果决定是否通过
  if (reviewContent.includes('**严重**')) {
    console.log('发现严重问题')
    process.exit(1)  // CI 失败
  }
}

async function postGitHubComment(content: string) {
  await fetch(
    `https://api.github.com/repos/${process.env.GITHUB_REPOSITORY}/issues/${process.env.PR_NUMBER}/comments`,
    {
      method: 'POST',
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        body: `## AI Code Review\n\n${content}`
      })
    }
  )
}

runReview()
```

---

### 场景三：自定义客户端

**目标**：构建自己的 AI 编程助手界面，完全定制 UI/UX。

```
┌─────────────────────────────────────────────────────────┐
│                    自定义 Web 客户端                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   对话面板   │  │  文件浏览器  │  │    代码编辑器   │  │
│  │             │  │             │  │                 │  │
│  │  [消息列表]  │  │  [项目结构]  │  │  [Monaco Editor]│  │
│  │  [输入框]   │  │             │  │                 │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP/SSE
                             ▼
                  ┌─────────────────────┐
                  │   OpenCode Server   │
                  └─────────────────────┘
```

#### React Hook 封装

```typescript
// hooks/useOpenCode.ts

import { createOpencodeClient } from '@opencode-ai/sdk'
import { useState, useEffect, useCallback } from 'react'

const client = createOpencodeClient({
  baseUrl: 'http://localhost:4096'
})

export function useOpenCode() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // 加载会话列表
  useEffect(() => {
    client.session.list().then(res => setSessions(res.data))
  }, [])

  // 创建新会话
  const createSession = useCallback(async (title: string) => {
    const res = await client.session.create({ body: { title } })
    setCurrentSession(res.data)
    setSessions(prev => [...prev, res.data])
    setMessages([])
    return res.data
  }, [])

  // 发送消息
  const sendMessage = useCallback(async (text: string) => {
    if (!currentSession) return

    setIsLoading(true)
    
    // 乐观更新：先显示用户消息
    const userMessage = { role: 'user', content: text, id: Date.now().toString() }
    setMessages(prev => [...prev, userMessage])

    try {
      const res = await client.session.prompt({
        path: { id: currentSession.id },
        body: {
          parts: [{ type: 'text', text }]
        }
      })

      // 添加 AI 响应
      const assistantMessage = {
        role: 'assistant',
        content: extractContent(res.data),
        id: res.data.info.id
      }
      setMessages(prev => [...prev, assistantMessage])
    } finally {
      setIsLoading(false)
    }
  }, [currentSession])

  // 中止当前请求
  const abort = useCallback(async () => {
    if (!currentSession) return
    await client.session.abort({ path: { id: currentSession.id } })
    setIsLoading(false)
  }, [currentSession])

  return {
    sessions,
    currentSession,
    messages,
    isLoading,
    createSession,
    sendMessage,
    abort,
    setCurrentSession
  }
}
```

#### 流式响应处理

```typescript
// hooks/useStreamingChat.ts

export function useStreamingChat(sessionId: string) {
  const [streamingContent, setStreamingContent] = useState('')
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([])

  useEffect(() => {
    let cancelled = false

    async function subscribe() {
      const events = await client.event.subscribe()
      
      for await (const event of events.stream) {
        if (cancelled) break

        switch (event.type) {
          case 'part.updated':
            // AI 正在生成文本，流式更新
            if (event.properties.sessionId === sessionId) {
              setStreamingContent(prev => prev + event.properties.delta)
            }
            break

          case 'tool.started':
            setToolCalls(prev => [...prev, {
              id: event.properties.id,
              name: event.properties.name,
              status: 'running',
              args: event.properties.args
            }])
            break

          case 'tool.completed':
            setToolCalls(prev => prev.map(t => 
              t.id === event.properties.id 
                ? { ...t, status: 'completed', result: event.properties.result }
                : t
            ))
            break

          case 'message.completed':
            setStreamingContent('')
            break
        }
      }
    }

    subscribe()
    return () => { cancelled = true }
  }, [sessionId])

  return { streamingContent, toolCalls }
}
```

#### 聊天组件

```tsx
// components/Chat.tsx

import { useOpenCode } from '../hooks/useOpenCode'
import { useStreamingChat } from '../hooks/useStreamingChat'

export function Chat() {
  const { 
    messages, 
    currentSession, 
    sendMessage, 
    isLoading,
    abort 
  } = useOpenCode()
  
  const { streamingContent, toolCalls } = useStreamingChat(currentSession?.id)
  const [input, setInput] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return
    sendMessage(input)
    setInput('')
  }

  return (
    <div className="chat-container">
      {/* 消息列表 */}
      <div className="messages">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {/* 流式生成中的内容 */}
        {streamingContent && (
          <div className="streaming-message">
            <Markdown>{streamingContent}</Markdown>
            <span className="cursor-blink">▋</span>
          </div>
        )}

        {/* 工具执行状态 */}
        {toolCalls.map(tool => (
          <ToolCallCard key={tool.id} tool={tool} />
        ))}
      </div>

      {/* 输入框 */}
      <form onSubmit={handleSubmit} className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="输入消息..."
          disabled={isLoading}
        />
        {isLoading ? (
          <button type="button" onClick={abort}>停止</button>
        ) : (
          <button type="submit">发送</button>
        )}
      </form>
    </div>
  )
}
```

---

### 场景四：批量处理

**目标**：批量分析代码库、执行重复任务、生成报告。

#### 代码库健康检查

```typescript
// scripts/codebase-health-check.ts

import { createOpencode } from '@opencode-ai/sdk'
import { glob } from 'glob'
import * as fs from 'fs'

async function healthCheck() {
  const { client } = await createOpencode()
  
  // 创建分析会话
  const session = await client.session.create({
    body: { title: 'Codebase Health Check' }
  })

  // 注入分析标准
  await client.session.prompt({
    path: { id: session.data.id },
    body: {
      noReply: true,
      parts: [{ 
        type: 'text', 
        text: `你是代码质量分析师。请分析代码并给出评分：

评分维度（每项 1-10 分）：
- 可读性：命名、注释、结构
- 可维护性：模块化、耦合度
- 健壮性：错误处理、边界检查
- 性能：明显的性能问题
- 安全性：潜在的安全漏洞

输出 JSON 格式：
{
  "file": "文件路径",
  "scores": { "可读性": 8, "可维护性": 7, ... },
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}` 
      }]
    }
  })

  // 获取所有源文件
  const files = await glob('src/**/*.{ts,tsx,js,jsx}')
  const results = []

  console.log(`开始分析 ${files.length} 个文件...`)

  for (const file of files) {
    console.log(`分析: ${file}`)
    
    const content = fs.readFileSync(file, 'utf-8')
    
    // 跳过太小的文件
    if (content.length < 100) continue

    const result = await client.session.prompt({
      path: { id: session.data.id },
      body: {
        parts: [{ 
          type: 'text', 
          text: `分析文件: ${file}\n\n\`\`\`\n${content}\n\`\`\`` 
        }]
      }
    })

    try {
      const analysis = JSON.parse(extractContent(result.data))
      results.push(analysis)
    } catch {
      console.warn(`解析失败: ${file}`)
    }

    // 避免 API 限流
    await sleep(1000)
  }

  // 生成汇总报告
  const report = generateReport(results)
  fs.writeFileSync('health-report.md', report)
  
  console.log('分析完成! 报告已保存到 health-report.md')
}

healthCheck()
```

#### 批量重构

```typescript
// scripts/batch-refactor.ts

async function batchRefactor() {
  const { client } = await createOpencode()
  
  // 查找所有使用旧 API 的文件
  const searchResult = await client.find.text({
    query: { pattern: 'oldApiMethod\\(' }
  })

  const session = await client.session.create({
    body: { title: 'Batch Refactor: API Migration' }
  })

  // 注入重构规则
  await client.session.prompt({
    path: { id: session.data.id },
    body: {
      noReply: true,
      parts: [{ 
        type: 'text', 
        text: `重构规则：
1. oldApiMethod(arg1, arg2) → newApi.method({ first: arg1, second: arg2 })
2. 保持原有的错误处理逻辑
3. 添加类型注解
4. 只输出修改后的代码，不要解释` 
      }]
    }
  })

  const changes = []

  for (const match of searchResult.data) {
    const fileContent = await client.file.read({
      query: { path: match.path }
    })

    const result = await client.session.prompt({
      path: { id: session.data.id },
      body: {
        parts: [{ 
          type: 'text', 
          text: `重构以下文件中的 oldApiMethod 调用：

文件: ${match.path}
\`\`\`
${fileContent.data.content}
\`\`\`` 
        }]
      }
    })

    changes.push({
      file: match.path,
      original: fileContent.data.content,
      refactored: extractCode(result.data)
    })
  }

  // 生成重构预览
  console.log('\n=== 重构预览 ===\n')
  for (const change of changes) {
    console.log(`📄 ${change.file}`)
    console.log(generateDiff(change.original, change.refactored))
  }

  // 确认后应用更改
  const confirm = await prompt('应用这些更改? (y/n): ')
  if (confirm === 'y') {
    for (const change of changes) {
      fs.writeFileSync(change.file, change.refactored)
    }
    console.log('重构完成!')
  }
}
```

#### 并行处理提升效率

```typescript
// scripts/parallel-analysis.ts

import pLimit from 'p-limit'

async function parallelAnalysis() {
  const { client } = await createOpencode()
  
  const files = await glob('src/**/*.ts')
  
  // 限制并发数，避免 API 限流
  const limit = pLimit(3)

  const tasks = files.map(file => 
    limit(async () => {
      // 每个文件创建独立会话，避免上下文污染
      const session = await client.session.create({
        body: { title: `Analyze: ${file}` }
      })

      const content = fs.readFileSync(file, 'utf-8')

      const result = await client.session.prompt({
        path: { id: session.data.id },
        body: {
          parts: [{ 
            type: 'text', 
            text: `分析这个文件的复杂度和潜在问题：\n\n${content}` 
          }]
        }
      })

      return {
        file,
        analysis: extractContent(result.data)
      }
    })
  )

  // 并行执行，最多 3 个同时运行
  const results = await Promise.all(tasks)
  
  console.log(`分析完成: ${results.length} 个文件`)
}
```

---

## HTTP API 直接调用

如果不使用 SDK，可以直接调用 HTTP API。

### 启动 Server

```bash
opencode serve --port 4096 --hostname 127.0.0.1
```

### 查看 OpenAPI 文档

访问 `http://localhost:4096/doc` 查看完整的 OpenAPI 3.1 规范。

### 常用端点

| HTTP 方法 | 路径 | 说明 |
|-----------|------|------|
| `GET` | `/global/health` | 健康检查 |
| `GET` | `/session` | 列出会话 |
| `POST` | `/session` | 创建会话 |
| `POST` | `/session/:id/message` | 发送消息 |
| `GET` | `/session/:id/message` | 获取消息列表 |
| `POST` | `/session/:id/abort` | 中止会话 |
| `GET` | `/event` | SSE 事件流 |
| `GET` | `/file/content?path=<p>` | 读取文件 |
| `GET` | `/find?pattern=<pat>` | 搜索内容 |

### curl 示例

```bash
# 健康检查
curl http://localhost:4096/global/health

# 创建会话
curl -X POST http://localhost:4096/session \
  -H "Content-Type: application/json" \
  -d '{"title": "My Session"}'

# 发送消息
curl -X POST http://localhost:4096/session/{id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "parts": [{"type": "text", "text": "Hello!"}]
  }'
```

---

## TypeScript 类型支持

SDK 包含完整的 TypeScript 类型定义：

```typescript
import type { 
  Session, 
  Message, 
  Part, 
  Provider,
  Agent
} from "@opencode-ai/sdk"
```

所有类型均从 Server 的 OpenAPI 规范自动生成。

---

## 场景对比总结

| 场景 | 关键 API | 特点 |
|------|----------|------|
| **IDE 集成** | `/tui/*`, `session.prompt()`, `event.subscribe()` | 驱动 TUI + 实时事件同步 |
| **CI/CD 自动化** | `session.create()`, `session.prompt()` | 无头运行，结果输出到 PR |
| **自定义客户端** | 全部 API | 完全自定义 UI，流式响应 |
| **批量处理** | `session.prompt()`, `find.*`, `file.*` | 批量创建会话，并行处理 |

---

## 常见问题

### Q: SDK 和直接调 HTTP API 有什么区别？
**A:** SDK 提供类型安全、更好的开发体验和错误处理。HTTP API 更灵活，适合非 JS/TS 项目。

### Q: 如何处理 API 限流？
**A:** 使用并发限制（如 `p-limit`），添加请求间隔，使用批处理而非逐条请求。

### Q: 会话数据存储在哪里？
**A:** OpenCode Server 本地存储，路径在 `~/.opencode/data`。

### Q: 如何在生产环境部署？
**A:** 使用 `opencode serve` 启动无头服务，配置好 API Key 和权限，通过反向代理暴露。

---

## 下一步

- 查看 [OpenAPI 文档](http://localhost:4096/doc)（启动 server 后访问）
- 查看 [SDK 源码](https://github.com/sst/opencode/tree/dev/packages/sdk)
- 查看 [实战案例](./case-add-feature.md)
