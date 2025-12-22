# CodeRAG 知识检索

> 不会写的时候，去"抄作业"

---

## 一句话定义

**CodeRAG = 代码的"参考答案库"**

就像写作业时不会做的题可以去查参考书，AI 生成代码时也可以去检索已有的代码实现作为参考。

---

## 为什么需要 CodeRAG？

### 论文描述不完整

```
论文通常这样写:

  "我们使用标准的 Transformer 编码器..."
  "采用常见的 BPR 损失函数..."
  "数据预处理参考 [37]..."

问题:
  - "标准"是什么标准？
  - "常见"是哪种实现？
  - [37] 又是另一篇论文，还要去读？
```

### 只有 Blueprint 不够

```
Blueprint 告诉你:
  "需要实现一个 Transformer 编码器"

但不会告诉你:
  - 具体怎么写 forward 函数
  - LayerNorm 放在哪里
  - 怎么处理 mask

这时候需要 CodeRAG:
  检索已有的 Transformer 实现 → 作为参考
```

---

## CodeRAG 怎么工作？

### 整体流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CodeRAG 工作流程                               │
└─────────────────────────────────────────────────────────────────────┘

                 正在生成 encoder.py
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 1: 识别需求                                                      │
│         从 Blueprint 中提取: "需要实现 Transformer 编码器"            │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 2: 构建查询                                                      │
│         query = "Transformer encoder PyTorch implementation"          │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 3: 检索参考代码                                                  │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │               Reference Code Repository                     │    │
│   │                      (知识库)                               │    │
│   │                                                             │    │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│   │  │ PyTorch  │  │ Hugging  │  │ OpenAI   │  │  Custom  │   │    │
│   │  │ 官方实现 │  │  Face    │  │ 实现     │  │  项目    │   │    │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│   │                                                             │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                        │
│                              ▼                                        │
│                    返回 Top-K 相关代码片段                            │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 4: 注入到生成上下文                                              │
│                                                                       │
│   context = Blueprint + CodeMem + 参考代码                           │
│   code = LLM.generate(context)                                        │
│                                                                       │
│   AI 看到参考代码后:                                                  │
│   "原来 LayerNorm 要这样用！"                                         │
│   "mask 的处理方式是这样的！"                                         │
└──────────────────────────────────────────────────────────────────────┘
```

### 检索方式

```
两种检索机制:

1. 语义检索 (Semantic Search)
   ─────────────────────────────
   使用向量嵌入，按语义相似度检索

   query: "BPR loss function for recommendation"

   检索过程:
     query → Embedding → 向量 → 与知识库向量比较 → 返回相似代码

   优点: 能理解语义，"loss" 和 "损失函数" 能匹配

2. 关键词检索 (Keyword Search)
   ─────────────────────────────
   使用关键词匹配，按词汇重叠度检索

   query: "BPR loss"

   检索过程:
     query → 分词 → 在代码中搜索关键词 → 返回匹配代码

   优点: 精确匹配，适合特定函数名
```

---

## CodeRAG 存什么？

### 知识库内容

```
Reference Code Repository 包含:

┌─────────────────────────────────────────────────────────────────────┐
│                        知识库内容                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 标准库实现                                                       │
│     ├── PyTorch 官方模块                                            │
│     ├── TensorFlow 核心组件                                         │
│     └── NumPy 常用函数                                              │
│                                                                     │
│  2. 开源项目代码                                                     │
│     ├── Hugging Face Transformers                                   │
│     ├── timm (PyTorch Image Models)                                 │
│     └── fairseq                                                     │
│                                                                     │
│  3. 论文复现代码                                                     │
│     ├── Papers With Code 收录项目                                   │
│     ├── 作者开源实现                                                │
│     └── 社区复现版本                                                │
│                                                                     │
│  4. 通用代码模式                                                     │
│     ├── 数据加载模式                                                │
│     ├── 训练循环模式                                                │
│     └── 评估脚本模式                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 索引结构

```yaml
# 代码块索引示例

- id: "pytorch_transformer_encoder_001"
  source: "torch.nn.TransformerEncoder"
  category: "encoder"
  tags: ["transformer", "attention", "nlp"]
  embedding: [0.23, -0.45, 0.12, ...]  # 向量表示
  code_snippet: |
    class TransformerEncoder(Module):
        def __init__(self, encoder_layer, num_layers, ...):
            ...
        def forward(self, src, mask=None, ...):
            ...

- id: "bpr_loss_001"
  source: "recbole/model/loss.py"
  category: "loss_function"
  tags: ["bpr", "recommendation", "ranking"]
  embedding: [0.67, -0.21, 0.89, ...]
  code_snippet: |
    class BPRLoss(nn.Module):
        def forward(self, pos_score, neg_score):
            loss = -torch.log(torch.sigmoid(pos_score - neg_score))
            return loss.mean()
```

---

## 检索时机

### 什么时候触发检索？

```
三种触发条件:

1. 实现细节不明确
   ───────────────────────
   Blueprint: "实现标准的多头注意力"

   CodeRAG 介入:
     "标准的"具体是什么？让我查一下参考实现...

2. AI 主动请求
   ───────────────────────
   AI: "我需要看一下 BPR Loss 的具体实现"
   调用: search_reference_code("BPR Loss implementation")

3. 检测到知识空白
   ───────────────────────
   AI 生成的代码不完整或有明显错误模式
   系统自动检索补充知识
```

### MCP 工具调用

```python
# AI 调用 search_reference_code 工具

# 请求
{
    "tool": "search_reference_code",
    "arguments": {
        "query": "PyTorch BPR loss function for recommendation",
        "top_k": 3
    }
}

# 响应
{
    "results": [
        {
            "source": "recbole/model/loss.py",
            "relevance_score": 0.95,
            "code": "class BPRLoss(nn.Module):\n    def forward(self, pos, neg):\n        ..."
        },
        {
            "source": "cornac/models/bpr/recom_bpr.py",
            "relevance_score": 0.87,
            "code": "def _bpr_loss(self, u, i, j):\n    ..."
        },
        {
            "source": "spotlight/losses.py",
            "relevance_score": 0.82,
            "code": "def bpr_loss(positive_preds, negative_preds):\n    ..."
        }
    ]
}
```

---

## 代码在哪里？

### 核心模块

**文件**: `tools/code_indexer.py`

```python
class CodeIndexer:
    """
    代码检索器，实现 CodeRAG 的核心功能

    职责:
    1. 管理参考代码知识库
    2. 构建代码向量索引
    3. 执行语义检索
    """

    def __init__(self, index_path: str):
        self.index = self._load_index(index_path)
        self.embedder = self._init_embedder()

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[CodeSnippet]:
        """
        搜索相关代码片段

        Args:
            query: 检索查询
            top_k: 返回结果数量

        Returns:
            相关代码片段列表
        """
        # 将查询转换为向量
        query_embedding = self.embedder.encode(query)

        # 在索引中检索
        results = self.index.search(query_embedding, top_k)

        return results

    def add_code(self, source: str, code: str, metadata: dict):
        """将新代码添加到知识库"""
        embedding = self.embedder.encode(code)
        self.index.add(embedding, code, metadata)
```

### MCP 服务器集成

**文件**: `tools/code_implementation_server.py`

```python
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "search_reference_code":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)

        # 使用 CodeIndexer 检索
        indexer = CodeIndexer(index_path)
        results = indexer.search(query, top_k)

        return {
            "status": "success",
            "results": [
                {
                    "source": r.source,
                    "relevance_score": r.score,
                    "code": r.code
                }
                for r in results
            ]
        }
```

---

## CodeRAG vs 直接搜索

### 区别

```
传统搜索引擎:
  输入: "PyTorch Transformer"
  返回: 一堆网页链接
  问题: AI 无法直接使用，需要点击、阅读、提取

CodeRAG:
  输入: "PyTorch Transformer encoder implementation"
  返回: 直接可用的代码片段
  优点: AI 可以直接参考，快速理解实现方式
```

### 类比

```
类比：查字典 vs 问老师

传统搜索 = 查字典
  - 给你一个定义
  - 你自己理解
  - 可能还是不会用

CodeRAG = 问老师
  - 给你一个例子
  - 告诉你怎么用
  - 可以直接模仿
```

---

## 实际效果

### 论文数据

```
CodeRAG 的消融实验结果 (来自论文):

┌──────────────────────────────────────────────────────────────────────┐
│                     模型能力与 CodeRAG 效果                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  小模型 (7B):                                                        │
│    无 CodeRAG:  25.3%                                                │
│    有 CodeRAG:  43.1%    (+70.4% 提升！)                            │
│                                                                      │
│  中模型 (32B):                                                       │
│    无 CodeRAG:  41.2%                                                │
│    有 CodeRAG:  53.8%    (+30.6% 提升)                              │
│                                                                      │
│  大模型 (Claude):                                                    │
│    无 CodeRAG:  68.4%                                                │
│    有 CodeRAG:  75.9%    (+11.0% 提升)                              │
│                                                                      │
│  结论: 模型越小，CodeRAG 帮助越大                                    │
│        即使是大模型，也能从参考代码中受益                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 帮助场景

```
CodeRAG 特别有用的场景:

1. 复杂算法实现
   Blueprint: "实现 Flash Attention"
   问题: Flash Attention 有很多优化技巧
   CodeRAG: 检索 FlashAttention 官方实现 → 参考优化方式

2. 领域特定模式
   Blueprint: "实现推荐系统的负采样"
   问题: 负采样有很多变种
   CodeRAG: 检索 RecBole 的采样实现 → 了解常见做法

3. 框架特定用法
   Blueprint: "使用 PyTorch Lightning 训练"
   问题: Lightning 的 hooks 怎么用
   CodeRAG: 检索 Lightning 示例 → 学习正确用法
```

---

## 小结

```
CodeRAG 是什么？
  → 代码的"参考答案库"，需要时去检索

存什么？
  → 标准库、开源项目、论文复现代码、通用模式

怎么检索？
  → 语义检索 + 关键词检索，返回 Top-K 相关代码

什么时候用？
  → 实现细节不明确、AI 主动请求、检测到知识空白

效果如何？
  → 小模型提升 70%，大模型也能提升 11%

代码在哪？
  → tools/code_indexer.py: CodeIndexer 类
  → tools/code_implementation_server.py: search_reference_code 工具
```

---

## 下一步

代码生成后，还需要验证和修复。Verification 模块负责这个工作：

**→ [06-Verification验证.md](./06-Verification验证.md)**
