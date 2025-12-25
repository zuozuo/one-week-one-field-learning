# Tool Result（工具结果）：把执行结果告诉 Claude

## 一句话定义

**Tool Result 是你对 Claude 的"回复"**——工具执行完了，结果是这个。

---

## 生活类比

继续之前的助理场景：

1. **Claude**："帮我查北京天气"（Tool Use）
2. **你**：打开天气 App，查到结果
3. **你**："查到了，北京今天 25°C，晴天"（Tool Result）
4. **Claude**："北京今天天气不错，25度，适合出门~"（最终回答）

Tool Result 就是第3步——把执行结果反馈给 Claude。

---

## Tool Result 的完整流程

```
┌────────────────────────────────────────────────────────────────────┐
│  第1轮：用户提问，Claude 决定用工具                                   │
├────────────────────────────────────────────────────────────────────┤
│  messages: [                                                        │
│    {role: "user", content: "北京天气如何？"}                         │
│  ]                                                                  │
│                              ↓                                      │
│  response: {                                                        │
│    stop_reason: "tool_use",                                        │
│    content: [{type: "tool_use", id: "toolu_01", name: "get_weather"}]│
│  }                                                                  │
└────────────────────────────────────────────────────────────────────┘
                               ↓
                    你执行 get_weather("北京")
                    得到结果："25°C，晴天"
                               ↓
┌────────────────────────────────────────────────────────────────────┐
│  第2轮：把工具结果告诉 Claude                                        │
├────────────────────────────────────────────────────────────────────┤
│  messages: [                                                        │
│    {role: "user", content: "北京天气如何？"},                        │
│    {role: "assistant", content: [原来的 tool_use]},                 │
│    {role: "user", content: [                                        │
│      {type: "tool_result", tool_use_id: "toolu_01", content: "..."}│
│    ]}                                                               │
│  ]                                                                  │
│                              ↓                                      │
│  response: {                                                        │
│    stop_reason: "end_turn",                                        │
│    content: [{type: "text", text: "北京今天25度，晴天，很适合出门"}]  │
│  }                                                                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## Tool Result 的数据结构

```python
{
    "type": "tool_result",
    "tool_use_id": "toolu_01ABC",      # 必须匹配 tool_use 的 id
    "content": "北京今天 25°C，晴天"    # 工具执行的结果
}
```

### 放在 messages 中的位置

```python
messages = [
    # 1. 原始用户消息
    {"role": "user", "content": "北京天气如何？"},
    
    # 2. Claude 的响应（包含 tool_use）
    {"role": "assistant", "content": response.content},
    
    # 3. 工具结果（作为新的 user 消息）
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "toolu_01ABC",
                "content": "北京今天 25°C，晴天"
            }
        ]
    }
]
```

---

## 完整代码示例

```python
from anthropic import Anthropic

client = Anthropic()

# 定义工具
weather_tool = {
    "name": "get_weather",
    "description": "获取城市天气",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
    }
}

# 模拟天气函数
def get_weather(city):
    # 实际项目中这里会调用真实 API
    return f"{city}今天 25°C，晴天"

# 第1轮：发送请求
messages = [{"role": "user", "content": "北京天气如何？"}]
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[weather_tool],
    messages=messages
)

# 检查是否需要调用工具
if response.stop_reason == "tool_use":
    # 找到 tool_use 块
    for block in response.content:
        if block.type == "tool_use":
            # 执行工具
            result = get_weather(block.input["city"])
            
            # 构建第2轮消息
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }
                ]
            })
    
    # 第2轮：带着结果再次请求
    final_response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=[weather_tool],
        messages=messages
    )
    print(final_response.content[0].text)
```

---

## 多工具结果的返回

如果 Claude 一次调用了多个工具，你需要返回**所有**结果：

```python
# Claude 调用了两个工具
tool_uses = [
    {"id": "toolu_01", "name": "get_weather", "input": {"city": "北京"}},
    {"id": "toolu_02", "name": "get_weather", "input": {"city": "上海"}}
]

# 你需要返回两个结果
tool_results = [
    {
        "type": "tool_result",
        "tool_use_id": "toolu_01",
        "content": "北京 25°C，晴天"
    },
    {
        "type": "tool_result",
        "tool_use_id": "toolu_02",
        "content": "上海 28°C，多云"
    }
]

messages.append({
    "role": "user",
    "content": tool_results  # 一个列表，包含所有结果
})
```

---

## 错误结果的处理

工具执行失败时，也要返回结果，告诉 Claude 发生了什么：

```python
{
    "type": "tool_result",
    "tool_use_id": "toolu_01ABC",
    "content": "错误：无法连接天气服务器，请稍后重试",
    "is_error": True  # 可选，明确标记这是错误
}
```

Claude 会理解这是错误，并做出相应处理（比如告诉用户、尝试其他方法等）。

---

## content 的格式

`content` 可以是：

### 1. 简单字符串
```python
"content": "北京 25°C，晴天"
```

### 2. 结构化数据（JSON 字符串）
```python
import json

"content": json.dumps({
    "city": "北京",
    "temperature": 25,
    "condition": "晴天",
    "humidity": 40
})
```

### 3. 多内容块（富文本）
```python
"content": [
    {"type": "text", "text": "查询结果如下："},
    {"type": "text", "text": "北京 25°C，晴天"}
]
```

---

## 常见坑点

### 1. tool_use_id 不匹配
```python
# 错误：ID 对不上，Claude 会困惑
{
    "tool_use_id": "wrong_id",  # 应该是 "toolu_01ABC"
    "content": "..."
}

# 正确：使用原来的 ID
{
    "tool_use_id": block.id,  # 直接用 block.id
    "content": "..."
}
```

### 2. 忘记把 assistant 响应加入 messages
```python
# 错误：跳过了 assistant 消息
messages = [
    {"role": "user", "content": "北京天气如何？"},
    {"role": "user", "content": [tool_result]}  # 直接加结果
]

# 正确：先加 assistant 响应，再加结果
messages = [
    {"role": "user", "content": "北京天气如何？"},
    {"role": "assistant", "content": response.content},  # Claude 的原响应
    {"role": "user", "content": [tool_result]}
]
```

### 3. content 类型错误
```python
# 错误：返回 Python 对象
"content": {"temp": 25}  # 这是 dict，不是字符串

# 正确：转成字符串
"content": json.dumps({"temp": 25})
# 或
"content": "25°C"
```

---

## 自检清单

- [ ] **费曼检验**：我能解释 tool_result 放在 messages 中的位置吗？
- [ ] **迁移检验**：如果工具执行失败，我知道怎么告诉 Claude 吗？
- [ ] **深度检验**：我能说出为什么必须包含 assistant 的原响应吗？

---

## 常见问题

### Q1: 为什么 tool_result 的 role 是 "user"？
**A**: 从 API 的视角看：
- Claude 发出请求（assistant）
- 你返回结果（user 角色）
- Claude 继续响应（assistant）

这样保持了 user/assistant 的交替模式。

### Q2: 可以在 tool_result 里返回图片吗？
**A**: 目前 tool_result 主要支持文本。如果需要图片，可以返回图片的描述或 URL。

### Q3: 返回的结果越详细越好吗？
**A**: 不一定。太详细会消耗更多 token。返回关键信息就够了：
```python
# 不推荐：返回整个 API 原始响应
"content": "{大量 JSON 数据...}"

# 推荐：提取关键信息
"content": "北京 25°C，晴天，湿度40%"
```

### Q4: Claude 收到结果后一定会停止吗？
**A**: 不一定。它可能：
- 直接给出最终答案（stop_reason: "end_turn"）
- 继续调用其他工具（stop_reason: "tool_use"）
- 基于结果提问（需要你再处理）

### Q5: 多长时间内必须返回结果？
**A**: 没有强制限制，但从用户体验考虑，工具执行应该尽快。如果需要长时间，考虑：
- 使用流式响应
- 返回"正在处理"的中间状态
- 异步处理 + 通知机制
