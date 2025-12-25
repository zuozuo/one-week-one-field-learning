# Tool Use（工具调用）：Claude 说"我要用这个工具"

## 一句话定义

**Tool Use 是 Claude 发出的"请求"**——它告诉你：我要用哪个工具，参数是什么。

---

## 生活类比

想象你是 Claude 的助理：

**Claude**："我需要查一下北京的天气，帮我打开天气 App，搜索'北京'。"

这句话就是 Tool Use：
- 工具名称：天气 App（`get_weather`）
- 参数：北京（`{"city": "北京"}`）

你（程序）收到这个请求后，去执行，然后把结果告诉 Claude。

---

## Tool Use 的触发流程

```
用户: "北京今天天气怎么样？"
           │
           ▼
┌─────────────────────────────────────┐
│  Claude 收到问题 + 可用工具列表       │
│  思考：用户问天气，我有 get_weather   │
│  决定：使用 get_weather 工具         │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  API 返回响应：                       │
│  stop_reason: "tool_use"            │
│  content: [                          │
│    {                                 │
│      type: "tool_use",              │
│      id: "toolu_xxx",               │
│      name: "get_weather",           │
│      input: {"city": "北京"}         │
│    }                                 │
│  ]                                   │
└─────────────────────────────────────┘
```

---

## Tool Use 的数据结构

当 Claude 决定使用工具时，响应的 `content` 中会包含 `tool_use` 类型的内容：

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[weather_tool],
    messages=[{"role": "user", "content": "北京天气如何？"}]
)

# 检查是否是工具调用
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            print(f"工具名称: {block.name}")   # "get_weather"
            print(f"调用ID: {block.id}")       # "toolu_01ABC..."
            print(f"参数: {block.input}")      # {"city": "北京"}
```

### 响应结构详解

```python
{
    "id": "msg_xxx",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "tool_use",
            "id": "toolu_01ABC...",      # 每次调用的唯一ID（重要！）
            "name": "get_weather",        # 工具名称
            "input": {                    # Claude 填的参数
                "city": "北京"
            }
        }
    ],
    "stop_reason": "tool_use",           # 标志着需要执行工具
    "usage": {"input_tokens": 50, "output_tokens": 30}
}
```

---

## 处理 Tool Use 的代码模式

```python
def handle_tool_use(response):
    """处理工具调用请求"""
    results = []
    
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            tool_use_id = block.id
            
            # 根据工具名称执行对应函数
            if tool_name == "get_weather":
                result = get_weather(tool_input["city"])
            elif tool_name == "search_flights":
                result = search_flights(tool_input)
            else:
                result = f"未知工具: {tool_name}"
            
            results.append({
                "tool_use_id": tool_use_id,  # 必须对应上！
                "result": result
            })
    
    return results
```

---

## 一次调用多个工具

Claude 可能在一次响应中请求使用多个工具：

```python
# 用户: "帮我查北京和上海的天气"
response.content = [
    {
        "type": "tool_use",
        "id": "toolu_01AAA",
        "name": "get_weather",
        "input": {"city": "北京"}
    },
    {
        "type": "tool_use",
        "id": "toolu_01BBB",
        "name": "get_weather",
        "input": {"city": "上海"}
    }
]
```

你需要执行**所有**工具调用，并返回**所有**结果。

---

## 混合内容：文本 + 工具调用

Claude 有时会先说一句话，再调用工具：

```python
response.content = [
    {
        "type": "text",
        "text": "好的，我来帮你查一下北京的天气。"
    },
    {
        "type": "tool_use",
        "id": "toolu_01CCC",
        "name": "get_weather",
        "input": {"city": "北京"}
    }
]
```

处理时两种类型都要考虑：
```python
for block in response.content:
    if block.type == "text":
        print(f"Claude 说: {block.text}")
    elif block.type == "tool_use":
        print(f"Claude 要用工具: {block.name}")
```

---

## tool_use_id 的重要性

每个 `tool_use` 都有唯一的 `id`。返回结果时**必须**带上这个 ID，Claude 才能知道这是哪个调用的结果。

```python
# Claude 发出的请求
{
    "type": "tool_use",
    "id": "toolu_01ABC",        # 这个 ID 很重要！
    "name": "get_weather",
    "input": {"city": "北京"}
}

# 你返回的结果（下一节详解）
{
    "type": "tool_result",
    "tool_use_id": "toolu_01ABC",  # 必须对应上
    "content": "北京今天 25°C，晴天"
}
```

---

## 常见坑点

### 1. 忘记检查 stop_reason
```python
# 错误：直接取 text，但可能是 tool_use
print(response.content[0].text)  # AttributeError!

# 正确：先判断类型
if response.stop_reason == "end_turn":
    print(response.content[0].text)
elif response.stop_reason == "tool_use":
    # 处理工具调用
```

### 2. 忽略多工具调用
```python
# 错误：只处理第一个
tool_block = response.content[0]

# 正确：遍历所有
for block in response.content:
    if block.type == "tool_use":
        handle_tool(block)
```

### 3. 弄混 name 和 id
```python
# name: 工具的名称，如 "get_weather"
# id: 这次调用的唯一标识，如 "toolu_01ABC"

# 执行工具用 name
if block.name == "get_weather":
    ...

# 返回结果用 id
{"tool_use_id": block.id, ...}
```

---

## 自检清单

- [ ] **费曼检验**：我能解释 tool_use 响应的结构吗？
- [ ] **迁移检验**：如果 Claude 同时调用3个工具，我知道怎么处理吗？
- [ ] **深度检验**：我能说出 tool_use_id 为什么重要吗？

---

## 常见问题

### Q1: Claude 怎么决定用不用工具？
**A**: Claude 会分析用户意图。如果用户的问题需要外部信息或执行操作，而且有合适的工具，它就会选择使用。

### Q2: 可以强制 Claude 用/不用工具吗？
**A**: 可以，用 `tool_choice` 参数：
```python
tool_choice={"type": "none"}           # 禁用工具
tool_choice={"type": "auto"}           # 自动判断（默认）
tool_choice={"type": "any"}            # 必须用工具（任意一个）
tool_choice={"type": "tool", "name": "get_weather"}  # 必须用指定工具
```

### Q3: tool_use 的 input 会有类型错误吗？
**A**: Claude 通常会按照 `input_schema` 填写，但建议你做校验：
```python
city = tool_input.get("city")
if not city or not isinstance(city, str):
    return "错误：城市参数无效"
```

### Q4: 工具调用失败了怎么办？
**A**: 在 tool_result 中返回错误信息，Claude 会理解并决定下一步：
```python
{
    "tool_use_id": "toolu_xxx",
    "content": "错误：无法获取天气数据，请稍后重试",
    "is_error": True  # 可选，明确标记这是错误
}
```

### Q5: Claude 会无限循环调用工具吗？
**A**: 理论上可能，所以建议设置最大循环次数：
```python
max_iterations = 10
for i in range(max_iterations):
    response = client.messages.create(...)
    if response.stop_reason == "end_turn":
        break
    # 处理工具调用...
```
