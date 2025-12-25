# Streaming（流式响应）：实时看到 AI 在"打字"

## 一句话定义

**Streaming 就是让你实时看到 Claude 的回答，一个字一个字蹦出来，而不是等它全部想完再一次性显示。**

---

## 生活类比

**非流式**：发微信语音 → 对方录完整段 → 你一次性听完

**流式**：打电话 → 对方说一句你听一句 → 实时交流

Streaming 让用户体验更好——不用干等，能看到 AI 正在"思考"。

---

## 为什么需要 Streaming？

| 场景 | 非流式 | 流式 |
|------|--------|------|
| 等待时间 | 可能几十秒 | 几乎即时开始 |
| 用户感知 | "卡住了？" | "它在回答了" |
| 长回答 | 等很久 | 边看边等 |
| 内存占用 | 一次性加载全部 | 逐块处理 |

---

## 基础用法

### 同步流式

```python
from anthropic import Anthropic

client = Anthropic()

# 使用 stream=True
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "给我讲个故事"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # 实时打印
```

### 异步流式

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def main():
    async with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{"role": "user", "content": "给我讲个故事"}]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)

asyncio.run(main())
```

---

## 流式事件类型

使用 `stream.events` 可以获取更详细的事件：

```python
with client.messages.stream(...) as stream:
    for event in stream.events:
        print(f"事件类型: {event.type}")
```

### 主要事件类型

| 事件 | 含义 |
|------|------|
| `message_start` | 消息开始 |
| `content_block_start` | 内容块开始（text 或 tool_use） |
| `content_block_delta` | 内容增量（新的一小段文本） |
| `content_block_stop` | 内容块结束 |
| `message_delta` | 消息级别的更新 |
| `message_stop` | 消息结束 |

### 处理不同事件

```python
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}]
) as stream:
    for event in stream.events:
        if event.type == "content_block_start":
            print(f"\n[开始内容块: {event.content_block.type}]")
        
        elif event.type == "content_block_delta":
            if hasattr(event.delta, "text"):
                print(event.delta.text, end="", flush=True)
        
        elif event.type == "message_stop":
            print("\n[消息结束]")
```

---

## 流式 + 工具调用

当 Claude 使用工具时，流式同样有效：

```python
weather_tool = {
    "name": "get_weather",
    "description": "获取天气",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}

with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[weather_tool],
    messages=[{"role": "user", "content": "北京天气如何？"}]
) as stream:
    for event in stream.events:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                print(f"[开始调用工具: {event.content_block.name}]")
        
        elif event.type == "content_block_delta":
            if hasattr(event.delta, "text"):
                print(event.delta.text, end="")
            elif hasattr(event.delta, "partial_json"):
                print(f"[工具参数: {event.delta.partial_json}]")
```

---

## 获取完整消息

流式结束后，可以获取完整的消息对象：

```python
with client.messages.stream(...) as stream:
    # 流式处理
    for text in stream.text_stream:
        print(text, end="")

# 流结束后获取完整消息
message = stream.get_final_message()
print(f"\nstop_reason: {message.stop_reason}")
print(f"总 tokens: {message.usage}")
```

---

## 完整的流式 Agent 示例

```python
from anthropic import Anthropic

client = Anthropic()

def stream_agent(user_message, tools, tool_functions, max_iterations=10):
    """流式 Agent 循环"""
    messages = [{"role": "user", "content": user_message}]
    
    for i in range(max_iterations):
        print(f"\n--- 第 {i+1} 轮 ---")
        
        collected_content = []
        
        with client.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=tools,
            messages=messages
        ) as stream:
            current_tool_use = None
            current_tool_input = ""
            
            for event in stream.events:
                if event.type == "content_block_start":
                    if event.content_block.type == "text":
                        pass  # 文本块开始
                    elif event.content_block.type == "tool_use":
                        current_tool_use = {
                            "type": "tool_use",
                            "id": event.content_block.id,
                            "name": event.content_block.name,
                            "input": {}
                        }
                        print(f"\n[调用工具: {event.content_block.name}]", end="")
                
                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        print(event.delta.text, end="", flush=True)
                    elif hasattr(event.delta, "partial_json"):
                        current_tool_input += event.delta.partial_json
                
                elif event.type == "content_block_stop":
                    if current_tool_use:
                        import json
                        try:
                            current_tool_use["input"] = json.loads(current_tool_input)
                        except:
                            current_tool_use["input"] = {}
                        collected_content.append(current_tool_use)
                        current_tool_use = None
                        current_tool_input = ""
            
            final_message = stream.get_final_message()
        
        # 检查是否完成
        if final_message.stop_reason == "end_turn":
            print("\n[任务完成]")
            return
        
        # 处理工具调用
        if final_message.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": final_message.content})
            
            tool_results = []
            for block in final_message.content:
                if block.type == "tool_use":
                    func = tool_functions.get(block.name)
                    if func:
                        result = func(**block.input)
                    else:
                        result = f"未知工具: {block.name}"
                    
                    print(f"\n[工具结果: {result}]")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            
            messages.append({"role": "user", "content": tool_results})

# 使用示例
tools = [{
    "name": "get_weather",
    "description": "获取城市天气",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]

def get_weather(city):
    return f"{city} 25°C，晴天"

stream_agent("北京天气如何？", tools, {"get_weather": get_weather})
```

---

## 常见坑点

### 1. 忘记 flush
```python
# 错误：可能不会实时显示
print(text, end="")

# 正确：强制刷新输出
print(text, end="", flush=True)
```

### 2. 使用错误的方法
```python
# 错误：这是非流式
response = client.messages.create(..., stream=True)

# 正确：使用 stream 方法
with client.messages.stream(...) as stream:
    ...
```

### 3. 忘记处理 context manager
```python
# 错误：没有 with 语句，资源可能不会正确释放
stream = client.messages.stream(...)
for text in stream.text_stream:
    ...

# 正确：使用 with 语句
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        ...
```

---

## 自检清单

- [ ] **费曼检验**：我能解释流式和非流式的区别吗？
- [ ] **迁移检验**：我能把一个非流式的代码改成流式吗？
- [ ] **深度检验**：我能说出为什么流式更节省内存吗？

---

## 常见问题

### Q1: 流式会更慢吗？
**A**: 总时间差不多，但用户感知更好。第一个字符出现得更快。

### Q2: 流式和非流式消耗的 token 一样吗？
**A**: 一样。流式只是改变了传输方式，不影响计费。

### Q3: 网络不好时流式会卡住吗？
**A**: 可能会。建议设置超时和重连机制。

### Q4: 可以在流式过程中取消吗？
**A**: 可以，关闭 stream 或退出 with 块即可：
```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        if should_cancel:
            break  # 退出循环，stream 会被关闭
```

### Q5: 流式能用在 Web 应用里吗？
**A**: 可以。使用 Server-Sent Events (SSE) 或 WebSocket 把流式内容推送给前端。
