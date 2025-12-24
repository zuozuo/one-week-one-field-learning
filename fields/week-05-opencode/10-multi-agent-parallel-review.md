# OpenCode 多 Agent 并行 Review 方案

本文档记录将 Revv（多模型并行代码审查工具）迁移到 OpenCode 多 Agent 架构的完整方案，以及与原 Python 实现的对比分析。

## 一、背景

### Revv 项目简介

**Revv** 是一个多 AI 模型协作审查工具，核心理念是「**同一角色 × 多个模型 = 交叉验证，发现更多盲点**」。

```
┌─────────────────────────────────────────────────────────────┐
│                      Revv 工作流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌─────────────┐                          │
│                    │   输入内容   │                          │
│                    │ (代码/文档)  │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐        │
│    │  Codex  │      │  Gemini   │     │ Claude    │ (并行)  │
│    └────┬────┘      └─────┬─────┘     └─────┬─────┘        │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │  Summary AI  │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │ summary.md  │                          │
│                    └─────────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 迁移目标

将 Revv 的多模型并行审查功能迁移到 OpenCode 的多 Agent 架构，利用 OpenCode 的交互体验同时保持并行执行能力。

---

## 二、OpenCode Agent 系统概述

### Agent 类型

OpenCode 的 Agent 系统分为两种类型：

| 类型 | 说明 | 切换方式 |
|------|------|----------|
| **Primary Agent** | 主代理，处理用户直接交互 | Tab 键切换 |
| **Subagent** | 子代理，由 Primary Agent 调用处理专项任务 | @mention 或自动调用 |

### 内置 Agent

| Agent | 类型 | 职责 |
|-------|------|------|
| **Build** | Primary | 默认开发 Agent，全功能访问 |
| **Plan** | Primary | 分析规划，不修改代码 |
| **General** | Subagent | 通用任务，多步骤执行 |
| **Explore** | Subagent | 快速代码库探索 |

### Subagent 串行执行的原因

OpenCode 原生的 `task` 工具启动 subagent 是**串行**的：

```
LLM Tool Calling 流程:

1. 发送消息给 LLM
   ↓
2. LLM 返回: "我要调用 task 工具"
   ↓
3. OpenCode 执行 task 工具 (启动 subagent)
   ↓
4. 等待 subagent 完成        ← 阻塞等待
   ↓
5. 将结果返回给 LLM
   ↓
6. LLM 看到结果，决定下一步
   ↓
7. 如果需要再调用 task，重复 2-6
```

**核心限制**：
- LLM 的对话是同步的、线性的
- 每次 LLM 调用必须等待工具执行完成才能继续
- 这是 LLM API 的根本限制，不是 OpenCode 特有的

---

## 三、并行方案设计

### 核心思路

绕过 OpenCode 原生 `task` 工具的串行限制，使用 **Custom Tool + OpenCode Server API** 实现真正的并行。

### 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Revv on OpenCode Architecture                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  入口层 (三种方式)                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ /revv 命令   │  │ @revv 调用   │  │ revv-orchestrator Agent │   │
│  │ (Command)    │  │ (Subagent)   │  │ (Primary Agent)          │   │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬──────────────┘   │
│         │                 │                      │                   │
│         └─────────────────┼──────────────────────┘                   │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Revv Core Tool                            │    │
│  │  parallel-review.ts                                          │    │
│  │  ┌─────────────────────────────────────────────────────────┐│    │
│  │  │ 1. 加载 Skill (prompt-selector 或指定 skill)            ││    │
│  │  │ 2. 并行创建 N 个 Session (每个使用不同模型)              ││    │
│  │  │ 3. 异步发送 prompt (POST /prompt_async)                  ││    │
│  │  │ 4. 监听 SSE 事件流，等待所有完成                         ││    │
│  │  │ 5. 收集结果，写入 review 文件                            ││    │
│  │  │ 6. 调用 Summary Session 生成汇总                         ││    │
│  │  └─────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Review Sessions                         │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │    │
│  │  │ Claude  │ │  GPT    │ │DeepSeek │ │ Gemini  │  (并行)    │    │
│  │  │ Session │ │ Session │ │ Session │ │ Session │            │    │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘            │    │
│  │       │           │           │           │                  │    │
│  │       └───────────┴───────────┴───────────┘                  │    │
│  │                       │                                      │    │
│  │                       ▼                                      │    │
│  │              ┌─────────────────┐                             │    │
│  │              │ Summary Session │                             │    │
│  │              │ (汇总 + 评分)    │                             │    │
│  │              └─────────────────┘                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 关键 API

| API | 作用 |
|-----|------|
| `POST /session` | 创建新 Session |
| `POST /session/:id/prompt_async` | **异步**发送 prompt，不等待完成 |
| `GET /session/status` | 检查 Session 状态 |
| `GET /session/:id/message` | 获取消息内容 |
| `GET /event` | SSE 事件流 |

---

## 四、文件结构

```
.opencode/
├── agent/
│   ├── revv-orchestrator.md      # Primary Agent: 编排器
│   ├── revv-reviewer.md          # Subagent: 单模型 Reviewer
│   └── revv-summary.md           # Subagent: 汇总器
│
├── command/
│   └── revv.md                   # /revv 命令定义
│
├── skill/
│   ├── prompt-selector/
│   │   └── SKILL.md              # Prompt 自动选择器
│   ├── backend-code/
│   │   └── SKILL.md              # 后端代码审查
│   ├── frontend-code/
│   │   └── SKILL.md              # 前端代码审查
│   ├── prd/
│   │   └── SKILL.md              # PRD 文档审查
│   ├── web-system-design/
│   │   └── SKILL.md              # 架构设计审查
│   ├── generic/
│   │   └── SKILL.md              # 通用审查
│   └── revv-summary/
│       └── SKILL.md              # 汇总 prompt
│
├── tool/
│   ├── parallel-review.ts        # 核心：并行 review 工具
│   ├── collect-reviews.ts        # 收集 review 结果
│   └── save-review-meta.ts       # 保存元信息
│
└── config/
    └── revv-models.json          # 默认模型配置

opencode.json                      # OpenCode 配置
```

---

## 五、核心组件实现

### 1. 模型配置 (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  
  "revv": {
    "defaultModels": [
      "anthropic/claude-sonnet-4-20250514",
      "openai/gpt-4o",
      "deepseek/deepseek-chat",
      "google/gemini-2.0-flash-exp"
    ],
    "summaryModel": "anthropic/claude-sonnet-4-20250514",
    "timeout": 300,
    "outputDir": ".revv/reviews"
  }
}
```

### 2. Primary Agent: revv-orchestrator.md

```markdown
---
description: Multi-model parallel code review orchestrator. Use when user wants comprehensive code review across multiple AI models.
mode: primary
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
tools:
  read: true
  glob: true
  list: true
  skill: true
  parallel-review: true
  collect-reviews: true
  save-review-meta: true
  write: true
permission:
  write: allow
  bash: deny
---

You are the Revv Orchestrator - a multi-model parallel code review coordinator.

## Your Role
Coordinate comprehensive code reviews by dispatching the same review task to multiple AI models in parallel, then synthesizing their findings.

## Workflow

### Step 1: Understand the Review Request
- Identify what content to review (file, directory, or specific code)
- Determine if user specified a review skill, or needs auto-selection

### Step 2: Select Review Skill
If user didn't specify a skill:
- Load skill `prompt-selector` 
- Analyze the content type and select the most appropriate skill

Available skills:
- `backend-code`: Python, Java, Go, Node.js backend code
- `frontend-code`: React, Vue, TypeScript frontend code  
- `prd`: Product requirement documents
- `web-system-design`: Architecture and system design docs
- `generic`: General purpose review

### Step 3: Execute Parallel Review
Call the `parallel-review` tool with:
- Content path
- Selected skill name
- Model list (use defaults or user-specified)

### Step 4: Generate Summary
After parallel reviews complete:
- Call `collect-reviews` to gather all review outputs
- The summary is automatically generated by parallel-review tool

### Step 5: Report Results
- Show user the summary location
- Highlight critical findings (P0/P1 issues)
- Report any model failures

## Output Locations
All outputs are saved to `.revv/reviews/{session-id}/`:
- `review_{model-name}.md` - Individual model reviews
- `summary.md` - Consolidated summary with scores
- `meta.json` - Review metadata
```

### 3. Subagent: revv-reviewer.md

```markdown
---
description: Single-model code reviewer. Performs thorough code review following specified guidelines.
mode: subagent
temperature: 0.1
maxSteps: 50
tools:
  read: true
  grep: true
  glob: true
  list: true
  skill: true
  write: false
  edit: false
  bash: false
---

You are an expert code reviewer. Your task is to thoroughly review the provided content following the specified review guidelines.

## Instructions
1. First, load the specified review skill to understand the review criteria
2. Carefully analyze all provided content
3. Identify issues at all severity levels (P0/P1/P2)
4. Provide specific, actionable feedback with file locations

## Output Format

Your review must follow this exact format:

# Code Review Report

## 审查概览
- **审查范围**: [files/directories reviewed]
- **主要发现**: [1-2 sentence summary]

## 问题列表

### P0 致命问题
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

### P1 严重问题  
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

### P2 一般问题
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

## 亮点
- [positive observations]

## 内容评分
| 评分项 | 分数 | 说明 |
|--------|------|------|
| 总分 | [0-10] | [brief justification] |

## Scoring Guidelines
- 9-10: Excellent, minimal issues
- 7-8: Good, minor improvements needed
- 5-6: Acceptable, notable issues exist
- 3-4: Poor, significant problems
- 0-2: Critical, needs major rework
```

### 4. Subagent: revv-summary.md

```markdown
---
description: Synthesizes multiple code reviews into unified summary with reviewer scores
mode: subagent  
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
maxSteps: 30
tools:
  read: true
  glob: true
  write: true
  skill: true
permission:
  write: allow
---

You are the Chief Architect responsible for synthesizing multiple code reviews into a unified report.

## Your Task
1. Read all review files from the specified directory
2. Identify consensus issues (mentioned by 2+ reviewers)
3. Identify conflicting opinions and make reasoned judgments
4. Score each reviewer's contribution quality
5. Generate a comprehensive summary report

## Output Format

# Review 汇总报告

## 元信息
- **时间**: {timestamp}
- **审查内容**: {content_path}
- **参与模型**: {model_list}
- **使用 Skill**: {skill_name}

## 共识问题
> 多个模型都指出的问题，可信度高

### [P0] 致命问题
| 问题 | 提及模型 | 位置 | 修复建议 |
|------|----------|------|----------|

### [P1] 严重问题
| 问题 | 提及模型 | 位置 | 修复建议 |

### [P2] 一般问题
| 问题 | 提及模型 | 位置 | 修复建议 |

## 分歧与裁决
> 模型之间有不同看法的问题

| 问题 | 不同观点 | 裁决 | 理由 |
|------|----------|------|------|

## 各模型独特发现
> 单个模型的独特见解

- **{model}**: {unique insight}

## Reviewer 评分

| Reviewer | 得分 | 评价 |
|----------|------|------|
| {model} | {0-10} | {评价，20字以内} |

### 评分维度
- 问题发现能力：是否发现关键问题、独特视角
- 建议可执行性：建议是否具体、包含定位信息
- 分析深度：是否有深入分析而非泛泛而谈

## 整体评估
[Overall assessment and recommendations]
```

### 5. Custom Command: revv.md

```markdown
---
description: Run multi-model parallel code review
agent: revv-orchestrator
---

Review the content at `$1` using multi-model parallel review.

## Parameters
- Content path: $1
- Review skill: $2 (optional, auto-select if not specified)
- Models: $3 (optional, comma-separated, use defaults if not specified)

## Examples
- `/revv ./src` - Auto-select skill, use default models
- `/revv ./src backend-code` - Use backend-code skill
- `/revv ./src prd anthropic/claude-opus-4,openai/gpt-4o` - Custom models

Please execute the review workflow:
1. Analyze content type if skill not specified
2. Launch parallel reviews across configured models
3. Generate summary with reviewer scores
4. Report the results location and critical findings
```

### 6. 核心工具: parallel-review.ts

```typescript
// .opencode/tool/parallel-review.ts
import { tool } from "@opencode-ai/plugin"

interface ReviewResult {
  model: string
  sessionId: string
  status: "success" | "failed" | "timeout"
  outputPath?: string
  error?: string
  duration?: number
}

export default tool({
  description: "Execute parallel code reviews across multiple AI models. Creates separate sessions for each model and waits for all to complete.",
  args: {
    contentPath: tool.schema.string().describe("Path to content to review"),
    skillName: tool.schema.string().describe("Review skill to use (e.g., backend-code, prd)"),
    models: tool.schema.array(tool.schema.string()).optional().describe("Model IDs to use. Defaults to configured models."),
    outputDir: tool.schema.string().optional().describe("Output directory. Defaults to .revv/reviews/{timestamp}"),
    timeout: tool.schema.number().optional().describe("Timeout in seconds per model. Default 300."),
  },
  
  async execute(args, context) {
    const baseUrl = "http://localhost:4096"  // OpenCode server
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19)
    const outputDir = args.outputDir || `.revv/reviews/${timestamp}`
    
    // 1. 获取配置的默认模型
    const configResponse = await fetch(`${baseUrl}/config`)
    const config = await configResponse.json()
    const defaultModels = config.revv?.defaultModels || [
      "anthropic/claude-sonnet-4-20250514",
      "openai/gpt-4o", 
      "deepseek/deepseek-chat",
      "google/gemini-2.0-flash-exp"
    ]
    const models = args.models || defaultModels
    const timeout = (args.timeout || 300) * 1000
    
    // 2. 读取 skill 内容
    const skillResponse = await fetch(`${baseUrl}/file/content?path=.opencode/skill/${args.skillName}/SKILL.md`)
    const skillContent = await skillResponse.json()
    
    // 3. 读取待 review 的内容
    const contentResponse = await fetch(`${baseUrl}/file/content?path=${args.contentPath}`)
    const content = await contentResponse.json()
    
    // 4. 构建 review prompt
    const reviewPrompt = `
You are reviewing the following content. Use the provided review guidelines.

## Review Guidelines (Skill: ${args.skillName})
${skillContent.content}

## Content to Review
Path: ${args.contentPath}

${content.content}

Please provide a thorough review following the output format specified in the guidelines.
`
    
    // 5. 并行创建 sessions 并发送 prompts
    const reviewPromises = models.map(async (modelId: string): Promise<ReviewResult> => {
      const startTime = Date.now()
      const [providerId, modelName] = modelId.split("/")
      const shortName = modelName.split("-")[0]
      
      try {
        // 创建 session
        const createRes = await fetch(`${baseUrl}/session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            title: `Revv Review - ${shortName}`,
            parentID: context.sessionID
          })
        })
        const session = await createRes.json()
        
        // 异步发送 prompt (不等待完成)
        await fetch(`${baseUrl}/session/${session.id}/prompt_async`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            agent: "revv-reviewer",
            model: { providerID: providerId, modelID: modelName },
            parts: [{ type: "text", text: reviewPrompt }]
          })
        })
        
        // 等待 session 完成 (轮询 status)
        const deadline = Date.now() + timeout
        while (Date.now() < deadline) {
          const statusRes = await fetch(`${baseUrl}/session/status`)
          const statuses = await statusRes.json()
          const sessionStatus = statuses[session.id]
          
          if (sessionStatus?.status === "idle") {
            // 完成，获取消息
            const messagesRes = await fetch(`${baseUrl}/session/${session.id}/message`)
            const messages = await messagesRes.json()
            
            const lastAssistant = messages.reverse().find((m: any) => m.info.role === "assistant")
            if (lastAssistant) {
              const textPart = lastAssistant.parts.find((p: any) => p.type === "text")
              if (textPart) {
                const outputPath = `${outputDir}/review_${shortName}.md`
                await fetch(`${baseUrl}/file/write`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ path: outputPath, content: textPart.text })
                })
                
                return {
                  model: modelId,
                  sessionId: session.id,
                  status: "success",
                  outputPath,
                  duration: Date.now() - startTime
                }
              }
            }
          }
          
          await new Promise(resolve => setTimeout(resolve, 2000))
        }
        
        return {
          model: modelId,
          sessionId: session.id,
          status: "timeout",
          error: `Timeout after ${timeout/1000}s`,
          duration: Date.now() - startTime
        }
        
      } catch (error) {
        return {
          model: modelId,
          sessionId: "",
          status: "failed",
          error: String(error),
          duration: Date.now() - startTime
        }
      }
    })
    
    // 6. 等待所有 reviews 完成
    const results = await Promise.all(reviewPromises)
    
    // 7. 收集成功的 reviews
    const successfulReviews = results.filter(r => r.status === "success")
    
    // 8. 生成 Summary
    let summaryPath = ""
    if (successfulReviews.length > 0) {
      const summaryRes = await fetch(`${baseUrl}/session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          title: "Revv Summary",
          parentID: context.sessionID
        })
      })
      const summarySession = await summaryRes.json()
      
      const reviewContents = await Promise.all(
        successfulReviews.map(async (r) => {
          const res = await fetch(`${baseUrl}/file/content?path=${r.outputPath}`)
          const data = await res.json()
          return `## Review from ${r.model}\n\n${data.content}`
        })
      )
      
      const summaryPrompt = `
Please synthesize the following code reviews into a unified summary report.

## Original Content
Path: ${args.contentPath}

## Reviews to Synthesize
${reviewContents.join("\n\n---\n\n")}

Generate a comprehensive summary following the revv-summary format.
`
      
      const summaryMsgRes = await fetch(`${baseUrl}/session/${summarySession.id}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: "revv-summary",
          parts: [{ type: "text", text: summaryPrompt }]
        })
      })
      const summaryMsg = await summaryMsgRes.json()
      
      const textPart = summaryMsg.parts.find((p: any) => p.type === "text")
      if (textPart) {
        summaryPath = `${outputDir}/summary.md`
        await fetch(`${baseUrl}/file/write`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: summaryPath, content: textPart.text })
        })
      }
    }
    
    // 9. 保存 meta.json
    const meta = {
      timestamp,
      contentPath: args.contentPath,
      skill: args.skillName,
      models: models,
      results: results.map(r => ({
        model: r.model,
        status: r.status,
        duration: r.duration,
        error: r.error
      })),
      summaryPath
    }
    
    await fetch(`${baseUrl}/file/write`, {
      method: "POST", 
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        path: `${outputDir}/meta.json`, 
        content: JSON.stringify(meta, null, 2) 
      })
    })
    
    // 10. 返回结果
    return JSON.stringify({
      outputDir,
      summaryPath,
      results: results.map(r => ({
        model: r.model,
        status: r.status,
        outputPath: r.outputPath,
        duration: r.duration ? `${(r.duration/1000).toFixed(1)}s` : undefined,
        error: r.error
      })),
      stats: {
        total: models.length,
        success: successfulReviews.length,
        failed: results.filter(r => r.status === "failed").length,
        timeout: results.filter(r => r.status === "timeout").length
      }
    }, null, 2)
  }
})
```

### 7. Skill: backend-code/SKILL.md

```markdown
---
name: backend-code
description: Backend code review guidelines for Python, Java, Go, Node.js server-side applications
---

## 评审维度

### 1. 代码质量 (权重: 30%)
- 命名清晰性和一致性
- 函数/方法职责单一
- 代码结构合理性（分层、模块化）
- 注释和文档完整性

### 2. API 设计 (权重: 20%)
- RESTful 规范符合度
- 接口命名和路径设计一致性
- 请求/响应格式规范性
- 版本控制策略

### 3. 数据层 (权重: 20%)
- SQL 性能问题（N+1 查询、全表扫描、缺少索引）
- 事务边界正确性
- 数据库连接管理
- ORM 使用规范

### 4. 安全问题 (权重: 20%)
- SQL 注入风险
- 命令注入风险
- 认证授权漏洞
- 敏感信息泄露（日志、错误信息）
- 输入验证缺失

### 5. 并发与性能 (权重: 10%)
- 并发安全问题（竞态条件、死锁）
- 资源泄漏（连接、文件句柄）
- 超时设置合理性
- 缓存使用策略

## 问题严重性定义

| 级别 | 定义 | 示例 |
|------|------|------|
| **P0 致命** | 安全漏洞、数据损坏风险、线上必崩 | SQL 注入、未捕获异常导致进程退出 |
| **P1 严重** | 性能问题、并发问题、资源泄漏 | 数据库连接泄漏、N+1 查询 |
| **P2 一般** | 代码风格、设计可优化、建议改进 | 命名不规范、缺少注释 |

## 输出格式

# Code Review Report

## 审查概览
- **审查范围**: [列出审查的文件/目录]
- **技术栈**: [识别的技术栈]
- **主要发现**: [1-2 句话概述]

## 问题列表

### P0 致命问题
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

### P1 严重问题
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

### P2 一般问题
| 问题 | 位置 | 影响 | 修复建议 |
|------|------|------|----------|

## 亮点
- [值得肯定的设计或实现]

## 内容评分
| 评分项 | 分数 | 说明 |
|--------|------|------|
| 总分 | [0-10] | [评分理由，20字以内] |
```

---

## 六、使用方式

### 方式 1: Custom Command

```bash
# 基本使用 (自动选择 skill)
/revv ./src

# 指定 skill
/revv ./src backend-code

# 指定 skill 和 models
/revv ./src prd anthropic/claude-opus-4,openai/gpt-4o
```

### 方式 2: @ mention Subagent

```
@revv-orchestrator 请 review src/api 目录的后端代码
```

### 方式 3: 切换到 Revv Primary Agent

按 `Tab` 切换到 `revv-orchestrator` agent，然后直接对话：

```
Review the src/api directory for security issues
```

---

## 七、输出结构

```
.revv/reviews/2024-12-25T14-30-00/
├── review_claude.md          # Claude 的 review
├── review_gpt.md             # GPT 的 review
├── review_deepseek.md        # DeepSeek 的 review
├── review_gemini.md          # Gemini 的 review
├── summary.md                # 汇总报告 (包含 Reviewer 评分)
└── meta.json                 # 元信息
```

### meta.json 示例

```json
{
  "timestamp": "2024-12-25T14-30-00",
  "contentPath": "./src/api",
  "skill": "backend-code",
  "models": [
    "anthropic/claude-sonnet-4-20250514",
    "openai/gpt-4o",
    "deepseek/deepseek-chat",
    "google/gemini-2.0-flash-exp"
  ],
  "results": [
    { "model": "anthropic/claude-sonnet-4-20250514", "status": "success", "duration": "45.2s" },
    { "model": "openai/gpt-4o", "status": "success", "duration": "38.1s" },
    { "model": "deepseek/deepseek-chat", "status": "success", "duration": "22.3s" },
    { "model": "google/gemini-2.0-flash-exp", "status": "timeout", "error": "Timeout after 300s" }
  ],
  "summaryPath": ".revv/reviews/2024-12-25T14-30-00/summary.md"
}
```

---

## 八、并行效率对比

```
串行方式（使用原生 task 工具）:
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Claude  │────▶│  GPT    │────▶│DeepSeek │────▶│ Gemini  │
│  60s    │     │  45s    │     │  30s    │     │  40s    │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                    总耗时: 60 + 45 + 30 + 40 = 175s

并行方式（使用 Custom Tool + Server API）:
┌─────────┐
│ Claude  │ ─┐
│  60s    │  │
└─────────┘  │
┌─────────┐  │
│  GPT    │  ├──▶ 同时进行，等待最慢的完成
│  45s    │  │
└─────────┘  │
┌─────────┐  │
│DeepSeek │  │
│  30s    │  │
└─────────┘  │
┌─────────┐  │
│ Gemini  │ ─┘
│  40s    │
└─────────┘
                    总耗时: max(60, 45, 30, 40) = 60s

效率提升：175s → 60s，节省 65% 时间！
```

---

## 九、实现阶段计划

### Phase 1: 核心功能 (MVP)

1. **parallel-review.ts** - 核心并行工具
2. **revv-reviewer.md** - Reviewer subagent
3. **revv-summary.md** - Summary subagent
4. **revv.md** - Custom command
5. **backend-code/SKILL.md** - 首个 skill

**交付物**: 可以运行 `/revv ./src backend-code` 完成多模型并行 review

### Phase 2: 完善 Skills

1. `frontend-code/SKILL.md`
2. `prd/SKILL.md`
3. `web-system-design/SKILL.md`
4. `generic/SKILL.md`
5. `prompt-selector/SKILL.md` - 自动选择

**交付物**: 支持自动 skill 选择，覆盖主要场景

### Phase 3: 评分与历史 (后续迭代)

1. Reviewer 评分解析和持久化
2. `/revv-history` 命令
3. `/revv-scores` 命令
4. 评分趋势统计

### Phase 4: Commit Review (后续迭代)

1. `commit-review/SKILL.md`
2. Git commit 解析支持
3. `--commits` 参数支持

---

## 十、方案对比分析

### 架构对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Revv Python 实现                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Python CLI (revv)                                                       │
│       │                                                                  │
│       ├─── asyncio.gather() ───┬───────┬───────┬───────┐                │
│       │                        │       │       │       │                │
│       ▼                        ▼       ▼       ▼       ▼                │
│  ┌─────────┐              ┌───────┐┌───────┐┌───────┐┌───────┐         │
│  │Selector │              │ codex ││gemini ││opencode││opencode│        │
│  │ Agent   │              │  CLI  ││  CLI  ││ (ds)  ││ (glm) │         │
│  └─────────┘              └───────┘└───────┘└───────┘└───────┘         │
│       │                        │       │       │       │                │
│       │                        └───────┴───────┴───────┘                │
│       │                                │                                 │
│       ▼                                ▼                                 │
│  ┌─────────┐                    ┌─────────────┐                         │
│  │ Prompt  │                    │  Summary    │                         │
│  │Templates│                    │   Agent     │                         │
│  └─────────┘                    └─────────────┘                         │
│                                                                          │
│  特点: 直接控制子进程，自主管理一切                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     Revv on OpenCode 实现                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  OpenCode TUI/CLI                                                        │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    OpenCode Server                               │    │
│  │  ┌─────────────┐                                                 │    │
│  │  │ revv-       │                                                 │    │
│  │  │ orchestrator│──── parallel-review.ts (Custom Tool)           │    │
│  │  └─────────────┘           │                                     │    │
│  │                            │ HTTP API calls                      │    │
│  │                            ▼                                     │    │
│  │  ┌─────────────────────────────────────────────────────────┐    │    │
│  │  │              Session Manager                             │    │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │    │    │
│  │  │  │Session 1│ │Session 2│ │Session 3│ │Session 4│        │    │    │
│  │  │  │ claude  │ │  gpt    │ │deepseek │ │ gemini  │        │    │    │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │    │    │
│  │  └─────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  特点: 依赖 OpenCode 基础设施，通过 API 间接控制                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 维度对比

| 维度 | Revv Python | Revv on OpenCode | 胜出 |
|------|-------------|------------------|------|
| **架构复杂度** | 简单直接，自主控制一切 | 间接控制，依赖 OpenCode 架构 | 🏆 Python |
| **并行实现** | 原生 asyncio，成熟稳定 | Promise.all + HTTP API，有额外开销 | 🏆 Python |
| **进程管理** | 直接管理子进程，精细控制 | 委托给 OpenCode，控制力有限 | 🏆 Python |
| **依赖管理** | 只依赖 Python + CLI 工具 | 依赖 OpenCode 运行时 | 🏆 Python |
| **流式输出** | 实时流式写入文件 | 需要轮询或 SSE | 🏆 Python |
| **超时控制** | asyncio.wait_for 精确控制 | HTTP 超时 + 轮询，不够精确 | 🏆 Python |
| **错误处理** | 完全自主，灵活处理 | 受限于 OpenCode 错误模型 | 🏆 Python |
| **调试体验** | 标准 Python 调试 | 需要理解 OpenCode 内部机制 | 🏆 Python |
| **生态整合** | 独立工具，需单独学习 | 融入 OpenCode 工作流 | 🏆 OpenCode |
| **交互体验** | 纯 CLI，无交互 | TUI + Agent 对话 | 🏆 OpenCode |
| **扩展性** | 需要写 Python 代码 | Markdown 配置即可扩展 | 🏆 OpenCode |
| **用户入口** | 单一 CLI 入口 | 多入口 (命令/Agent/@mention) | 🏆 OpenCode |
| **Session 管理** | 自己实现 | OpenCode 原生支持，可导航 | 🏆 OpenCode |
| **结果展示** | 生成文件，需手动查看 | TUI 中直接展示 | 🏆 OpenCode |
| **部署复杂度** | pip install 即可 | 需要 OpenCode 环境 | 🏆 Python |

### Revv Python 方案优势

```
✅ 架构简洁
   - 直接调用 CLI 工具，没有中间层
   - asyncio 原生并行，性能好
   - 完全掌控执行流程

✅ 稳定可靠
   - 成熟的 Python 异步模型
   - 精确的超时和错误处理
   - 已经验证过的实现

✅ 独立性强
   - 不依赖特定 IDE/编辑器
   - 可以在任何环境运行
   - CI/CD 集成更简单
```

### Revv on OpenCode 方案优势

```
✅ 用户体验
   - 融入 OpenCode 工作流，无需学习新工具
   - TUI 中直接交互，体验流畅
   - 可以对话式 review，追问细节

✅ 扩展性
   - 添加新 Skill 只需写 Markdown
   - Agent 配置声明式，易于定制
   - 利用 OpenCode 的 MCP/Tools 生态

✅ 可发现性
   - @revv-orchestrator 自然语言调用
   - Tab 切换到 revv agent
   - 与其他 OpenCode 功能无缝协作
```

### Revv Python 方案劣势

```
❌ 用户体验
   - 纯 CLI，缺乏交互性
   - 结果需要手动打开文件查看
   - 与日常开发工作流割裂

❌ 学习成本
   - 需要单独学习 revv 命令
   - 需要理解其参数和配置
   - 对新用户不够友好

❌ 扩展复杂
   - 添加新功能需要写 Python
   - 修改 prompt 需要改代码
```

### Revv on OpenCode 方案劣势

```
❌ 技术复杂度
   - 并行实现是"workaround"，不是原生支持
   - 依赖 OpenCode Server API 的稳定性
   - 调试困难，链路长

❌ 性能开销
   - HTTP API 调用开销
   - 轮询 Session 状态
   - 多层抽象带来的延迟

❌ 依赖风险
   - 依赖 OpenCode 的 API 稳定性
   - OpenCode 更新可能破坏实现
   - 不是官方支持的用法
```

---

## 十一、综合评价

### 从技术实现角度：Python 方案更好

```
评分: Python 8/10 vs OpenCode 6/10

理由:
1. 并行是核心需求，Python asyncio 是正道，OpenCode 是绕道
2. 直接控制 vs 间接控制，前者更可靠
3. 已验证的实现 vs 新方案的不确定性
4. 调试和维护成本更低
```

### 从用户体验角度：OpenCode 方案更好

```
评分: Python 5/10 vs OpenCode 8/10

理由:
1. 对话式交互 vs CLI 命令
2. 融入工作流 vs 独立工具
3. TUI 展示 vs 手动查看文件
4. 多入口 vs 单一入口
```

### 从长期维护角度：取决于目标用户

```
如果目标用户是:
- 开发者/CLI 用户 → Python 方案更好
- OpenCode 用户群体 → OpenCode 方案更好
```

---

## 十二、推荐策略

### 短期：保持 Python 实现

```
理由:
1. 已经可用，稳定可靠
2. 并行实现是正道
3. 维护成本低
```

### 中期：作为 OpenCode MCP Server 集成

```
方案: 将 Revv Python 包装为 MCP Server

优势:
- 保留 Python 的并行能力
- 获得 OpenCode 的交互体验
- 两全其美

架构:
┌─────────────────────────────────────────────────────┐
│  OpenCode                                           │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────┐                               │
│  │ revv MCP Server │ ←── Python 实现，提供 MCP 接口 │
│  └─────────────────┘                               │
│       │                                             │
│       ▼                                             │
│  asyncio + subprocess (原有逻辑)                    │
└─────────────────────────────────────────────────────┘
```

### 长期：等待 OpenCode 原生支持

```
如果 OpenCode 未来支持:
- 原生并行 subagent
- 更好的 session 管理 API
- 官方的 multi-model 功能

那时再迁移到纯 OpenCode 方案会更合理
```

---

## 十三、总结

| 方面 | 结论 |
|------|------|
| **技术实现** | Python 方案更优，是"正道" |
| **用户体验** | OpenCode 方案更优，更自然 |
| **推荐策略** | 保持 Python 核心，通过 MCP 集成到 OpenCode |
| **完全迁移** | 不推荐，除非 OpenCode 原生支持并行 multi-agent |

**一句话总结**：Python 实现是更好的技术方案，但可以通过 MCP 获得 OpenCode 的交互体验，两全其美。
