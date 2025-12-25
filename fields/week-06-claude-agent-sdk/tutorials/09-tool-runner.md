# Tool Runner：自动执行工具的便捷助手

## 一句话定义

**Tool Runner 就是"自动挡"**——你定义好工具，它帮你自动处理调用和循环。

---

## 生活类比

**手动挡（自己写 Agent Loop）**：
- 你发请求 → 检查 stop_reason → 执行工具 → 拼消息 → 再发请求...

**自动挡（Tool Runner）**：
- 你说"跑起来" → 它自动完成所有步骤 → 每一轮给你汇报

---

## 对比：手写 Loop vs Tool Runner

### 手写 Agent Loop

```python
messages = [{"role": "user", "content": "北京天气如何？"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=[weather_tool],
        messages=messages
    )
    
    if response.stop_reason == "end_turn":
        print(response.content[0].text)
        break
    
    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = get_weather(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        messages.append({"role": "user", "content": tool_results})
```

### 使用 Tool Runner

```python
from anthropic import Anthropic, beta_tool

client = Anthropic()

@beta_tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 25°C，晴天"

runner = client.beta.messages.tool_runner(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[get_weather],
    messages=[{"role": "user", "content": "北京天气如何？"}]
)

for message in runner:
    print(f"stop_reason: {message.stop_reason}")
    for block in message.content:
        if hasattr(block, "text"):
            print(f"文本: {block.text}")
        elif block.type == "tool_use":
            print(f"调用工具: {block.name}")
```

---

## Tool Runner 做了什么？

```
┌────────────────────────────────────────────────────────────────┐
│                        Tool Runner                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   你只需要：                                                     │
│   1. 用 @beta_tool 定义工具                                      │
│   2. 传入 tools 和 messages                                     │
│   3. 遍历 runner，每轮得到一个 message                           │
│                                                                 │
│   它自动帮你：                                                   │
│   ✓ 调用 API                                                    │
│   ✓ 检测 tool_use                                               │
│   ✓ 执行工具函数                                                 │
│   ✓ 拼接 tool_result                                            │
│   ✓ 继续下一轮                                                   │
│   ✓ 直到 end_turn 停止                                          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 完整使用示例

> **依赖安装**：此示例使用 `rich` 库美化输出，需先安装：`pip install rich`

```python
from anthropic import Anthropic, beta_tool
import rich  # 用于漂亮打印（需要 pip install rich）

client = Anthropic()

@beta_tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息
    """
    # 模拟 API
    weather_data = {
        "北京": "25°C，晴天",
        "上海": "28°C，多云",
        "广州": "32°C，雷阵雨"
    }
    return weather_data.get(city, f"{city} 天气数据未知")

@beta_tool
def get_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间
    
    Args:
        timezone: 时区，默认北京时间
    
    Returns:
        当前时间
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 创建 runner
runner = client.beta.messages.tool_runner(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[get_weather, get_time],  # 直接传函数，不需要 to_dict()
    messages=[
        {"role": "user", "content": "北京和上海天气怎么样？现在几点了？"}
    ]
)

# 遍历每一轮
for i, message in enumerate(runner):
    print(f"\n=== 第 {i+1} 轮 ===")
    print(f"stop_reason: {message.stop_reason}")
    rich.print(message.content)
```

输出示例：
```
=== 第 1 轮 ===
stop_reason: tool_use
[ToolUseBlock(name='get_weather', input={'city': '北京'}),
 ToolUseBlock(name='get_weather', input={'city': '上海'}),
 ToolUseBlock(name='get_time', input={})]

=== 第 2 轮 ===
stop_reason: end_turn
[TextBlock(text='根据查询结果：
- 北京今天 25°C，晴天
- 上海今天 28°C，多云
- 现在是 2024-01-15 14:30:00')]
```

---

## 获取最终结果

```python
runner = client.beta.messages.tool_runner(...)

# 方式1：遍历，最后一个就是最终结果
last_message = None
for message in runner:
    last_message = message

# 方式2：如果只关心最终结果
messages = list(runner)
final_message = messages[-1]

# 提取文本
final_text = ""
for block in final_message.content:
    if hasattr(block, "text"):
        final_text += block.text
```

---

## 错误处理

工具函数中的异常会被捕获，作为错误结果返回给 Claude：

```python
@beta_tool
def risky_operation(data: str) -> str:
    """可能会失败的操作"""
    if not data:
        raise ValueError("数据不能为空")
    return f"处理 {data} 完成"

# Claude 会收到错误信息，并决定如何处理
runner = client.beta.messages.tool_runner(
    tools=[risky_operation],
    messages=[{"role": "user", "content": "处理空数据"}]
)
```

---

## 与手写 Loop 的选择

| 场景 | 推荐方式 |
|------|----------|
| 快速原型、简单任务 | Tool Runner |
| 需要自定义每轮逻辑 | 手写 Loop |
| 需要流式输出 | 手写 Loop（目前） |
| 需要中途干预 | 手写 Loop |
| 需要详细日志 | 手写 Loop 或遍历 Runner |

---

## 常见坑点

### 1. 忘记遍历 runner
```python
# 错误：runner 是迭代器，不遍历就不会执行
runner = client.beta.messages.tool_runner(...)
# 什么都没发生！

# 正确：必须遍历
for message in runner:
    print(message)
```

### 2. 混淆 tools 参数格式
```python
# 使用 @beta_tool 时：
tools=[get_weather]  # 直接传函数

# 使用手写 dict 时：
tools=[weather_tool_dict]  # 传 dict

# 不能混用！
```

### 3. 异步函数用错版本
```python
# 同步函数用 @beta_tool
@beta_tool
def sync_func(): pass

# 异步函数用 @beta_async_tool
@beta_async_tool
async def async_func(): pass
```

---

## 自检清单

- [ ] **费曼检验**：我能解释 Tool Runner 帮我省了哪些代码吗？
- [ ] **迁移检验**：我能把手写的 Agent Loop 改成 Tool Runner 吗？
- [ ] **深度检验**：我能说出什么时候应该用手写 Loop 而不是 Runner 吗？

---

## 常见问题

### Q1: Tool Runner 支持流式吗？
**A**: 目前不直接支持。如果需要流式输出，建议手写 Loop。

### Q2: 可以限制最大循环次数吗？
**A**: 可以在遍历时自己控制：
```python
for i, message in enumerate(runner):
    if i >= 10:
        break
```

### Q3: 工具执行失败会怎样？
**A**: 异常会被捕获，错误信息返回给 Claude。Claude 会尝试处理（重试、换方法、告知用户）。

### Q4: 可以动态添加/移除工具吗？
**A**: 不可以。每次调用 `tool_runner()` 时工具列表是固定的。需要动态工具，用手写 Loop。

### Q5: Tool Runner 是 beta 功能，稳定吗？
**A**: 核心功能稳定，但 API 可能会调整。生产环境建议做好兼容处理。
