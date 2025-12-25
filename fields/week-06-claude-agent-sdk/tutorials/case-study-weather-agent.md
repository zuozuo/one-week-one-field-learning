# 单点穿透案例：从零构建一个天气查询 Agent

## 目标

用 **不到 50 行核心代码**，构建一个能自动查询天气的 AI Agent。

通过这个案例，你将完整体验：
1. 初始化 Client
2. 定义 Tool
3. 发送请求
4. 处理 Tool Use
5. 返回 Tool Result
6. 完成 Agent 循环

---

## 准备工作

### 1. 安装依赖

```bash
pip install anthropic
```

### 2. 设置 API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-xxx..."
```

或者创建 `.env` 文件：
```
ANTHROPIC_API_KEY=sk-ant-xxx...
```

---

## 第一步：Hello World（最简对话）

先确保 SDK 能正常工作：

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=100,
    messages=[{"role": "user", "content": "说'你好'两个字"}]
)

print(response.content[0].text)
# 输出：你好
```

**检查点**：如果能看到"你好"，说明连接成功！

---

## 第二步：定义天气工具

```python
# 工具定义（告诉 Claude 有这个能力）
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息，包括温度和天气状况。当用户询问天气时使用此工具。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，如'北京'、'上海'、'广州'"
            }
        },
        "required": ["city"]
    }
}

# 工具实现（实际执行的函数）
def get_weather(city: str) -> str:
    """
    模拟天气 API。实际项目中，这里会调用真实的天气服务。
    """
    weather_data = {
        "北京": {"temp": 25, "condition": "晴天", "humidity": 40},
        "上海": {"temp": 28, "condition": "多云", "humidity": 65},
        "广州": {"temp": 32, "condition": "雷阵雨", "humidity": 80},
        "深圳": {"temp": 30, "condition": "阴天", "humidity": 75},
    }
    
    if city in weather_data:
        data = weather_data[city]
        return f"{city}天气：{data['condition']}，温度 {data['temp']}°C，湿度 {data['humidity']}%"
    else:
        return f"抱歉，暂无 {city} 的天气数据"
```

---

## 第三步：发送带工具的请求

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[weather_tool],  # 把工具告诉 Claude
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}]
)

print(f"stop_reason: {response.stop_reason}")
print(f"content: {response.content}")
```

输出：
```
stop_reason: tool_use
content: [ToolUseBlock(type='tool_use', id='toolu_01ABC...', name='get_weather', input={'city': '北京'})]
```

**观察**：Claude 没有直接回答，而是说"我想用 get_weather 工具，参数是 city=北京"。

---

## 第四步：执行工具，返回结果

```python
# 接上一步的代码...

if response.stop_reason == "tool_use":
    # 1. 找到 tool_use 块
    tool_use_block = None
    for block in response.content:
        if block.type == "tool_use":
            tool_use_block = block
            break
    
    # 2. 执行工具
    tool_result = get_weather(tool_use_block.input["city"])
    print(f"工具执行结果: {tool_result}")
    
    # 3. 把结果告诉 Claude
    messages = [
        {"role": "user", "content": "北京今天天气怎么样？"},
        {"role": "assistant", "content": response.content},  # Claude 的原响应
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": tool_result
                }
            ]
        }
    ]
    
    # 4. 再次请求，让 Claude 生成最终回答
    final_response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=[weather_tool],
        messages=messages
    )
    
    print(f"最终回答: {final_response.content[0].text}")
```

输出：
```
工具执行结果: 北京天气：晴天，温度 25°C，湿度 40%
最终回答: 北京今天天气很好，晴天，温度 25°C，湿度 40%，非常适合户外活动！
```

---

## 第五步：封装成完整的 Agent

把上面的逻辑封装成可复用的函数：

```python
from anthropic import Anthropic

client = Anthropic()

# ===== 工具定义 =====
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
    }
}

def get_weather(city: str) -> str:
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "广州": "雷阵雨，32°C",
    }
    return weather_data.get(city, f"{city} 天气数据未知")

# ===== Agent 核心循环 =====
def weather_agent(user_input: str, max_turns: int = 5) -> str:
    """
    天气查询 Agent
    
    Args:
        user_input: 用户输入
        max_turns: 最大对话轮数
    
    Returns:
        Agent 的最终回答
    """
    tools = [weather_tool]
    tool_functions = {"get_weather": get_weather}
    messages = [{"role": "user", "content": user_input}]
    
    for turn in range(max_turns):
        # 调用 Claude
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # 任务完成
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        # 需要调用工具
        if response.stop_reason == "tool_use":
            # 保存 assistant 响应
            messages.append({"role": "assistant", "content": response.content})
            
            # 执行所有工具调用
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    func = tool_functions.get(block.name)
                    result = func(**block.input) if func else "未知工具"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # 添加工具结果
            messages.append({"role": "user", "content": tool_results})
    
    return "超过最大轮数，任务未完成"


# ===== 使用 Agent =====
if __name__ == "__main__":
    questions = [
        "北京天气怎么样？",
        "上海和广州今天天气如何？",
        "深圳下雨吗？"
    ]
    
    for q in questions:
        print(f"\n用户: {q}")
        answer = weather_agent(q)
        print(f"Agent: {answer}")
```

---

## 运行效果

```
用户: 北京天气怎么样？
Agent: 北京今天是晴天，气温25°C，天气很好，适合出行！

用户: 上海和广州今天天气如何？
Agent: 查询结果如下：
- 上海：多云，28°C
- 广州：雷阵雨，32°C
广州可能需要带伞，上海天气还不错。

用户: 深圳下雨吗？
Agent: 抱歉，我目前没有深圳的天气数据，建议您查看其他天气服务。
```

---

## 完整代码（可直接运行）

```python
"""
天气查询 Agent - 完整可运行示例
运行前请设置环境变量: export ANTHROPIC_API_KEY="sk-ant-xxx..."
"""

from anthropic import Anthropic

# 初始化客户端
client = Anthropic()

# 工具定义
WEATHER_TOOL = {
    "name": "get_weather",
    "description": "获取指定城市的天气信息。当用户询问某个城市的天气时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称，如北京、上海"}
        },
        "required": ["city"]
    }
}

# 模拟天气数据（实际项目中替换为真实 API）
def get_weather(city: str) -> str:
    data = {
        "北京": "晴天 25°C",
        "上海": "多云 28°C", 
        "广州": "雷阵雨 32°C",
        "深圳": "阴天 30°C",
        "杭州": "小雨 22°C",
    }
    return data.get(city, f"暂无{city}的天气数据")

# Agent 主函数
def run_agent(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]
    
    for _ in range(5):  # 最多5轮
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=[WEATHER_TOOL],
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = get_weather(block.input["city"])
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": results})
    
    return "任务未完成"

# 主程序
if __name__ == "__main__":
    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ["退出", "exit", "quit"]:
            print("再见！")
            break
        response = run_agent(user_input)
        print(f"Agent: {response}")
```

---

## 下一步挑战

你已经掌握了基础！试试这些扩展：

### 挑战1：添加更多工具
```python
# 添加时间查询工具
time_tool = {
    "name": "get_time",
    "description": "获取当前时间",
    "input_schema": {"type": "object", "properties": {}}
}

def get_time() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

### 挑战2：接入真实天气 API
```python
import httpx

def get_weather_real(city: str) -> str:
    # 使用免费的天气 API
    response = httpx.get(f"https://wttr.in/{city}?format=3")
    return response.text
```

### 挑战3：添加记忆功能
```python
class WeatherAgent:
    def __init__(self):
        self.history = []
    
    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        # ... 使用 self.history 作为 messages
```

---

## 自检清单

- [ ] 我能独立运行这个天气 Agent
- [ ] 我理解每一步的作用（Client → Tool → Request → Tool Use → Result → Loop）
- [ ] 我能修改代码，添加一个新工具
- [ ] 我能解释为什么需要把 tool_result 的 role 设为 "user"

---

> **恭喜！** 你已经完成了 Claude Agent SDK 的入门之旅。
> 
> 现在，你可以用这套模式构建各种 AI Agent：
> - 客服机器人（查订单、处理退款）
> - 代码助手（读写文件、运行命令）
> - 数据分析师（查数据库、生成图表）
> - ...任何需要"AI + 工具"的场景！
