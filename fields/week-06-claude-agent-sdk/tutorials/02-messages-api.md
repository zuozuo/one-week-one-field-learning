# Messages API：和 Claude 对话的核心接口

## 一句话定义

**Messages API 就是"对话框"**——你发消息进去，Claude 回消息出来。

---

## 生活类比

想象你在用微信聊天：
- 你发一条消息（`messages` 参数）
- 对方回复你（API 返回的 `response`）
- 聊天记录保存着上下文（多轮对话的 `messages` 列表）

Messages API 就是这个"聊天窗口"的接口。

---

## 什么是 Token？

在开始之前，先解释一个重要概念：**Token**（令牌）。

Token 是 AI 模型处理文本的基本单位，你可以简单理解为"文字碎片"：
- 英文：1 个 token ≈ 1 个单词或标点
- 中文：1 个 token ≈ 0.5-1 个汉字

**举例**：
- "Hello world" = 2 tokens
- "你好世界" ≈ 4 tokens

为什么要了解 token？因为：
1. **计费按 token**：输入和输出的 token 数决定费用
2. **有上限**：`max_tokens` 限制返回内容长度

> 小技巧：1024 tokens 约能生成 500 字中文或 750 字英文。

---

## 基础用法

### 最简单的对话

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",  # 选择模型
    max_tokens=1024,                      # 最多返回多少 token（约500字）
    messages=[
        {"role": "user", "content": "你好，Claude！"}
    ]
)

print(message.content[0].text)
# 输出类似：你好！很高兴见到你。有什么我可以帮助你的吗？
```

> **模型说明**：`claude-sonnet-4-5-20250929` 是模型名称，格式为 `系列-版本-日期`。可在 [Anthropic 官网](https://docs.anthropic.com/en/docs/about-claude/models) 查看最新可用模型列表。

### 多轮对话

```python
messages = [
    {"role": "user", "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明！很高兴认识你。"},
    {"role": "user", "content": "我叫什么名字？"}
]

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=messages
)

print(response.content[0].text)
# 输出：你叫小明。
```

---

## 核心参数详解

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | 是 | 模型名称，如 `claude-sonnet-4-5-20250929` |
| `max_tokens` | 是 | 返回内容的最大 token 数 |
| `messages` | 是 | 对话历史，`role` + `content` 的列表 |
| `system` | 否 | 系统提示词，设定 Claude 的角色/行为 |
| `tools` | 否 | 可用的工具列表（Agent 核心！） |
| `temperature` | 否 | 随机性，0=确定性，1=创意性 |
| `stream` | 否 | 是否流式返回 |

### system 参数示例

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system="你是一个专业的Python程序员，回答要简洁、有代码示例。",
    messages=[
        {"role": "user", "content": "怎么读取JSON文件？"}
    ]
)
```

---

## 响应结构

```python
response = client.messages.create(...)

# 响应对象的关键属性
response.id           # 请求ID，如 "msg_01XFDUDYJgAACzvnptvVoYEL"
response.model        # 使用的模型
response.role         # 永远是 "assistant"
response.content      # 内容列表（重点！）
response.stop_reason  # 停止原因："end_turn" 或 "tool_use"
response.usage        # token 使用统计
```

### content 的结构

`response.content` 是一个列表，可能包含：

```python
# 纯文本回复
[
    {"type": "text", "text": "你好，我是Claude！"}
]

# 工具调用（后面会详细讲）
[
    {"type": "tool_use", "id": "xxx", "name": "get_weather", "input": {"city": "北京"}}
]

# 混合（先说话，再调工具）
[
    {"type": "text", "text": "好的，我来查一下天气"},
    {"type": "tool_use", "id": "xxx", "name": "get_weather", "input": {"city": "北京"}}
]
```

---

## stop_reason 的含义

这个字段决定了你接下来该做什么：

| 值 | 含义 | 你该做什么 |
|----|------|-----------|
| `end_turn` | Claude 说完了 | 展示结果，对话结束 |
| `tool_use` | Claude 想用工具 | 执行工具，把结果告诉它 |
| `max_tokens` | token 用完了 | 内容被截断，考虑增加 max_tokens |
| `stop_sequence` | 遇到停止词 | 自定义行为 |

**Agent 的核心逻辑就是检查 `stop_reason`：**
```python
if response.stop_reason == "tool_use":
    # 执行工具，继续对话
elif response.stop_reason == "end_turn":
    # 任务完成
```

---

## 常见坑点

### 1. 忘记 max_tokens
```python
# 错误：会报错
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "你好"}]
)

# 正确：必须指定
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,  # 必填！
    messages=[{"role": "user", "content": "你好"}]
)
```

### 2. 消息顺序错误
```python
# 错误：第一条必须是 user
messages = [
    {"role": "assistant", "content": "你好"},  # 错！
    {"role": "user", "content": "嗯"}
]

# 正确：user 开头，user/assistant 交替
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"},
    {"role": "user", "content": "今天天气怎么样？"}
]
```

### 3. 访问 content 方式错误
```python
# 错误：content 是列表，不是字符串
print(response.content)

# 正确：取第一个元素的 text
print(response.content[0].text)
```

---

## 自检清单

- [ ] **费曼检验**：我能向别人解释 messages 参数的结构吗？
- [ ] **迁移检验**：如果换一个 LLM API，我能找到类似的对话接口吗？
- [ ] **深度检验**：我能说出 stop_reason 各个值的含义吗？

---

## 常见问题

### Q1: messages 里能放多少条消息？
**A**: 取决于模型的上下文窗口（context window）。Claude 3.5 Sonnet 支持 200K tokens。一般几十轮对话没问题。

### Q2: system 和 messages 里的第一条 user 消息有什么区别？
**A**: 
- `system`：全局设定，影响整个对话的行为风格
- `user` 消息：具体的用户输入

类比：system 是"你是客服经理"，user 消息是"我要退货"。

### Q3: temperature 怎么选？
**A**:
- 代码生成、事实问答 → 低温度（0-0.3）
- 创意写作、头脑风暴 → 高温度（0.7-1）

### Q4: 返回的 usage 有什么用？
**A**: 用于计费和监控：
```python
print(f"输入 tokens: {response.usage.input_tokens}")
print(f"输出 tokens: {response.usage.output_tokens}")
```

### Q5: 怎么实现"记忆"功能？
**A**: Claude 本身无状态。你需要自己维护 messages 列表，每次请求都带上完整的对话历史。
