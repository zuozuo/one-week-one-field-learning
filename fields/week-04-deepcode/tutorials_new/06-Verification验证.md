# Verification 验证

> 代码写完了，能跑起来吗？

---

## 一句话定义

**Verification = 代码的"质检员"**

就像产品出厂前要经过质检，生成的代码也要经过验证。能运行、无报错、结果正确，才算合格。

---

## 为什么需要 Verification？

### 生成的代码不一定能跑

```
常见问题:

1. 语法错误
   ──────────
   def forward(self, x)    # 漏了冒号
       return self.fc(x)

2. 导入错误
   ──────────
   from model import Encoder  # 实际文件叫 models.py

3. 接口不匹配
   ──────────
   # model.py 定义: forward(self, user_id, item_id)
   # train.py 调用: model.forward(batch)  # 参数不对！

4. 依赖缺失
   ──────────
   import torch_geometric  # 没装这个包
```

### CodeMem 不能解决所有问题

```
CodeMem 记住了接口，但还是可能出错:

场景:
  CodeMem 记录: "Encoder.forward(x) -> Tensor"

  但 AI 生成 train.py 时:
    output = encoder.forward(input_ids, attention_mask)
                             ^^^^^^^^^^  ^^^^^^^^^^^^^^
                             多传了参数!

  原因: AI 可能"脑补"了额外参数

只有真正运行代码，才能发现这类问题
```

---

## Verification 怎么工作？

### 整体流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Verification 工作流程                            │
└─────────────────────────────────────────────────────────────────────┘

                    生成的代码文件
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 1: 运行代码                                                      │
│         执行 python train.py 或运行测试                               │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                            ┌─────────┴─────────┐
                            │                   │
                            ▼                   ▼
                    ┌───────────┐       ┌───────────┐
                    │  成功 ✓   │       │  失败 ✗   │
                    │           │       │           │
                    │ 结束!     │       │ 继续...   │
                    └───────────┘       └─────┬─────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 2: 分析错误                                                      │
│                                                                       │
│   错误信息:                                                           │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │ Traceback (most recent call last):                          │    │
│   │   File "train.py", line 23, in <module>                     │    │
│   │     from models.encoder import TransformerEncoder           │    │
│   │ ImportError: cannot import name 'TransformerEncoder'        │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│   分析结果:                                                           │
│   - 错误类型: ImportError                                             │
│   - 问题文件: train.py, line 23                                       │
│   - 原因: encoder.py 中类名可能不对                                   │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 3: 生成修复方案                                                  │
│                                                                       │
│   检查 encoder.py:                                                    │
│     发现类名是 Encoder，不是 TransformerEncoder                       │
│                                                                       │
│   修复方案:                                                           │
│     Option A: 修改 train.py 的 import 语句                            │
│     Option B: 修改 encoder.py 的类名                                  │
│                                                                       │
│   选择: Option A (修改使用方，不动底层实现)                           │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Step 4: 应用修复                                                      │
│                                                                       │
│   修改 train.py:                                                      │
│   - from models.encoder import TransformerEncoder                     │
│   + from models.encoder import Encoder                                │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ 返回 Step 1   │
                              │ 重新运行      │
                              │               │
                              │ (最多 N 次)   │
                              └───────────────┘
```

### 迭代修复

```
典型的修复过程:

第 1 轮:
  运行 → ImportError
  修复 → 改正 import 语句

第 2 轮:
  运行 → TypeError: forward() got unexpected argument
  修复 → 修正函数调用参数

第 3 轮:
  运行 → FileNotFoundError: data.csv
  修复 → 创建示例数据或修正路径

第 4 轮:
  运行 → 成功！✓

每一轮都在逼近可运行的代码
```

---

## 错误类型和处理

### 常见错误分类

```
┌─────────────────────────────────────────────────────────────────────┐
│                        错误类型分类                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Level 1: 语法错误 (Syntax Error)                                   │
│  ─────────────────────────────────                                  │
│  • 缺少冒号、括号不匹配、缩进错误                                    │
│  • 修复: 直接修正语法                                               │
│  • 难度: ⭐                                                         │
│                                                                     │
│  Level 2: 导入错误 (Import Error)                                   │
│  ─────────────────────────────────                                  │
│  • 模块不存在、类名错误、路径不对                                    │
│  • 修复: 检查文件结构，修正 import                                  │
│  • 难度: ⭐⭐                                                       │
│                                                                     │
│  Level 3: 类型错误 (Type Error)                                     │
│  ─────────────────────────────────                                  │
│  • 参数类型不对、返回值类型不匹配                                    │
│  • 修复: 检查接口定义，修正调用                                      │
│  • 难度: ⭐⭐⭐                                                     │
│                                                                     │
│  Level 4: 运行时错误 (Runtime Error)                                │
│  ─────────────────────────────────────                              │
│  • 数组越界、除零错误、内存不足                                      │
│  • 修复: 分析逻辑，添加检查或修正算法                               │
│  • 难度: ⭐⭐⭐⭐                                                   │
│                                                                     │
│  Level 5: 逻辑错误 (Logic Error)                                    │
│  ─────────────────────────────────                                  │
│  • 代码能跑，但结果不对                                             │
│  • 修复: 对照论文，检查算法实现                                      │
│  • 难度: ⭐⭐⭐⭐⭐                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 处理策略

```python
# 伪代码：错误处理策略

def handle_error(error: Exception, context: dict):
    error_type = classify_error(error)

    if error_type == "SyntaxError":
        # 直接修复语法
        fix = fix_syntax(error.lineno, error.text)

    elif error_type == "ImportError":
        # 检查文件结构和模块名
        fix = reconcile_imports(error.name, context.file_structure)

    elif error_type == "TypeError":
        # 检查 CodeMem 中的接口定义
        expected_interface = context.code_mem.get_interface(error.module)
        fix = align_call_with_interface(error.call, expected_interface)

    elif error_type == "RuntimeError":
        # 需要更深入分析
        fix = analyze_and_fix_runtime(error, context)

    return fix
```

---

## 验证脚本生成

### 自动生成测试

```
DeepCode 不只是运行代码，还会生成验证脚本:

Blueprint 中的验证方案:
┌─────────────────────────────────────────────────────────────────────┐
│ validation_approach:                                                │
│   - type: "unit_test"                                               │
│     target: "BPR Loss computation"                                  │
│     expected: "Loss should be positive and decrease during training"│
│                                                                     │
│   - type: "integration_test"                                        │
│     target: "Full training loop"                                    │
│     expected: "Model can complete one epoch without error"          │
│                                                                     │
│   - type: "metric_test"                                             │
│     target: "Recommendation accuracy"                               │
│     expected: "NDCG@10 > 0.1 on test set"                          │
└─────────────────────────────────────────────────────────────────────┘

生成的验证代码:
┌─────────────────────────────────────────────────────────────────────┐
│ # test_bpr_loss.py                                                  │
│                                                                     │
│ def test_bpr_loss_positive():                                       │
│     loss_fn = BPRLoss()                                             │
│     pos_scores = torch.tensor([0.8, 0.6, 0.9])                     │
│     neg_scores = torch.tensor([0.2, 0.3, 0.1])                     │
│     loss = loss_fn(pos_scores, neg_scores)                         │
│     assert loss > 0, "Loss should be positive"                      │
│                                                                     │
│ def test_training_loop():                                           │
│     model = RecommendationModel(config)                             │
│     trainer = Trainer(model, data)                                  │
│     trainer.train(epochs=1)  # Should not raise                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 代码在哪里？

### 核心模块

**文件**: `workflows/code_implementation_workflow.py`

```python
class CodeImplementationWorkflow:
    """
    代码实现工作流，包含验证逻辑

    核心方法:
    - run(): 执行完整工作流
    - verify_code(): 验证生成的代码
    - fix_errors(): 修复发现的错误
    """

    async def verify_code(self, code_path: str) -> VerificationResult:
        """
        验证生成的代码

        1. 运行语法检查
        2. 运行测试脚本
        3. 收集错误信息
        """
        # 运行代码
        result = await self._run_code(code_path)

        if result.success:
            return VerificationResult(success=True)

        # 分析错误
        error_analysis = self._analyze_error(result.error)

        return VerificationResult(
            success=False,
            error_type=error_analysis.type,
            error_message=error_analysis.message,
            suggested_fix=error_analysis.fix
        )

    async def fix_errors(
        self,
        errors: List[Error],
        max_iterations: int = 5
    ) -> bool:
        """
        迭代修复错误

        最多尝试 max_iterations 次
        """
        for i in range(max_iterations):
            # 生成修复
            fixes = await self._generate_fixes(errors)

            # 应用修复
            await self._apply_fixes(fixes)

            # 重新验证
            result = await self.verify_code(self.code_path)

            if result.success:
                logger.info(f"验证通过，共迭代 {i+1} 次")
                return True

            errors = result.errors

        logger.warning(f"达到最大迭代次数 {max_iterations}，仍有错误")
        return False
```

### 错误分析器

**文件**: `workflows/agents/verification_agent.py`

```python
class VerificationAgent:
    """
    验证代理，负责分析错误和生成修复方案
    """

    async def analyze_error(
        self,
        error_message: str,
        code_context: dict
    ) -> ErrorAnalysis:
        """
        分析错误信息，生成修复建议

        使用 LLM 理解错误上下文，提供智能修复
        """
        prompt = f"""
        分析以下错误并提供修复方案:

        错误信息:
        {error_message}

        相关代码:
        {code_context}

        请提供:
        1. 错误原因分析
        2. 具体修复步骤
        3. 修复后的代码
        """

        response = await self._call_llm(prompt)
        return self._parse_fix_response(response)
```

---

## 验证策略

### 渐进式验证

```
不是等所有文件生成完再验证，而是:

┌─────────────────────────────────────────────────────────────────────┐
│                      渐进式验证策略                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  生成 config.py                                                     │
│       │                                                             │
│       ▼                                                             │
│  验证 config.py ──────────────────────── 确保配置正确               │
│       │                                                             │
│       ▼                                                             │
│  生成 utils.py                                                      │
│       │                                                             │
│       ▼                                                             │
│  验证 utils.py + config.py 集成 ──────── 确保能一起工作             │
│       │                                                             │
│       ▼                                                             │
│  生成 model.py                                                      │
│       │                                                             │
│       ▼                                                             │
│  验证 model.py + utils + config ──────── 确保模型可实例化           │
│       │                                                             │
│       ▼                                                             │
│  ...                                                                │
│       │                                                             │
│       ▼                                                             │
│  全部生成后，运行完整测试                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

好处:
  - 早发现问题，早修复
  - 不会积累大量错误
  - 每一步都是可运行状态
```

---

## 实际效果

### 论文数据

```
Verification 的消融实验结果:

┌──────────────────────────────────────────────────────────────────────┐
│                    Verification 效果                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  无 Verification:                                                    │
│    代码生成后直接交付                                                │
│    成功率: 68.4%                                                     │
│                                                                      │
│  有 Verification (1 轮):                                             │
│    运行一次，修复一次                                                │
│    成功率: 72.1%    (+3.7%)                                         │
│                                                                      │
│  有 Verification (3 轮):                                             │
│    最多运行三次修复                                                  │
│    成功率: 75.9%    (+7.5%)                                         │
│                                                                      │
│  结论: 多轮验证修复显著提升成功率                                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 类比

```
类比：写作文

没有 Verification:
  写完就交
  可能有错别字、语法错误、逻辑不通

有 Verification:
  写完 → 检查 → 修改 → 再检查 → 再修改 → 交
  质量高得多

DeepCode 的 Verification 就像一个耐心的检查员
  发现问题 → 告诉你问题在哪 → 帮你改 → 再检查
```

---

## 小结

```
Verification 是什么？
  → 代码的"质检员"，确保能运行

怎么工作？
  → 运行代码 → 发现错误 → 分析原因 → 生成修复 → 重新运行
  → 迭代直到成功

处理哪些错误？
  → 语法错误、导入错误、类型错误、运行时错误、逻辑错误

什么时候验证？
  → 渐进式验证，每生成一个文件就验证一次

效果如何？
  → 多轮验证可提升 7.5% 的成功率

代码在哪？
  → workflows/code_implementation_workflow.py: 主工作流
  → workflows/agents/verification_agent.py: 错误分析
```

---

## 下一步

理论学完了，来看一个完整的实战案例：

**→ [07-单点穿透案例.md](./07-单点穿透案例.md)**
