# Agentic Loop（Agent 循环）：让 AI 自动完成任务

## 一句话定义

**Agentic Loop 就是"自动驾驶模式"**——AI 自己决定下一步做什么，循环执行直到任务完成。

---

## 生活类比

想象你让朋友帮你订一张机票：

**普通对话模式**（每步都需要你指令）：
1. 你："帮我查一下机票" → 朋友："查到了，有3个航班"
2. 你："选最便宜的" → 朋友："好，南航的最便宜"
3. 你："帮我订这个" → 朋友："订好了"

**Agent 模式**（你说目标，它自动完成）：
1. 你："帮我订一张明天去上海的便宜机票"
2. 朋友：*查航班 → 比价 → 选择 → 下单*
3. 朋友："订好了，南航 MU5101，500 元"

Agentic Loop 就是让 AI 像这个"自主"的朋友一样工作。

---

## Agent Loop 的核心流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agentic Loop                              │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │    用户输入      │
                    │  "帮我订机票"    │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │                              │
              │    ┌────────────────────┐    │
              │    │    发送请求给 Claude  │◀──┼──────────────┐
              │    └──────────┬─────────┘    │              │
              │               │              │              │
              │               ▼              │              │
              │    ┌────────────────────┐    │              │
              │    │   检查 stop_reason  │    │              │
              │    └──────────┬─────────┘    │              │
              │               │              │              │
              │       ┌───────┴───────┐      │              │
              │       ▼               ▼      │              │
              │  ┌─────────┐    ┌─────────┐  │              │
              │  │end_turn │    │tool_use │  │              │
              │  │ 任务完成 │    │需要工具  │  │              │
              │  └────┬────┘    └────┬────┘  │              │
              │       │              │       │              │
              │       │              ▼       │              │
              │       │    ┌──────────────┐  │              │
              │       │    │  执行工具     │  │              │
              │       │    └──────┬───────┘  │              │
              │       │           │          │              │
              │       │           ▼          │              │
              │       │    ┌──────────────┐  │              │
              │       │    │ 返回工具结果  │──┼──────────────┘
              │       │    └──────────────┘  │
              │       │                      │
              └───────┼──────────────────────┘
                      │       循环！
                      ▼
              ┌──────────────┐
              │   输出结果    │
              │  "订好了！"   │
              └──────────────┘
```

---

## 伪代码实现

```python
def agent_loop(user_message, tools):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        # 1. 发送请求
        response = claude.create(messages=messages, tools=tools)
        
        # 2. 检查是否完成
        if response.stop_reason == "end_turn":
            return response.content[0].text  # 任务完成！
        
        # 3. 执行工具调用
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages.append({"role": "user", "content": tool_results})
        
        # 继续循环...
```

---

## 完整代码实现

```python
from anthropic import Anthropic

client = Anthropic()

def run_agent(user_message: str, tools: list, tool_functions: dict, max_iterations: int = 10):
    """
    运行 Agent 循环
    
    Args:
        user_message: 用户输入
        tools: 工具定义列表
        tool_functions: 工具名称到函数的映射
        max_iterations: 最大循环次数（防止无限循环）
    
    Returns:
        最终回答文本
    """
    messages = [{"role": "user", "content": user_message}]
    
    for i in range(max_iterations):
        print(f"\n--- 第 {i+1} 轮 ---")
        
        # 调用 Claude
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        print(f"stop_reason: {response.stop_reason}")
        
        # 任务完成
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text
        
        # 需要调用工具
        if response.stop_reason == "tool_use":
            # 把 assistant 响应加入历史
            messages.append({"role": "assistant", "content": response.content})
            
            # 执行所有工具调用
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"调用工具: {block.name}({block.input})")
                    
                    # 执行对应函数
                    func = tool_functions.get(block.name)
                    if func:
                        try:
                            result = func(**block.input)
                        except Exception as e:
                            result = f"错误: {str(e)}"
                    else:
                        result = f"未知工具: {block.name}"
                    
                    print(f"工具结果: {result}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            
            # 把工具结果加入历史
            messages.append({"role": "user", "content": tool_results})
    
    return "达到最大迭代次数，任务未完成"


# 使用示例
if __name__ == "__main__":
    # 定义工具
    tools = [
        {
            "name": "get_weather",
            "description": "获取城市天气",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        },
        {
            "name": "get_time",
            "description": "获取当前时间",
            "input_schema": {
                "type": "object",
                "properties": {},
            }
        }
    ]
    
    # 定义工具函数
    def get_weather(city):
        return f"{city}今天 25°C，晴天"
    
    def get_time():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tool_functions = {
        "get_weather": get_weather,
        "get_time": get_time
    }
    
    # 运行 Agent
    result = run_agent(
        "现在几点了？北京天气怎么样？",
        tools,
        tool_functions
    )
    print(f"\n最终结果: {result}")
```

---

## Agent Loop 的四个阶段

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  感知   │ ──▶ │  决策   │ ──▶ │  行动   │ ──▶ │  反馈   │
│Perceive │     │ Decide  │     │   Act   │     │Feedback │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
    │               │               │               │
    │               │               │               │
接收用户输入    Claude 分析       执行工具        结果返回
  + 上下文      决定下一步         调用          给 Claude
```

| 阶段 | 做什么 | 对应代码 |
|------|--------|----------|
| 感知 | 接收输入、理解上下文 | `messages` 构建 |
| 决策 | Claude 分析、选择工具 | `client.messages.create()` |
| 行动 | 执行工具函数 | `func(**block.input)` |
| 反馈 | 结果返回，更新状态 | `tool_results` 加入 messages |

---

## 重要设计模式

### 1. 防止无限循环
```python
max_iterations = 10
for i in range(max_iterations):
    # ...
    if response.stop_reason == "end_turn":
        break
else:
    print("警告：达到最大迭代次数")
```

### 2. 错误恢复
```python
try:
    result = execute_tool(name, input)
except Exception as e:
    result = f"工具执行失败: {str(e)}"
    # 继续运行，让 Claude 决定怎么处理
```

### 3. 日志记录
```python
import logging

logging.info(f"用户输入: {user_message}")
logging.info(f"工具调用: {tool_name}({tool_input})")
logging.info(f"工具结果: {result}")
logging.info(f"最终回答: {final_response}")
```

### 4. 状态持久化
```python
class AgentSession:
    def __init__(self):
        self.messages = []
        self.tool_calls_history = []
    
    def save(self, path):
        # 保存到文件
        pass
    
    def load(self, path):
        # 从文件加载
        pass
```

---

## 常见坑点

### 1. 忘记累积 messages
```python
# 错误：每次都重新开始
messages = [{"role": "user", "content": new_message}]

# 正确：累积历史
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": tool_results})
```

### 2. 没有退出条件
```python
# 错误：可能死循环
while True:
    response = client.messages.create(...)
    # 如果 Claude 一直返回 tool_use...

# 正确：设置上限
for i in range(max_iterations):
    ...
```

### 3. 工具函数签名不匹配
```python
# Claude 传的参数
block.input = {"city": "北京", "unit": "celsius"}

# 错误：函数只接受一个参数
def get_weather(city):
    pass

# 正确：使用 **kwargs 或匹配所有参数
def get_weather(city, unit="celsius"):
    pass
```

---

## 自检清单

- [ ] **费曼检验**：我能画出 Agent Loop 的流程图吗？
- [ ] **迁移检验**：如果要加一个新工具，我知道在哪里改代码吗？
- [ ] **深度检验**：我能说出为什么需要防止无限循环吗？

---

## 常见问题

### Q1: Agent 和普通对话有什么区别？
**A**: 
- **普通对话**：一问一答，用户驱动
- **Agent**：用户给目标，AI 自主规划和执行

### Q2: 什么时候用 Agent，什么时候用普通对话？
**A**:
- 简单问答 → 普通对话
- 需要外部数据/操作 → Agent
- 多步骤任务 → Agent

### Q3: Agent 能"记住"之前的对话吗？
**A**: 通过 messages 列表实现。但注意 token 限制，太长需要做摘要或截断。

### Q4: Agent 做错了怎么办？
**A**: 
1. 在错误结果中说明问题
2. Claude 会尝试修正或换方法
3. 严重错误可以直接中断循环

### Q5: 怎么让 Agent 更"聪明"？
**A**:
1. 写好工具的 description
2. 用 system prompt 设定行为规范
3. 提供清晰的错误信息
4. 合理设计工具的粒度
