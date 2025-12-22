# CodeMem 代码记忆

> 让 AI 记住已经写过的代码，但不用记住每一行

---

## 一句话定义

**CodeMem = 代码的"读书笔记"**

你看完一本书不会记住每个字，但会记住"这本书讲了什么、有哪些章节、核心观点是什么"。CodeMem 对代码做同样的事情。

---

## 为什么需要 CodeMem？

### 核心问题

```
场景：生成一个有 10 个文件的项目

生成第 10 个文件时，需要知道:
  - 第 1 个文件导出了什么函数？
  - 第 3 个文件的类叫什么名字？
  - 第 5 个文件的接口参数是什么？

朴素方案：把前 9 个文件的代码都放进 prompt
问题：
  - 每个文件平均 500 tokens
  - 9 个文件 = 4500 tokens
  - 加上论文、Blueprint、其他指令...
  - 很快就超出上下文窗口限制！
```

### CodeMem 的解决方案

```
不存完整代码，只存"摘要"

原始代码 (500 tokens):
┌──────────────────────────────────────────────────────┐
│ class DataLoader:                                    │
│     """加载和预处理训练数据"""                        │
│                                                      │
│     def __init__(self, path: str, batch_size: int):  │
│         self.path = path                             │
│         self.batch_size = batch_size                 │
│         self.data = []                               │
│         self._load_data()                            │
│                                                      │
│     def _load_data(self):                            │
│         with open(self.path) as f:                   │
│             for line in f:                           │
│                 ...（省略 50 行）                     │
│                                                      │
│     def load(self) -> List[Dict]:                    │
│         ...（省略 30 行）                             │
│                                                      │
│     def batch(self, size: int) -> Iterator:          │
│         ...（省略 20 行）                             │
│                                                      │
│     def shuffle(self):                               │
│         ...（省略 10 行）                             │
└──────────────────────────────────────────────────────┘

CodeMem 摘要 (50 tokens):
┌──────────────────────────────────────────────────────┐
│ 文件: data/dataset.py                                │
│                                                      │
│ 核心职责: 加载和预处理训练数据                        │
│                                                      │
│ 公开接口:                                            │
│   - class DataLoader(path: str, batch_size: int)     │
│   - load() -> List[Dict]                             │
│   - batch(size: int) -> Iterator                     │
│   - shuffle() -> None                                │
│                                                      │
│ 依赖关系:                                            │
│   - 导入: config.py                                  │
│   - 被导入: train.py, evaluate.py                    │
└──────────────────────────────────────────────────────┘

压缩率: 10:1
```

---

## CodeMem 存什么？

### Memory Entry 三元组

论文定义的公式：
```
M_f = (P_t, I_t, E_t)
```

翻译成人话：
```
每个文件的记忆 = (核心职责, 公开接口, 依赖关系)

P_t = Core Purpose = 这个文件是干什么的？
I_t = Public Interface = 导出了哪些类、函数、方法？
E_t = Dependency Edges = 和其他文件的关系？
```

### 实际例子

```yaml
# 文件: models/encoder.py 的 Memory Entry

core_purpose: |
  实现 Transformer 编码器模块，包含多头自注意力机制
  和前馈神经网络层，用于将输入序列编码为隐藏表示

public_interface:
  - "class TransformerEncoder(nn.Module)"
  - "  __init__(self, d_model=512, nhead=8, num_layers=6)"
  - "  forward(self, src, src_mask=None) -> Tensor"
  - "class MultiHeadAttention(nn.Module)"
  - "  __init__(self, d_model, nhead, dropout=0.1)"
  - "  forward(self, query, key, value) -> Tensor"

dependency_edges:
  imports_from:        # 这个文件导入了谁
    - config.py        # 导入配置参数
    - utils.py         # 导入辅助函数
  imported_by:         # 这个文件被谁导入
    - model.py         # 主模型使用
    - train.py         # 训练脚本使用
```

---

## CodeMem 怎么工作？

### 工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CodeMem 工作流程                               │
└─────────────────────────────────────────────────────────────────────┘

                    write_file(encoder.py, code_content)
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 1: 检测到 write_file 调用                                        │
│         code_implementation_agent.py 拦截工具调用                     │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 2: 生成摘要                                                      │
│         memory_agent_concise.py:create_code_implementation_summary()  │
│                                                                       │
│         输入: file_path + code_content                                │
│         处理: LLM 分析代码，提取 (Purpose, Interface, Dependencies)   │
│         输出: Memory Entry 摘要                                       │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 3: 存储到 Memory Bank                                            │
│         self.implemented_files[file_path] = memory_entry              │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 4: 后续使用                                                      │
│         生成新文件时，通过 read_code_mem 读取已有文件的摘要            │
│         而不是读取完整代码                                            │
└──────────────────────────────────────────────────────────────────────┘
```

### 生成新文件时

```
场景：要生成 train.py，需要知道之前文件的接口

传统方式:
  context = Blueprint + 完整的 config.py + 完整的 model.py + ...
  问题: 太长了!

CodeMem 方式:
  context = Blueprint + config.py 的摘要 + model.py 的摘要 + ...
  好处: 短小精悍，只包含需要的接口信息

生成 train.py 时看到的上下文:
┌──────────────────────────────────────────────────────────────────────┐
│ ## Blueprint (实现计划)                                              │
│ ...                                                                   │
│                                                                       │
│ ## Code Memory (已实现文件摘要)                                       │
│                                                                       │
│ ### config.py                                                         │
│ 核心职责: 管理全局配置参数                                            │
│ 接口: get_config() -> Config, class Config(embed_dim, lr, ...)       │
│                                                                       │
│ ### models/encoder.py                                                 │
│ 核心职责: 实现 Transformer 编码器                                     │
│ 接口: class TransformerEncoder(d_model, nhead, num_layers)           │
│       forward(src, src_mask) -> Tensor                                │
│                                                                       │
│ ### models/model.py                                                   │
│ 核心职责: 组合编码器和解码器                                          │
│ 接口: class RecommendationModel(config)                               │
│       forward(user_ids, item_ids) -> Tensor                           │
│                                                                       │
│ ## 当前任务                                                           │
│ 请实现 train.py                                                       │
└──────────────────────────────────────────────────────────────────────┘

AI 看到摘要后:
  "我知道了！"
  "从 config 导入 get_config"
  "从 models.model 导入 RecommendationModel"
  "forward 方法需要 user_ids 和 item_ids 两个参数..."
```

---

## 消息历史优化

### 为什么需要优化？

```
迭代生成过程中，消息历史越来越长:

Message 1: [User] 请实现 config.py
Message 2: [AI] 好的，让我实现... (生成代码)
Message 3: [Tool] write_file 成功
Message 4: [User] 请实现 utils.py
Message 5: [AI] 好的，让我实现...
Message 6: [Tool] write_file 成功
... (50 条消息后) ...

问题: 消息历史太长，塞不进上下文窗口
```

### Memory Optimization

```
优化前 (50 条消息):
┌──────────────────────────────────────────────────────────────────────┐
│ Message 1: [User] 请实现 config.py                                   │
│ Message 2: [AI] 好的，让我实现 config.py...                          │
│            class Config:                                              │
│                embed_dim = 64                                         │
│                lr = 0.001                                             │
│                ...（完整代码）                                        │
│ Message 3: [Tool] write_file("config.py") 成功                       │
│ Message 4: [User] 请实现 utils.py                                    │
│ ... (省略 46 条)                                                      │
└──────────────────────────────────────────────────────────────────────┘

优化后 (5 条消息):
┌──────────────────────────────────────────────────────────────────────┐
│ Message 1: [User] Code Memory Summary:                               │
│                                                                       │
│   === 已实现文件 (8 个) ===                                          │
│                                                                       │
│   1. config.py                                                        │
│      职责: 配置管理                                                   │
│      接口: get_config(), class Config                                 │
│                                                                       │
│   2. utils.py                                                         │
│      职责: 工具函数                                                   │
│      接口: normalize(), batch()                                       │
│                                                                       │
│   ... (其他文件的摘要)                                                │
│                                                                       │
│   === 待实现文件 (2 个) ===                                          │
│   - train.py                                                          │
│   - evaluate.py                                                       │
│                                                                       │
│ Message 2-5: (最近 4 条消息保留)                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## read_file 优化

### 问题

```
生成代码时，AI 可能想读取之前的文件:

AI: "我需要看一下 encoder.py 的实现..."
    调用 read_file("encoder.py")

问题:
  - 返回完整代码 = 500 tokens
  - 但 AI 只是想知道接口是什么
  - 浪费 tokens!
```

### CodeMem 的优化

```
拦截 read_file，优先返回摘要:

AI 调用: read_file("encoder.py")

CodeMem 检查: encoder.py 有摘要吗？

  如果有 → 返回摘要 (50 tokens)
  如果没有 → 返回完整代码 (500 tokens)

结果:
  {
    "status": "summary_found",
    "file_path": "encoder.py",
    "summary_content": "核心职责: 编码器模块\n接口: class Encoder...",
    "optimization": "redirected_to_read_code_mem"
  }
```

---

## 代码在哪里？

### 核心类

**文件**: `workflows/agents/memory_agent_concise.py`

```python
class ConciseMemoryAgent:
    """
    简洁记忆代理，实现 CodeMem 机制

    核心职责:
    1. 为每个实现的文件生成压缩摘要
    2. 维护 Memory Bank
    3. 触发消息历史优化
    """

    def __init__(self, plan_content, logger, ...):
        # Memory Bank - 存储所有文件的摘要
        self.implemented_files: Dict[str, str] = {}

    async def create_code_implementation_summary(
        self,
        client,
        client_type,
        file_path: str,
        implementation_content: str,
        files_implemented: int
    ) -> str:
        """为新实现的代码文件创建摘要"""

        prompt = f"""
        分析这段代码，生成简洁的记忆条目:

        文件: {file_path}
        内容:
        {implementation_content}

        请提取:
        1. 核心职责 (1-2 句话)
        2. 公开接口 (类、函数签名)
        3. 依赖关系 (导入和被导入)
        """

        summary = await self._call_llm(client, client_type, prompt)
        self.implemented_files[file_path] = summary
        return summary

    def apply_memory_optimization(
        self,
        system_prompt: str,
        messages: List[Dict],
        files_implemented: int
    ) -> List[Dict]:
        """优化消息历史，用摘要替换完整代码"""

        # 构建 Memory Context
        memory_context = self._build_memory_context()

        # 返回压缩后的消息
        return [
            {"role": "user", "content": f"Code Memory:\n{memory_context}"},
            *messages[-5:]  # 保留最近 5 条
        ]
```

### MCP 工具

**文件**: `tools/code_implementation_server.py`

```python
# read_code_mem 工具
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "read_code_mem":
        file_paths = arguments.get("file_paths", [])

        results = []
        for path in file_paths:
            if path in memory_bank:
                results.append({
                    "file_path": path,
                    "status": "found",
                    "summary_content": memory_bank[path]
                })
            else:
                results.append({
                    "file_path": path,
                    "status": "no_summary"
                })

        return {"results": results}
```

---

## 类比帮助理解

### 类比：学习笔记

```
没有 CodeMem:
  复习考试时，把所有课本从头到尾再看一遍
  问题: 太慢了，来不及

有 CodeMem:
  复习考试时，看之前做的笔记
  笔记上写着: "第三章讲了 XXX，重点公式是 YYY"
  好处: 快速回顾，抓住重点
```

### 类比：会议纪要

```
没有 CodeMem:
  开会时，把之前所有会议的录音都听一遍
  问题: 太长了，没时间

有 CodeMem:
  开会时，看之前会议的纪要
  纪要上写着: "上次决定了 A，待办事项是 B"
  好处: 快速了解上下文
```

---

## 小结

```
CodeMem 是什么？
  → 代码的"读书笔记"，只记关键信息

存什么？
  → Memory Entry = (核心职责, 公开接口, 依赖关系)

怎么用？
  → 生成新文件时，读取已有文件的摘要
  → 消息历史太长时，用摘要压缩

代码在哪？
  → memory_agent_concise.py: ConciseMemoryAgent 类
  → code_implementation_server.py: read_code_mem 工具
```

---

## 下一步

CodeMem 解决了"记住已有代码"的问题，但如果论文里没说清楚怎么实现呢？这时候需要 CodeRAG 来检索参考代码：

**→ [05-CodeRAG知识检索.md](./05-CodeRAG知识检索.md)**
