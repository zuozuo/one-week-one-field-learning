# Tool（工具）：教给 Claude 的"技能"

## 一句话定义

**Tool 就是 Claude 的"手"**——让它不仅能"说"，还能"做"。

---

## 生活类比

想象 Claude 是一个超级聪明的助理，但他被关在一个房间里，只能通过电话和你交流。

**没有 Tool**：你问"现在几点了？"他只能说"我不知道，我看不到时钟"。

**有了 Tool**：你给他一个"看时间"的按钮（Tool），他按一下，就能告诉你准确时间。

Tool 就是给 Claude 开的"窗口"，让他能访问外部世界。

---

## Tool 能做什么？

| 能力 | 例子 |
|------|------|
| 获取实时信息 | 查天气、查股价、查新闻 |
| 执行操作 | 发邮件、订机票、下单购物 |
| 访问数据库 | 查询用户订单、搜索知识库 |
| 调用其他 API | 翻译、图像识别、语音合成 |
| 操作文件 | 读取文档、生成报告、修改代码 |

---

## Tool 的结构

一个 Tool 由三部分组成：

```
┌─────────────────────────────────────────┐
│                 Tool                     │
├─────────────────────────────────────────┤
│  name: "get_weather"        ← 工具名称   │
│                                          │
│  description: "获取城市天气" ← 功能描述   │
│                                          │
│  input_schema: {...}        ← 参数定义   │
└─────────────────────────────────────────┘
```

### 完整的 Tool 定义示例

```python
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息，包括温度和天气状况",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，如'北京'、'上海'"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度单位，默认摄氏度"
            }
        },
        "required": ["city"]
    }
}
```

---

## 传给 API 的方式

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[weather_tool],  # 把工具传进去！
    messages=[
        {"role": "user", "content": "北京今天天气怎么样？"}
    ]
)
```

当 Claude 收到这个请求，它会：
1. 看到用户问天气
2. 发现自己有 `get_weather` 这个工具
3. 决定使用这个工具
4. 返回 `stop_reason: "tool_use"`

---

## input_schema 详解

### 什么是 JSON Schema？

**JSON**（JavaScript Object Notation）是一种数据格式，用 `{}` 和 `[]` 组织数据，类似 Python 的字典和列表。

**JSON Schema** 则是描述"JSON 数据应该长什么样"的规范——就像表格的"列定义"，告诉你每列叫什么名字、应该填什么类型的数据。

### 具体结构

input_schema 告诉 Claude 这个工具需要什么参数：

```python
"input_schema": {
    "type": "object",           # 参数是一个对象
    "properties": {             # 包含哪些字段
        "city": {
            "type": "string",   # 类型是字符串
            "description": "城市名称"  # 描述（很重要！）
        },
        "date": {
            "type": "string",
            "description": "日期，格式 YYYY-MM-DD，默认今天"
        }
    },
    "required": ["city"]        # 哪些是必填的
}
```

**关键点**：`description` 写得越清楚，Claude 用得越准确！

---

## 支持的参数类型

| 类型 | 示例 |
|------|------|
| `string` | `"北京"`, `"hello"` |
| `number` | `42`, `3.14` |
| `integer` | `1`, `100` |
| `boolean` | `true`, `false` |
| `array` | `["a", "b", "c"]` |
| `object` | `{"key": "value"}` |

### 复杂参数示例

```python
"input_schema": {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "filters": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "price_min": {"type": "number"},
                "price_max": {"type": "number"}
            }
        },
        "sort_by": {
            "type": "string",
            "enum": ["price", "rating", "date"]
        }
    }
}
```

---

## 多工具场景

你可以一次传多个工具，Claude 会自己选择用哪个：

```python
tools = [
    {
        "name": "get_weather",
        "description": "获取天气",
        "input_schema": {...}
    },
    {
        "name": "search_flights",
        "description": "搜索航班",
        "input_schema": {...}
    },
    {
        "name": "book_hotel",
        "description": "预订酒店",
        "input_schema": {...}
    }
]

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "帮我订一张明天去上海的机票"}]
)
# Claude 会选择 search_flights 工具
```

---

## 常见坑点

### 1. description 太简略
```python
# 不好：Claude 不知道什么时候该用
"description": "计算"

# 好：清楚说明用途和场景
"description": "对两个数字进行四则运算，支持加减乘除"
```

### 2. 忘记指定 required
```python
# 问题：Claude 可能不传必要参数
"properties": {"city": {...}}
# 没有 "required": ["city"]

# 正确：明确必填字段
"properties": {"city": {...}},
"required": ["city"]
```

### 3. 参数类型不匹配
```python
# 你期望数字
"price": {"type": "number"}

# 但你的处理函数写成了
def process(price):
    return f"价格是{price}元"  # 字符串拼接，没问题

# 但如果是
def process(price):
    return price * 1.1  # 乘法运算，如果 Claude 传了字符串就会报错
```

---

## 自检清单

- [ ] **费曼检验**：我能解释 Tool 的三个组成部分吗？
- [ ] **迁移检验**：我能为一个新功能（如发邮件）定义 Tool 吗？
- [ ] **深度检验**：我能说出为什么 description 很重要吗？

---

## 常见问题

### Q1: Tool 和 Function 有什么区别？
**A**: 在 Anthropic 的术语中，叫 Tool。在 OpenAI 中，以前叫 Function，现在也改叫 Tool 了。本质是一样的。

### Q2: 一次能传多少个 Tool？
**A**: 没有硬性限制，但工具太多会：
- 消耗更多 token（工具描述算 input）
- 增加 Claude 选错工具的概率

建议：根据任务场景，只传相关的工具。

### Q3: Claude 怎么知道用哪个工具？
**A**: Claude 根据用户意图和工具描述来判断。所以 `description` 写得好很关键！

### Q4: 用户没提到工具相关的事，Claude 会乱调吗？
**A**: 一般不会。Claude 很聪明，它会判断是否需要使用工具。你也可以用 `tool_choice` 参数控制：
```python
tool_choice={"type": "none"}  # 禁止使用工具
tool_choice={"type": "auto"}  # 自动判断（默认）
tool_choice={"type": "tool", "name": "get_weather"}  # 强制使用某个工具
```

### Q5: Tool 能返回多少数据？
**A**: 理论上没限制，但返回太多会消耗 token。建议：返回用户需要的关键信息，不要把整个数据库扔回去。
