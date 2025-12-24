# Provider（提供商）详解

## 什么是 Provider？

**一句话定义**：Provider 就是提供 AI "大脑" 的服务商，比如 OpenAI（提供 GPT）、Anthropic（提供 Claude）。

### 生活类比

想象 OpenCode 是一台电视机：
- **Provider** = 电视台（央视、湖南卫视、Netflix）
- **Model** = 具体的节目（新闻联播、快乐大本营）
- **API Key** = 你的会员卡

你需要有会员卡才能看节目，不同电视台的节目风格不同。

---

## Provider 全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenCode 支持的 Provider                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    推荐的 Provider                        │   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │ OpenCode   │  │ Anthropic  │  │   OpenAI   │        │   │
│  │  │    Zen     │  │  (Claude)  │  │   (GPT)    │        │   │
│  │  │  官方推荐   │  │  超强编程   │  │   老牌厂商  │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    其他云端 Provider                       │   │
│  │                                                          │   │
│  │  Google Gemini  |  Amazon Bedrock  |  Azure OpenAI     │   │
│  │  DeepSeek       |  Groq            |  xAI (Grok)       │   │
│  │  OpenRouter     |  Together AI     |  Fireworks AI     │   │
│  │  ...还有 70+ 个                                          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    本地模型方案                            │   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │   Ollama   │  │ LM Studio  │  │ llama.cpp  │        │   │
│  │  │  最简单     │  │   GUI友好  │  │   最灵活    │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速配置步骤

### 步骤 1：运行连接命令

```bash
# 在 OpenCode TUI 中
/connect
```

### 步骤 2：选择 Provider

```
┌ Add credential
│
◆ Select provider
│  OpenCode Zen (推荐新手)
│  Anthropic
│  OpenAI
│  ...
└
```

### 步骤 3：输入 API Key

```
┌ API key
│
│ sk-xxxxxxxxx
│
└ enter
```

### 步骤 4：选择模型

```bash
# 查看可用模型
/models
```

完成！现在你就可以使用 AI 了。

---

## 主流 Provider 详解

### OpenCode Zen（官方推荐）

**特点**：
- 经过 OpenCode 团队测试验证的模型
- 新手最友好
- 一个账户可用多个模型

**配置步骤**：
1. 运行 `/connect` 选择 OpenCode
2. 访问 [opencode.ai/auth](https://opencode.ai/auth) 登录
3. 添加支付信息，复制 API Key
4. 粘贴 API Key 到 OpenCode

**推荐指数**：⭐⭐⭐⭐⭐（新手首选）

---

### Anthropic (Claude)

**特点**：
- Claude 系列模型，编程能力超强
- 支持 Claude Pro/Max 订阅直接使用
- 上下文窗口大

**配置步骤**：
```bash
/connect
# 选择 Anthropic
# 选择 Claude Pro/Max（如果有订阅）或输入 API Key
```

**推荐模型**：
- `claude-sonnet-4` - 性价比最高
- `claude-opus-4` - 最强大

**推荐指数**：⭐⭐⭐⭐⭐（编程首选）

---

### OpenAI (GPT)

**特点**：
- 老牌厂商，生态完善
- GPT-4o 多模态能力强
- o1 系列推理能力强

**配置步骤**：
1. 访问 [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. 创建 API Key
3. 在 OpenCode 中 `/connect` 选择 OpenAI
4. 粘贴 API Key

**推荐模型**：
- `gpt-4o` - 全能型
- `o1-preview` - 强推理

**推荐指数**：⭐⭐⭐⭐

---

### DeepSeek

**特点**：
- 性价比超高
- 推理能力强
- 国产模型

**配置步骤**：
1. 访问 [platform.deepseek.com](https://platform.deepseek.com)
2. 创建 API Key
3. 在 OpenCode 中 `/connect` 选择 DeepSeek

**推荐模型**：
- `deepseek-reasoner` - 推理能力强

**推荐指数**：⭐⭐⭐⭐（性价比首选）

---

### 本地模型 (Ollama)

**特点**：
- 完全免费
- 数据不出本机
- 需要较好的硬件

**配置步骤**：

1. 安装 Ollama
```bash
# macOS
brew install ollama

# 启动
ollama serve
```

2. 下载模型
```bash
ollama pull llama2
# 或者其他模型
ollama pull codellama
```

3. 配置 OpenCode（在 `opencode.json`）
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "llama2": {
          "name": "Llama 2"
        }
      }
    }
  }
}
```

**推荐指数**：⭐⭐⭐（隐私优先用户）

---

## 配置文件详解

### 基本结构

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4",
  "small_model": "anthropic/claude-haiku-4",
  "provider": {
    "提供商ID": {
      "options": {
        "baseURL": "API地址",
        "apiKey": "API密钥"
      },
      "models": {
        "模型ID": {
          "name": "显示名称"
        }
      }
    }
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `model` | 默认使用的模型 |
| `small_model` | 用于轻量任务（如生成标题）的模型 |
| `provider` | Provider 配置 |
| `options.baseURL` | API 端点地址 |
| `options.apiKey` | API 密钥 |
| `models` | 该 Provider 可用的模型 |

### 使用环境变量

```json
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```

这样就不用把密钥写在配置文件里了。

---

## 模型选择指南

### 按需求选模型

| 需求 | 推荐模型 | 原因 |
|------|---------|------|
| 日常编程 | Claude Sonnet 4 | 性价比高，编程能力强 |
| 复杂推理 | Claude Opus 4 / o1 | 深度思考能力 |
| 快速响应 | Claude Haiku / GPT-4o-mini | 速度快，成本低 |
| 省钱 | DeepSeek | 超高性价比 |
| 隐私敏感 | Ollama + Llama | 本地运行 |

### 按预算选 Provider

| 预算 | 推荐方案 |
|------|---------|
| 免费 | Ollama 本地模型 |
| 低成本 | DeepSeek |
| 中等 | Claude Sonnet / GPT-4o |
| 不差钱 | Claude Opus / o1-preview |

---

## 多 Provider 配置

你可以同时配置多个 Provider，按需切换：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4",
  "provider": {
    "anthropic": {},
    "openai": {},
    "deepseek": {}
  }
}
```

切换模型：
```bash
# 在 TUI 中
/models
# 选择想用的模型
```

---

## 高级配置

### 自定义 Provider

对于不在列表中的 OpenAI 兼容服务：

```json
{
  "provider": {
    "my-provider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "我的自定义提供商",
      "options": {
        "baseURL": "https://api.my-provider.com/v1",
        "apiKey": "{env:MY_PROVIDER_KEY}"
      },
      "models": {
        "my-model": {
          "name": "我的模型",
          "limit": {
            "context": 128000,
            "output": 8192
          }
        }
      }
    }
  }
}
```

### 禁用 Provider

```json
{
  "disabled_providers": ["openai", "gemini"]
}
```

### 只启用特定 Provider

```json
{
  "enabled_providers": ["anthropic", "openai"]
}
```

---

## API Key 存储位置

API Key 存储在：
```
~/.local/share/opencode/auth.json
```

这是一个本地文件，不会上传到任何地方。

---

## 常见问题

### Q: 没有 API Key 怎么办？
**A:** 几个选择：
1. 注册 OpenCode Zen（推荐新手）
2. 注册各个 Provider 的账户获取
3. 使用 Ollama 本地模型（免费）

### Q: 哪个 Provider 最便宜？
**A:**
- 完全免费：Ollama 本地模型
- 云端最便宜：DeepSeek
- 性价比高：Claude Sonnet

### Q: 可以同时用多个 Provider 吗？
**A:** 可以！配置多个后用 `/models` 切换。

### Q: API Key 安全吗？
**A:** 存在本地，不会上传。但要保护好你的电脑。

### Q: 本地模型效果怎么样？
**A:** 取决于你的硬件。中高端显卡（如 RTX 3080+）效果还行，但通常不如云端模型。

---

## 下一步

- 了解 [Mode（模式）](./04-mode.md) 切换 Build/Plan
- 学习 [Config（配置）](./07-config.md) 更多选项
- 查看 [实战案例](./case-add-feature.md)
