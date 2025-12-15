# zk-STARKs

## 一句话大白话

**不需要可信设置的零知识证明，用哈希函数代替椭圆曲线，抗量子计算攻击。**

如果 SNARKs 需要一个"启动仪式"才能开始（像成立公司需要股东大会），那 STARKs 就是"说干就干"，不需要任何预先准备，而且不怕量子计算机。代价是证明会大一些。

## 它解决什么问题

### 核心问题：可信设置的信任假设

SNARKs（特别是 Groth16）的最大争议点：
1. **可信设置的"有毒废料"**：如果泄露，系统就不安全了
2. **信任参与者**：必须相信至少一个参与者是诚实的
3. **量子威胁**：依赖椭圆曲线，量子计算机可以攻破

**STARKs 的突破**：
- 透明设置（Transparent）：不需要任何可信设置
- 后量子安全：只依赖哈希函数，量子计算机也攻不破

### 使用场景

1. **需要最高透明度**：不想依赖任何信任假设
2. **为量子时代做准备**：长期安全性要求
3. **zkVM/zkEVM**：StarkNet、Cairo 语言
4. **大规模计算**：证明生成可以很高效

## STARK 名字的含义

```
zk-STARK = Zero-Knowledge Scalable Transparent ARgument of Knowledge

拆解:
- Zero-Knowledge: 零知识性
- Scalable:       可扩展（证明生成准线性时间）
- Transparent:    透明（无需可信设置）
- ARgument:       论证
- of Knowledge:   知识证明
```

## 什么时候用 / 什么时候别用

### 适合使用 STARKs

| 场景 | 原因 |
|------|------|
| 不能接受可信设置 | 核心优势 |
| 需要后量子安全 | 只依赖哈希函数 |
| 证明大规模计算 | 证明生成效率高 |
| 需要透明性 | 完全公开可验证 |

### 不适合使用 STARKs

| 场景 | 原因 |
|------|------|
| 对证明大小敏感 | 证明比 SNARKs 大很多 |
| 链上验证 gas 敏感 | 验证计算量更大 |
| 需要极致简洁 | SNARKs 证明更小 |

## SNARKs vs STARKs 对比

```
┌────────────────────┬────────────────────┬────────────────────┐
│       特性         │      SNARKs        │      STARKs        │
├────────────────────┼────────────────────┼────────────────────┤
│   可信设置         │   需要             │   不需要 ✓         │
│   量子安全         │   否               │   是 ✓             │
│   证明大小         │   ~200B ✓          │   ~50-200KB        │
│   验证时间         │   ~3ms ✓           │   ~10-50ms         │
│   证明生成         │   O(n·log n)       │   O(n·log n) ✓     │
│   密码学假设       │   椭圆曲线         │   仅哈希函数 ✓     │
│   成熟度           │   高               │   快速发展中       │
└────────────────────┴────────────────────┴────────────────────┘

总结: SNARKs 追求简洁，STARKs 追求透明和安全
```

## 它不是什么

### 常见混淆点

| 误解 | 真相 |
|------|------|
| "STARK 一定比 SNARK 好" | 各有优劣，看场景 |
| "STARK 证明很大没法用" | 对于大计算，大小可以接受 |
| "STARK 很新不成熟" | StarkNet 已经在生产环境运行 |
| "STARK 计算效率低" | 证明生成效率其实很高 |

## 最小例子：理解 STARK 的核心思想

### STARK 的理论基础

STARK 基于三个核心技术：

```
┌─────────────────────────────────────────────────────────────────┐
│                      STARK 技术栈                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. AIR (Algebraic Intermediate Representation)                │
│      │                                                          │
│      └──→ 把计算表示为多项式约束                                 │
│                                                                 │
│   2. FRI (Fast Reed-Solomon IOP of Proximity)                   │
│      │                                                          │
│      └──→ 证明多项式的"低度性"                                   │
│                                                                 │
│   3. Merkle Tree + Hash                                         │
│      │                                                          │
│      └──→ 把交互式证明变成非交互式                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### AIR：代数中间表示

```
与 R1CS 不同，STARK 使用 AIR 来表示计算

AIR 约束的形式:
  P(trace[i], trace[i+1], ..., trace[i+k]) = 0

trace = 计算执行轨迹（一系列状态）

例子：斐波那契数列
  约束: trace[i+2] - trace[i+1] - trace[i] = 0

  trace = [1, 1, 2, 3, 5, 8, 13, ...]
  检验: 2 - 1 - 1 = 0 ✓
        3 - 2 - 1 = 0 ✓
        ...
```

### FRI 协议简介

FRI（Fast Reed-Solomon Interactive Oracle Proof of Proximity）是 STARK 的核心：

```
核心思想:
  如果一个函数可以用低度多项式表示，
  那么它的值在随机点上的表现也"接近"低度多项式。

工作方式:
  1. 证明者提交多项式的评估值（用 Merkle 树）
  2. 验证者随机挑战
  3. 证明者"折叠"多项式，度数减半
  4. 重复，直到度数足够低可以直接检验

FRI 让验证者可以高效地检验"证明者的多项式确实是低度的"
```

### Python 概念演示

```python
import hashlib
from typing import List, Tuple

class SimpleFRI:
    """
    简化版 FRI 概念演示（非实际安全）
    """

    def __init__(self, prime: int = 97):
        self.p = prime

    def commit(self, values: List[int]) -> str:
        """用 Merkle 根承诺一组值"""
        # 简化：直接哈希所有值
        data = ",".join(map(str, values))
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def fold(self, values: List[int], challenge: int) -> List[int]:
        """
        FRI 折叠操作：把 n 个值变成 n/2 个
        f(x) → g(x) = (f(x) + f(-x))/2 + challenge * (f(x) - f(-x))/(2x)
        简化版本
        """
        n = len(values)
        new_values = []
        for i in range(n // 2):
            v1 = values[i]
            v2 = values[n // 2 + i]
            # 简化的折叠
            folded = (v1 + v2 + challenge * (v1 - v2)) % self.p
            new_values.append(folded)
        return new_values


def demonstrate_fri_concept():
    """演示 FRI 的基本思想"""
    fri = SimpleFRI()

    # 假设这是一个多项式的评估值
    # f(x) 在 x = 0, 1, 2, ..., 7 的值
    polynomial_evals = [1, 3, 7, 13, 21, 31, 43, 57]

    print("FRI 折叠演示")
    print("=" * 40)
    print(f"原始值 (n=8): {polynomial_evals}")
    print(f"承诺: {fri.commit(polynomial_evals)}")

    # 第一轮折叠
    challenge1 = 5
    round1 = fri.fold(polynomial_evals, challenge1)
    print(f"\n第1轮折叠 (challenge={challenge1})")
    print(f"折叠后 (n=4): {round1}")
    print(f"承诺: {fri.commit(round1)}")

    # 第二轮折叠
    challenge2 = 3
    round2 = fri.fold(round1, challenge2)
    print(f"\n第2轮折叠 (challenge={challenge2})")
    print(f"折叠后 (n=2): {round2}")
    print(f"承诺: {fri.commit(round2)}")

    # 最后一轮
    challenge3 = 7
    round3 = fri.fold(round2, challenge3)
    print(f"\n第3轮折叠 (challenge={challenge3})")
    print(f"最终值 (n=1): {round3}")

    print("\n验证者检验最终值是否为常数多项式（度=0）")


if __name__ == "__main__":
    demonstrate_fri_concept()
```

## STARKs 的优势详解

### 1. 透明性（Transparency）

```
SNARK (Groth16):
  CRS = (g^τ, g^τ², ..., g^τⁿ, ...)
  ↑
  τ 是"有毒废料"，必须销毁

STARK:
  公共参数 = 空！（或者只是哈希函数的选择）
  ↑
  完全透明，任何人都可以验证
```

### 2. 后量子安全

```
SNARK 依赖:
- 椭圆曲线离散对数问题
- 双线性配对
↓
量子计算机可以用 Shor 算法攻破

STARK 只依赖:
- 抗碰撞哈希函数
↓
量子计算机需要 Grover 算法
只能提供平方级加速，增加哈希输出长度即可防御
```

### 3. 可扩展性

```
STARK 的证明生成:
  时间: O(n · log n)  ← 准线性，非常高效
  空间: O(n)

STARK 的验证:
  时间: O(log² n)     ← 多对数，亚线性

这意味着: 证明越大的计算，STARK 的优势越明显
```

## Cairo 和 StarkNet

Cairo 是专门为 STARK 设计的编程语言：

```python
# Cairo 代码示例
# 计算斐波那契数列第 n 项

func fibonacci(n: felt) -> felt {
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    let a = fibonacci(n - 1);
    let b = fibonacci(n - 2);
    return a + b;
}

# 'felt' = field element，有限域元素
```

## 新手最常踩的 3 个坑

### 坑 1：被证明大小劝退

**错误想法**："STARK 证明那么大（50KB+），肯定不实用"

**真相**：
```
对于小计算:
  SNARK: 200B，STARK: 50KB → SNARK 完胜

对于大计算 (100万步):
  证明大小差距相对减小
  STARK 的证明生成更快
  链下验证场景 STARK 更合适
```

### 坑 2：混淆 STARK 和 StarkNet

```
STARK: 零知识证明技术
StarkNet: 使用 STARK 的 L2 区块链

类比:
  STARK ≈ 发动机技术
  StarkNet ≈ 使用这种发动机的汽车品牌
```

### 坑 3：以为 STARK 完全不需要任何设置

**误解**：STARK 真的什么准备都不需要

**真相**：虽然不需要"可信"设置，但还是需要：
- 选择哈希函数
- 选择有限域
- 确定 AIR 约束

这些是"透明设置"——任何人都可以验证，不需要信任任何人。

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────┐
│                     零知识证明系统全景图                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   算术电路                                                       │
│      │                                                          │
│      ├──────────────────────────────────────┐                   │
│      ↓                                      ↓                   │
│   R1CS                                     AIR                  │
│      │                                      │                   │
│      ↓                                      ↓                   │
│   ┌────────────┐                     ┌───────────┐              │
│   │  SNARKs    │                     │【你在这里】│              │
│   │ (Groth16)  │                     │  STARKs   │              │
│   └────────────┘                     └───────────┘              │
│      │                                      │                   │
│      │   ← 需要可信设置                      │ ← 透明设置 ✓      │
│      │   ← 证明小 ✓                         │ ← 证明大          │
│      │   ← 量子不安全                        │ ← 量子安全 ✓      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 自测题

1. **概念题**：解释 STARK 中 "Transparent" 的含义。与 SNARK 的可信设置有什么本质区别？

2. **对比题**：在什么场景下你会选择 STARK 而不是 SNARK？给出至少两个理由。

3. **技术题**：为什么 STARK 被认为是"后量子安全"的？量子计算机对 SNARK 和 STARK 的威胁有什么不同？

---

<details>
<summary>点击查看答案</summary>

1. **Transparent 的含义**：
   - STARK 的所有参数都是公开的，可以由任何人独立生成和验证
   - 不存在任何需要被"信任"的秘密
   - 与 SNARK 的本质区别：
     - SNARK（Groth16）需要可信设置，产生必须销毁的"有毒废料"τ
     - STARK 只依赖公开的哈希函数，没有任何秘密参数
     - SNARK 的安全依赖"至少一个参与者诚实"
     - STARK 的安全只依赖密码学假设（哈希函数抗碰撞）

2. **选择 STARK 的场景**：
   - **不能接受任何信任假设**：监管机构或对安全性要求极高的场景
   - **需要后量子安全**：政府机密、长期保存的数据、金融基础设施
   - **大规模计算证明**：证明生成效率高，适合 zkVM/zkEVM
   - **透明度要求高**：需要完全可审计的系统
   - **证明大小不敏感**：链下验证、批量验证场景

3. **后量子安全分析**：
   - **SNARK 的威胁**：
     - 依赖椭圆曲线离散对数问题
     - 量子计算机可用 Shor 算法在多项式时间内攻破
     - 一旦大规模量子计算机出现，SNARK 完全失效
   - **STARK 的优势**：
     - 只依赖哈希函数的抗碰撞性
     - 量子计算机只能用 Grover 算法获得平方级加速
     - 对于 256 位哈希，量子攻击需要 2^128 次操作，仍然不可行
     - 如果担心，只需增加哈希输出长度

</details>
