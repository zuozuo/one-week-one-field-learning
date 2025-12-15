# Witness（见证）

## 一句话大白话

**Witness 就是证明者知道的"秘密答案"，是让整个电路能算通的那组私密数据。**

就像数独游戏：公开的是部分已填的数字（公开输入），你需要证明你知道完整的正确答案（witness），但又不想直接展示答案。

## 它解决什么问题

### 核心问题：什么是"知识证明"中的"知识"？

零知识证明的全称是"零知识**知识证明**"（Zero-Knowledge **Proof of Knowledge**）：
- **知识**：就是 witness
- **证明**：证明你真的"知道"这个 witness
- **零知识**：验证者学不到 witness 的任何信息

```
类比:
  - 数独答案 = witness
  - 部分已知数字 = 公开输入
  - 证明规则满足 = 验证
```

### 使用场景

1. **密码/私钥**：证明你知道某个账户的私钥
2. **原像证明**：证明你知道某个哈希值的原像
3. **交易细节**：隐私币中隐藏的金额和地址
4. **数据库查询**：证明查询结果正确，但不暴露数据

## 什么时候用 / 什么时候别用

### Witness 的使用原则

```
判断是否放入 witness:
  Q: 这个值需要对验证者保密吗？

  如果是 → 放入 witness（私密输入）
  如果否 → 放入 public input（公开输入）
```

### 常见分类

| 数据类型 | 是否保密 | 放在哪里 |
|---------|---------|---------|
| 私钥 | 保密 | witness |
| 交易金额 | 可能保密 | witness |
| 哈希值 | 公开 | public input |
| 签名结果 | 公开 | public input |
| 中间计算值 | 保密 | witness |

## 它不是什么

### 常见混淆点

| 误解 | 真相 |
|------|------|
| "witness = 所有变量" | witness 只是私密输入 |
| "witness 会发给验证者" | witness 永远不离开证明者 |
| "witness 越大证明越大" | SNARK 证明大小与 witness 无关 |
| "没有 witness 就没有 ZKP" | 有些证明不需要隐藏任何东西 |

## 最小例子

### 例子 1：证明我知道密码

```
场景: 网站验证用户身份，但不想接收明文密码

公开输入:
  - password_hash = "a1b2c3..."  (存储在服务器的哈希)

私密输入 (witness):
  - password = "mysecret123"  (用户知道的密码)

电路逻辑:
  Hash(password) === password_hash

零知识性:
  服务器知道用户确实知道正确密码
  服务器学不到密码是什么
```

### 例子 2：证明我有足够余额

```
场景: 证明我有至少 1000 元，但不暴露具体金额

公开输入:
  - threshold = 1000  (最低要求)
  - balance_commitment  (余额的承诺值)

私密输入 (witness):
  - balance = 5678  (实际余额)
  - randomness = "xxx"  (承诺的随机数)

电路逻辑:
  1. Commit(balance, randomness) === balance_commitment
  2. balance >= threshold

零知识性:
  验证者知道余额 >= 1000
  验证者不知道具体是多少
```

### 代码示例：circom 中的 witness

```javascript
pragma circom 2.0.0;

// 证明我知道两个数的乘积
template Multiplier() {
    // 私密输入 (witness)
    signal private input a;
    signal private input b;

    // 公开输入
    signal input expected_product;

    // 中间变量（也是 witness 的一部分）
    signal product;

    // 计算
    product <== a * b;

    // 约束：乘积必须等于期望值
    product === expected_product;
}

component main = Multiplier();
```

### 见证生成过程

```javascript
// 输入文件 input.json
{
    "a": 3,          // 私密
    "b": 11,         // 私密
    "expected_product": 33  // 公开
}

// 生成 witness
// snarkjs 会执行电路，计算所有中间值

// witness 向量结构
// w = [1, a, b, expected_product, product]
//   = [1, 3, 11, 33, 33]
//      ^  ^  ^   ^    ^
//      |  |  |   |    └── 中间变量
//      |  |  |   └─────── 公开输入
//      |  |  └────────── 私密输入
//      |  └───────────── 私密输入
//      └──────────────── 常数 1
```

## Witness 的完整性要求

### 正确的 witness 必须满足所有约束

```
给定:
  - 电路 C
  - 公开输入 x
  - witness w

要求:
  C(x, w) = true  (所有约束都满足)

如果找不到这样的 w:
  → 说明陈述是假的
  → 证明生成会失败
```

### Python 演示

```python
from typing import Dict, Tuple, Optional

class SimpleCircuit:
    """
    简单的电路示例：证明知道 a, b 使得 a * b = c
    """

    def __init__(self, public_input: int):
        self.expected_product = public_input

    def compute_witness(self, a: int, b: int) -> Optional[Dict]:
        """
        计算 witness

        Returns:
            如果输入有效，返回完整的 witness
            如果输入无效，返回 None
        """
        # 计算中间值
        product = a * b

        # 检查约束
        if product != self.expected_product:
            print(f"约束不满足: {a} * {b} = {product} != {self.expected_product}")
            return None

        # 返回完整的 witness
        return {
            "one": 1,              # 常数
            "a": a,                # 私密输入
            "b": b,                # 私密输入
            "expected": self.expected_product,  # 公开输入
            "product": product     # 中间变量
        }

    def verify_witness(self, witness: Dict) -> bool:
        """验证 witness 是否满足所有约束"""
        # 约束 1: product = a * b
        if witness["a"] * witness["b"] != witness["product"]:
            return False

        # 约束 2: product = expected
        if witness["product"] != witness["expected"]:
            return False

        return True


def demo():
    # 公开输入：乘积应该是 33
    circuit = SimpleCircuit(33)

    print("=== 正确的 witness ===")
    witness = circuit.compute_witness(3, 11)
    if witness:
        print(f"Witness: {witness}")
        print(f"验证结果: {circuit.verify_witness(witness)}")

    print("\n=== 错误的 witness ===")
    witness = circuit.compute_witness(4, 8)  # 4 * 8 = 32 ≠ 33
    if witness is None:
        print("无法生成有效的 witness")


if __name__ == "__main__":
    demo()
```

输出：
```
=== 正确的 witness ===
Witness: {'one': 1, 'a': 3, 'b': 11, 'expected': 33, 'product': 33}
验证结果: True

=== 错误的 witness ===
约束不满足: 4 * 8 = 32 != 33
无法生成有效的 witness
```

## Witness 向量的结构

在实际的 ZKP 系统中，witness 向量有特定的结构：

```
witness 向量 w = [1, public_inputs..., private_inputs..., intermediate_values...]
                 ^         ^                 ^                    ^
                 |         |                 |                    |
              常数项   公开输入          私密输入            中间计算值

Groth16 的验证:
  - 验证者知道: [1, public_inputs...]
  - 验证者不知道: [private_inputs..., intermediate_values...]
  - 验证者检查: 证明 π 与公开部分一致
```

## 新手最常踩的 3 个坑

### 坑 1：witness 泄露在公开输出中

**错误做法**：
```javascript
// 错误：直接输出 witness
signal private input secret;
signal output leaked_secret;
leaked_secret <== secret;  // 秘密直接变成公开输出！
```

**正确做法**：
```javascript
// 正确：输出秘密的哈希或承诺
signal private input secret;
signal output secret_hash;
secret_hash <== Hash(secret);  // 只暴露哈希
```

### 坑 2：从公开输入推断 witness

**风险场景**：
```javascript
// 如果 public = 4，很容易猜到 a=2, b=2
signal private input a;
signal private input b;
signal input public;
a * b === public;
```

**解决方案**：
- 确保 witness 的熵足够高
- 添加随机数（blinding factor）
- 使用承诺方案

### 坑 3：混淆"赋值"和"约束"

```javascript
// 在 circom 中:
a <-- b;     // 只是赋值，不产生约束（危险！）
a === b;     // 只是约束，不赋值
a <== b;     // 赋值 + 约束（推荐）

// 只赋值不约束的风险：
// 恶意证明者可以给 a 任意值，因为没有约束检查！
```

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────┐
│                     零知识证明系统全景图                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   证明者输入                                                     │
│   ┌────────────────────────────────────┐                       │
│   │  公开输入 (public input)           │ ← 验证者也知道        │
│   │  ┌───────────────────────────────┐ │                       │
│   │  │【你在这里】                    │ │                       │
│   │  │  私密输入 (witness)           │ │ ← 只有证明者知道      │
│   │  └───────────────────────────────┘ │                       │
│   └────────────────────────────────────┘                       │
│                    │                                            │
│                    ↓                                            │
│              电路执行 & 约束检查                                 │
│                    │                                            │
│                    ↓                                            │
│              证明生成 (witness 不离开证明者)                      │
│                    │                                            │
│                    ↓                                            │
│              验证 (只用公开输入和证明)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Witness 是零知识证明的核心——它是被"隐藏"的东西，是整个系统要保护的秘密。

## 自测题

1. **概念题**：在"证明我知道某个数的平方根"的场景中，什么是 witness？什么是公开输入？

2. **安全题**：下面的电路有什么安全问题？
   ```javascript
   signal private input password;
   signal input password_length;
   signal output is_valid;

   // 检查密码长度
   is_valid <== (CalculateLength(password) == password_length) ? 1 : 0;
   ```

3. **设计题**：设计一个电路的输入结构，用于"证明我知道一个数 x，使得 x³ + x + 5 = 35"。

---

<details>
<summary>点击查看答案</summary>

1. **平方根证明的输入结构**：
   - **Witness（私密输入）**：x = 3（平方根）
   - **公开输入**：9（被开方的数）
   - **电路约束**：x * x === 9

2. **安全问题**：
   - 泄露了密码长度！`password_length` 作为公开输入
   - 攻击者知道密码长度后，大大缩小了搜索空间
   - **正确做法**：不要把任何关于 witness 的信息作为公开输入
   ```javascript
   // 改进版：不暴露长度
   signal private input password;
   signal input password_hash;  // 只公开哈希
   Hash(password) === password_hash;
   ```

3. **x³ + x + 5 = 35 的输入结构**：
   ```javascript
   // 公开输入
   signal input target;  // = 35

   // 私密输入 (witness)
   signal private input x;  // = 3

   // 中间变量（自动成为 witness 的一部分）
   signal x_squared;
   signal x_cubed;
   signal result;

   // 电路
   x_squared <== x * x;           // x² = 9
   x_cubed <== x_squared * x;     // x³ = 27
   result <== x_cubed + x + 5;    // 27 + 3 + 5 = 35
   result === target;              // 约束
   ```

   Witness 向量：[1, 35, 3, 9, 27, 35]
   - 1: 常数
   - 35: 公开输入
   - 3: 私密输入 x
   - 9: 中间变量 x²
   - 27: 中间变量 x³
   - 35: 中间变量 result

</details>
