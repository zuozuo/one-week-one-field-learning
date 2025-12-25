# @beta_tool 装饰器：用 Python 函数快速定义工具

## 一句话定义

**@beta_tool 是语法糖**——让你直接用 Python 函数定义工具，不用手写 JSON Schema。

---

## 生活类比

**传统方式**：想注册一个技能，需要填一堆表格（JSON Schema）

**@beta_tool**：直接亮出你的技能，系统自动帮你填表格

---

## 对比：传统 vs @beta_tool

### 传统方式（手写 JSON Schema）

```python
# 1. 定义工具 Schema
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的天气信息",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度单位"
            }
        },
        "required": ["city"]
    }
}

# 2. 定义执行函数
def get_weather_impl(city: str, unit: str = "celsius") -> str:
    return f"{city} 25°C"

# 3. 手动关联
tool_functions = {"get_weather": get_weather_impl}
```

### @beta_tool 方式（一步到位）

```python
from anthropic import beta_tool

@beta_tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称
        unit: 温度单位，可选 celsius 或 fahrenheit
    
    Returns:
        天气信息字符串
    """
    return f"{city} 25°C"

# 直接使用！
# get_weather.to_dict() 会生成 JSON Schema
# get_weather("北京") 会执行函数
```

---

## 核心原理

`@beta_tool` 装饰器做了这些事：

1. **解析函数签名**：参数名、类型、默认值
2. **解析 docstring**：description 和参数描述
3. **生成 JSON Schema**：自动转换为 API 需要的格式
4. **保留原函数**：装饰后的函数仍然可以正常调用

```python
@beta_tool
def add(a: int, b: int) -> int:
    """将两个整数相加
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        两数之和
    """
    return a + b

# 查看生成的 Schema
print(add.to_dict())
# {
#     "name": "add",
#     "description": "将两个整数相加",
#     "input_schema": {
#         "type": "object",
#         "properties": {
#             "a": {"type": "integer", "description": "第一个整数"},
#             "b": {"type": "integer", "description": "第二个整数"}
#         },
#         "required": ["a", "b"]
#     }
# }

# 正常调用函数
result = add(1, 2)  # 3
```

---

## 完整使用示例

```python
from anthropic import Anthropic, beta_tool

client = Anthropic()

@beta_tool
def get_weather(city: str) -> str:
    """获取城市天气信息
    
    Args:
        city: 城市名称，如"北京"、"上海"
    
    Returns:
        天气描述
    """
    # 模拟 API 调用
    return f"{city}今天 25°C，晴天"

@beta_tool
def get_time() -> str:
    """获取当前时间
    
    Returns:
        当前时间字符串
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 使用工具
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[get_weather.to_dict(), get_time.to_dict()],  # 转成 dict
    messages=[{"role": "user", "content": "北京天气怎么样？现在几点？"}]
)

# 处理工具调用
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            if block.name == "get_weather":
                result = get_weather(**block.input)  # 直接调用
            elif block.name == "get_time":
                result = get_time()
            print(f"{block.name}: {result}")
```

---

## 支持的类型标注

| Python 类型 | JSON Schema 类型 |
|-------------|-----------------|
| `str` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `list` | `array` |
| `dict` | `object` |
| `Optional[T]` | 非必填字段 |
| `Literal["a", "b"]` | `enum` |

### 复杂类型示例

```python
from typing import Optional, Literal, List

@beta_tool
def search(
    query: str,
    category: Literal["news", "images", "videos"],
    max_results: int = 10,
    filters: Optional[List[str]] = None
) -> str:
    """搜索内容
    
    Args:
        query: 搜索关键词
        category: 搜索类别
        max_results: 最大返回数量
        filters: 可选的过滤条件
    """
    return f"搜索 {query} 在 {category}"
```

---

## 异步版本（进阶内容）

> **提示**：异步编程是 Python 进阶概念，初学者可跳过本节。

对于异步函数，使用 `@beta_async_tool`：

```python
# 需要先安装 httpx: pip install httpx
from anthropic import beta_async_tool
import httpx

@beta_async_tool
async def fetch_url(url: str) -> str:
    """获取 URL 内容
    
    Args:
        url: 要获取的网址
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text[:500]

# 在异步代码中使用
result = await fetch_url("https://example.com")
```

---

## Docstring 格式要求

`@beta_tool` 依赖 docstring 来生成描述。推荐使用 Google 风格：

```python
@beta_tool
def example(param1: str, param2: int = 0) -> str:
    """这里是函数的整体描述，会变成 tool 的 description。
    
    可以有多行描述。
    
    Args:
        param1: 第一个参数的描述
        param2: 第二个参数的描述，默认值是 0
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 什么情况下会抛异常
    """
    return "result"
```

---

## 常见坑点

### 1. 忘记类型标注
```python
# 错误：没有类型，无法推断 Schema
@beta_tool
def get_weather(city):
    pass

# 正确：加上类型
@beta_tool
def get_weather(city: str) -> str:
    pass
```

### 2. Docstring 格式不对
```python
# 错误：Args 格式不对
@beta_tool
def get_weather(city: str) -> str:
    """获取天气
    city - 城市名
    """

# 正确：使用标准格式
@beta_tool
def get_weather(city: str) -> str:
    """获取天气
    
    Args:
        city: 城市名
    """
```

### 3. 忘记调用 to_dict()
```python
# 错误：传了函数对象
tools=[get_weather]

# 正确：转成 dict
tools=[get_weather.to_dict()]
```

---

## 自检清单

- [ ] **费曼检验**：我能解释 @beta_tool 帮我省了什么工作吗？
- [ ] **迁移检验**：我能把一个手写的 tool 改成 @beta_tool 形式吗？
- [ ] **深度检验**：我能说出 docstring 的 Args 是怎么变成 Schema 的吗？

---

## 常见问题

### Q1: beta 是什么意思？以后会变吗？
**A**: 说明这个 API 还在测试阶段，可能会有变化。但核心功能应该会保留。

### Q2: 可以用 Pydantic 模型作为参数吗？
**A**: 目前不直接支持，建议用基础类型。复杂对象可以拆成多个参数。

### Q3: 怎么让某个参数变成可选的？
**A**: 两种方式：
```python
# 方式1：给默认值
def func(city: str, unit: str = "celsius"):
    pass

# 方式2：用 Optional
from typing import Optional
def func(city: str, unit: Optional[str] = None):
    pass
```

### Q4: 支持 \*args 和 \*\*kwargs 吗？
**A**: 不支持。工具参数需要是明确定义的。

### Q5: 装饰器会影响函数性能吗？
**A**: 几乎不影响。Schema 只在导入时生成一次，函数调用和普通函数一样。
