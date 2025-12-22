# Blueprint 蓝图

> 把杂乱的论文变成清晰的实现计划

---

## 一句话定义

**Blueprint = 论文的"施工图纸"**

就像建房子需要先画图纸，写代码也需要先有计划。Blueprint 就是把一篇论文变成一份可执行的实现计划。

---

## 为什么需要 Blueprint？

### 没有 Blueprint 的问题

```
直接让 AI 读论文写代码:

AI: "好的，让我读完这 20 页论文..."
    (读了前 3 页)
    "我先写个 config.py..."
    (写完)
    "然后是 model.py..."
    (写到一半)
    "等等，第 15 页有个超参数我漏看了..."
    "还有第 8 页的公式我理解错了..."
    (返工重写)

问题:
  - 边读边写，容易遗漏
  - 前后不一致
  - 大量返工
```

### 有 Blueprint 的好处

```
先生成 Blueprint，再按计划执行:

Phase 1:
  Concept Agent: "整体架构是这样的..."
  Algorithm Agent: "所有公式和参数都提取出来了..."
  Planning Agent: "实现计划如下..."
  → 输出 Blueprint

Phase 2:
  AI: "按照 Blueprint，第一步是 config.py"
      "Blueprint 说参数是这些..."
      (写完)
      "第二步是 data_loader.py"
      "Blueprint 说接口是这样..."
      (写完)
      ...

好处:
  - 先整体规划，再分步执行
  - 信息集中，不会遗漏
  - 前后一致
```

---

## Blueprint 包含什么？

### 五大部分

```yaml
complete_reproduction_plan:

  # ═══════════════════════════════════════════════════════════
  # Part 1: 文件结构 (file_structure)
  # ═══════════════════════════════════════════════════════════
  # 告诉你: 需要创建哪些文件，按什么顺序

  file_structure:
    - path: "config.py"
      priority: 1                    # 优先级，数字越小越先实现
      description: "全局配置和超参数"

    - path: "data/dataset.py"
      priority: 2
      description: "数据加载和预处理"

    - path: "models/encoder.py"
      priority: 3
      description: "编码器模块"

    - path: "models/model.py"
      priority: 4
      description: "主模型，组合各个组件"

    - path: "train.py"
      priority: 5
      description: "训练脚本"


  # ═══════════════════════════════════════════════════════════
  # Part 2: 组件规格 (implementation_components)
  # ═══════════════════════════════════════════════════════════
  # 告诉你: 每个模块具体要实现什么

  implementation_components:
    - name: "BPR Loss"
      file: "models/loss.py"
      algorithm: "Bayesian Personalized Ranking"
      formula: "L = -∑ log σ(y_ui - y_uj) + λ||Θ||²"
      pseudocode: |
        for (u, i, j) in samples:
            pos_score = model(u, i)
            neg_score = model(u, j)
            loss += -log(sigmoid(pos_score - neg_score))
        loss += lambda * regularization

    - name: "User Encoder"
      file: "models/encoder.py"
      algorithm: "Embedding Lookup"
      input: "user_id: int"
      output: "user_embedding: Tensor[batch, dim]"


  # ═══════════════════════════════════════════════════════════
  # Part 3: 验证方案 (validation_approach)
  # ═══════════════════════════════════════════════════════════
  # 告诉你: 怎么验证代码是否正确

  validation_approach:
    - type: "unit_test"
      target: "BPR Loss computation"
      expected: "Loss decreases during training"

    - type: "metric_test"
      target: "Recommendation accuracy"
      expected: "NDCG@10 > 0.3 on test set"


  # ═══════════════════════════════════════════════════════════
  # Part 4: 环境配置 (environment_setup)
  # ═══════════════════════════════════════════════════════════
  # 告诉你: 运行需要什么环境

  environment_setup:
    python_version: "3.9"
    dependencies:
      - torch>=2.0
      - numpy>=1.21
      - pandas>=1.5
    hardware:
      - GPU recommended


  # ═══════════════════════════════════════════════════════════
  # Part 5: 实现策略 (implementation_strategy)
  # ═══════════════════════════════════════════════════════════
  # 告诉你: 分几个阶段实现

  implementation_strategy:
    phases:
      - name: "Foundation"
        description: "基础设施"
        files: ["config.py", "utils.py"]

      - name: "Data Pipeline"
        description: "数据处理流水线"
        files: ["data/dataset.py", "data/sampler.py"]

      - name: "Core Model"
        description: "核心模型组件"
        files: ["models/encoder.py", "models/model.py", "models/loss.py"]

      - name: "Training"
        description: "训练和评估"
        files: ["train.py", "evaluate.py"]
```

---

## 三个 Agent 如何协作？

### 分工

```
┌─────────────────────────────────────────────────────────────────────┐
│                           论文内容                                   │
│                                                                     │
│  "We propose a novel recommendation framework based on              │
│   Bayesian Personalized Ranking. The core innovation is...          │
│   The loss function is defined as L = -∑ log σ(...)                 │
│   We use embedding dimension of 64 and learning rate 0.001..."      │
│                                                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
    ┌─────────────────────────┐    ┌─────────────────────────┐
    │     Concept Agent       │    │    Algorithm Agent      │
    │     (宏观专家)          │    │    (微观专家)           │
    │                         │    │                         │
    │  看的是:                │    │  看的是:                │
    │  • 论文整体结构         │    │  • 每个公式             │
    │  • 核心贡献是什么       │    │  • 每个算法步骤         │
    │  • 有哪些模块           │    │  • 每个超参数           │
    │  • 模块之间怎么连接     │    │  • 伪代码               │
    │                         │    │                         │
    │  输出:                  │    │  输出:                  │
    │  • 这是推荐系统论文     │    │  • Loss 公式: L = ...   │
    │  • 核心是 BPR 方法      │    │  • 采样策略: ...        │
    │  • 包含 User Encoder,   │    │  • embed_dim = 64       │
    │    Item Encoder,        │    │  • lr = 0.001           │
    │    Interaction Model    │    │  • batch_size = 256     │
    └────────────┬────────────┘    └────────────┬────────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                   ┌─────────────────────────┐
                   │     Planning Agent      │
                   │     (规划专家)          │
                   │                         │
                   │  整合两边的信息:        │
                   │  • 设计文件结构         │
                   │  • 分配实现优先级       │
                   │  • 明确每个文件的规格   │
                   │  • 制定验证方案         │
                   │                         │
                   │  输出:                  │
                   │  → Blueprint            │
                   └─────────────────────────┘
```

### 生活类比

```
类比：装修房子

Concept Agent = 设计师
  "这个房子的风格是现代简约，有客厅、卧室、厨房..."

Algorithm Agent = 工程师
  "客厅需要 30 平米，用这种材料，电路要这样布..."

Planning Agent = 项目经理
  "好，综合两边的意见，施工计划如下:
   第一周: 水电
   第二周: 墙面
   ..."
```

---

## 代码在哪里？

### Prompt 定义

**文件**: `prompts/code_prompts.py`

```python
# Concept Agent 的 Prompt
PAPER_CONCEPT_ANALYSIS_PROMPT = """
You are a research analyst specialized in extracting
high-level concepts from research papers.

Your task:
1. Identify the paper's core contribution
2. Map the overall structure and methodology
3. Identify key modules and their relationships
4. Extract validation criteria

Output format:
- Paper Structure Analysis
- Method Decomposition
- Implementation Mapping
- Validation Approach
"""

# Algorithm Agent 的 Prompt
PAPER_ALGORITHM_ANALYSIS_PROMPT = """
You are a technical analyst specialized in extracting
implementation details from research papers.

Your task:
1. Extract all algorithms and pseudocode
2. Identify mathematical formulas
3. Document network architectures
4. List hyperparameters and configurations

Output format:
- Algorithm Implementations
- Mathematical Formulations
- Network Specifications
- Hyperparameter Settings
"""

# Planning Agent 的 Prompt (CODE_PLANNING_PROMPT)
# 包含 5 个必需的 section
```

### Blueprint 完整性检查

**文件**: `agent_orchestration_engine.py`

```python
def _assess_output_completeness(text: str) -> float:
    """
    检查 Blueprint 是否完整

    必须包含 5 个 section:
    1. file_structure
    2. implementation_components
    3. validation_approach
    4. environment_setup
    5. implementation_strategy
    """
    required_sections = [
        "file_structure:",
        "implementation_components:",
        "validation_approach:",
        "environment_setup:",
        "implementation_strategy:",
    ]

    found = sum(1 for s in required_sections if s in text.lower())
    return found / len(required_sections)  # 返回 0.0 - 1.0
```

---

## 实际效果

### 输入（论文片段）

```
We propose BPR-MF, a matrix factorization approach for
personalized ranking. The optimization criterion is:

  L = ∑ -ln σ(x̂_uij) + λ||Θ||²

where x̂_uij = x̂_ui - x̂_uj represents the difference between
positive and negative item scores.

We use embedding dimension d=64, learning rate η=0.001,
regularization λ=0.01, and batch size 256.
```

### 输出（Blueprint 片段）

```yaml
file_structure:
  - path: "config.py"
    priority: 1
    description: "Configuration with embed_dim=64, lr=0.001, reg=0.01"

  - path: "models/bpr_mf.py"
    priority: 3
    description: "BPR-MF model implementation"

implementation_components:
  - name: "BPR Loss"
    file: "models/loss.py"
    formula: "L = ∑ -ln σ(x̂_ui - x̂_uj) + λ||Θ||²"
    implementation_notes:
      - "Use torch.sigmoid for σ"
      - "Use torch.mean for summation"
      - "Add L2 regularization term"

environment_setup:
  dependencies:
    - torch>=2.0
  hyperparameters:
    embed_dim: 64
    learning_rate: 0.001
    regularization: 0.01
    batch_size: 256
```

---

## 小结

```
Blueprint 是什么？
  → 论文的"施工图纸"，把杂乱信息整理成结构化计划

包含什么？
  → 文件结构、组件规格、验证方案、环境配置、实现策略

怎么生成的？
  → 3 个 Agent 协作:
     Concept Agent (宏观) + Algorithm Agent (微观) → Planning Agent (整合)

代码在哪？
  → prompts/code_prompts.py 定义各 Agent 的 Prompt
  → agent_orchestration_engine.py 协调执行
```

---

## 下一步

Blueprint 生成后，接下来是代码生成阶段。其中 CodeMem 是关键组件：

**→ [04-CodeMem代码记忆.md](./04-CodeMem代码记忆.md)**
