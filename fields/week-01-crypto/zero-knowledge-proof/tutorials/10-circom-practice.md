# circom 实战

## 一句话大白话

**circom 是写零知识电路的专用语言，就像写程序一样定义你要证明什么，然后工具自动帮你生成证明系统。**

如果说 Python 是写普通程序的语言，那 circom 就是写"可证明程序"的语言。你定义计算逻辑，它帮你生成能证明这个计算正确执行的系统。

## 它解决什么问题

### 核心问题：如何方便地构建 ZKP 电路？

手写 R1CS 约束太痛苦：
- 需要手动管理变量
- 容易出错
- 难以复用

**circom 的价值**：
- 用高级语言写电路
- 自动编译为 R1CS
- 配合 snarkjs 生成和验证证明

### 使用场景

1. **学习 ZKP**：最友好的入门工具
2. **快速原型**：快速验证想法
3. **生产级应用**：zkSync、Polygon 等都用 circom
4. **自定义逻辑**：实现特定业务的零知识证明

## circom 工具链

```
┌─────────────────────────────────────────────────────────────────┐
│                     circom + snarkjs 工具链                      │
└─────────────────────────────────────────────────────────────────┘

  circuit.circom                 ← 你写的电路代码
       │
       ▼ (circom 编译器)
       │
       ├──→ circuit.r1cs        ← R1CS 约束系统
       │
       ├──→ circuit.wasm        ← WebAssembly (计算 witness)
       │
       └──→ circuit.sym         ← 符号表 (调试用)
       │
       ▼ (snarkjs: 可信设置)
       │
       ├──→ proving_key.zkey    ← 证明密钥
       │
       └──→ verification_key.json ← 验证密钥
       │
       ▼ (snarkjs: 证明)
       │
       └──→ proof.json + public.json ← 证明和公开输入
```

## 什么时候用 / 什么时候别用

### 适合使用 circom

| 场景 | 原因 |
|------|------|
| 学习 ZKP | 工具成熟，文档丰富 |
| 快速开发 | 比手写约束快很多 |
| 需要 Groth16 | 原生支持 |
| 需要链上验证 | 可导出 Solidity 验证合约 |

### 不太适合 circom

| 场景 | 原因 |
|------|------|
| 需要 STARK | circom 主要用于 SNARK |
| 超大规模电路 | 编译时间可能很长 |
| 需要递归证明 | 支持有限 |

## 最小例子

### 环境安装

```bash
# 1. 安装 circom 编译器
# macOS
brew install circom

# 或者从源码编译
git clone https://github.com/iden3/circom.git
cd circom
cargo build --release
cargo install --path circom

# 2. 安装 snarkjs
npm install -g snarkjs
```

### 第一个电路：证明乘法

```javascript
// multiplier.circom
pragma circom 2.0.0;

// 模板定义
template Multiplier() {
    // 声明信号
    signal input a;    // 私密输入
    signal input b;    // 私密输入
    signal output c;   // 公开输出

    // 约束：c = a * b
    c <== a * b;
}

// 主组件
component main = Multiplier();
```

### 完整工作流程

```bash
# 1. 编译电路
circom multiplier.circom --r1cs --wasm --sym -o ./build

# 输出:
#   build/multiplier.r1cs    (约束系统)
#   build/multiplier.wasm    (计算 witness)
#   build/multiplier.sym     (符号表)

# 2. 查看电路信息
snarkjs r1cs info build/multiplier.r1cs
# Curve: bn-128
# # of Wires: 4
# # of Constraints: 1
# # of Private Inputs: 2
# # of Public Inputs: 0
# # of Outputs: 1

# 3. Powers of Tau (可信设置第一阶段)
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First contribution" -v
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v

# 4. 电路特定设置 (第二阶段)
snarkjs groth16 setup build/multiplier.r1cs pot12_final.ptau multiplier_0000.zkey
snarkjs zkey contribute multiplier_0000.zkey multiplier_final.zkey --name="Final contribution" -v
snarkjs zkey export verificationkey multiplier_final.zkey verification_key.json

# 5. 准备输入
echo '{"a": 3, "b": 11}' > input.json

# 6. 计算 witness
snarkjs wtns calculate build/multiplier.wasm input.json witness.wtns

# 7. 生成证明
snarkjs groth16 prove multiplier_final.zkey witness.wtns proof.json public.json

# 8. 验证证明
snarkjs groth16 verify verification_key.json public.json proof.json
# [INFO]  snarkJS: OK!

# 9. (可选) 导出 Solidity 验证合约
snarkjs zkey export solidityverifier multiplier_final.zkey verifier.sol
```

### 查看生成的证明

```json
// proof.json
{
  "pi_a": ["123...", "456...", "1"],
  "pi_b": [["789...", "012..."], ["345...", "678..."], ["1", "0"]],
  "pi_c": ["901...", "234...", "1"],
  "protocol": "groth16",
  "curve": "bn128"
}

// public.json (公开输出)
["33"]  // 因为 3 * 11 = 33
```

## circom 语法详解

### 信号类型

```javascript
signal input a;          // 输入信号（默认私密）
signal private input b;  // 显式私密输入
signal output c;         // 输出信号（公开）
signal intermediate;     // 中间信号
```

### 操作符

```javascript
// 赋值 + 约束
c <== a * b;   // 等价于: c <-- a * b; c === a * b;

// 只赋值（危险！需要单独添加约束）
c <-- a * b;

// 只约束（信号必须已有值）
c === a * b;

// 算术运算
signal sum;
sum <== a + b;

signal diff;
diff <== a - b;

signal prod;
prod <== a * b;

// 注意：除法需要特殊处理
// 不能直接用 a / b，需要用乘法逆元
```

### 模板和组件

```javascript
// 定义模板
template Add() {
    signal input a;
    signal input b;
    signal output sum;
    sum <== a + b;
}

// 使用组件
template Calculator() {
    signal input x;
    signal input y;
    signal output result;

    // 实例化组件
    component adder = Add();
    adder.a <== x;
    adder.b <== y;
    result <== adder.sum;
}
```

### 数组和循环

```javascript
template SumArray(n) {
    signal input arr[n];
    signal output sum;

    signal partial[n];

    partial[0] <== arr[0];
    for (var i = 1; i < n; i++) {
        partial[i] <== partial[i-1] + arr[i];
    }

    sum <== partial[n-1];
}

// 使用
component main = SumArray(5);
```

### 条件逻辑（选择器模式）

```javascript
// circom 没有 if-else，用选择器实现
template Select() {
    signal input selector;  // 0 或 1
    signal input a;
    signal input b;
    signal output out;

    // 如果 selector=1 则 out=a，否则 out=b
    out <== selector * a + (1 - selector) * b;

    // 确保 selector 是二进制
    selector * (1 - selector) === 0;
}
```

## 实战项目：证明哈希原像

```javascript
// hash_preimage.circom
pragma circom 2.0.0;

include "circomlib/circuits/poseidon.circom";

template HashPreimage() {
    // 私密输入：原像
    signal input preimage;

    // 公开输入：哈希值
    signal input hash;

    // 计算哈希
    component hasher = Poseidon(1);
    hasher.inputs[0] <== preimage;

    // 约束：计算的哈希等于公开的哈希
    hasher.out === hash;
}

component main {public [hash]} = HashPreimage();
```

### 使用流程

```bash
# 1. 安装 circomlib
npm install circomlib

# 2. 编译（指定 circomlib 路径）
circom hash_preimage.circom --r1cs --wasm --sym -o ./build -l node_modules

# 3. 计算哈希值（使用 JavaScript）
node -e "
const { buildPoseidon } = require('circomlibjs');
(async () => {
    const poseidon = await buildPoseidon();
    const hash = poseidon.F.toString(poseidon([42]));
    console.log('Hash of 42:', hash);
})();
"
# 输出: Hash of 42: 14744269619966411208579211824598458697587494354926760081771325075741142829156

# 4. 准备输入
echo '{
    "preimage": 42,
    "hash": "14744269619966411208579211824598458697587494354926760081771325075741142829156"
}' > input.json

# 5. 后续步骤同前...
```

## 常用的 circomlib 组件

```javascript
// 比较器
include "circomlib/circuits/comparators.circom";
component lt = LessThan(32);    // a < b
component eq = IsEqual();       // a == b
component gt = GreaterThan(32); // a > b

// 位操作
include "circomlib/circuits/bitify.circom";
component n2b = Num2Bits(256);  // 数字转位数组
component b2n = Bits2Num(256);  // 位数组转数字

// 哈希
include "circomlib/circuits/poseidon.circom";
component hash = Poseidon(2);   // Poseidon 哈希

include "circomlib/circuits/mimcsponge.circom";
component mimc = MiMCSponge(2, 220, 1);

// 签名
include "circomlib/circuits/eddsamimc.circom";
component sig = EdDSAMiMCVerifier();

// Merkle 树
include "circomlib/circuits/mux1.circom";
component mux = Mux1();         // 二选一多路复用器
```

## 新手最常踩的 3 个坑

### 坑 1：只赋值不约束

```javascript
// 危险！没有约束的赋值
signal output out;
out <-- a * b;  // 恶意证明者可以给 out 任意值！

// 正确做法
signal output out;
out <== a * b;  // 赋值 + 约束
```

### 坑 2：非二次约束

```javascript
// 错误：三个变量相乘
signal output out;
out <== a * b * c;  // 编译错误！

// 正确：拆分为多个二次约束
signal temp;
temp <== a * b;
out <== temp * c;
```

### 坑 3：信号只能赋值一次

```javascript
// 错误：重复赋值
signal x;
x <== a;
x <== b;  // 编译错误！

// 正确：使用不同的信号
signal x1;
signal x2;
x1 <== a;
x2 <== b;
```

## 调试技巧

```javascript
// 1. 使用 log 输出（只在 witness 生成时有效）
log("a =", a);
log("b =", b);

// 2. 使用 assert 检查
assert(a > 0);

// 3. 查看约束数量
// circom xxx.circom --r1cs
// snarkjs r1cs info xxx.r1cs
```

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────┐
│                     零知识证明系统全景图                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────┐                                                 │
│   │【你在这里】│ ← 实践层：把理论变成代码                         │
│   │  circom   │                                                 │
│   └───────────┘                                                 │
│         │                                                       │
│         ↓                                                       │
│   编译 → R1CS → 可信设置 → 证明/验证                             │
│         │                                                       │
│         ├── 理论：算术电路、R1CS、SNARKs                         │
│         │                                                       │
│         └── 应用：隐私交易、身份验证、zkRollup                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

circom 是把 ZKP 理论变成实践的桥梁。掌握它，你就能真正动手构建零知识证明应用。

## 自测题

1. **语法题**：`<==` 和 `<--` 有什么区别？什么时候用 `<--`？

2. **实践题**：写一个 circom 电路，证明你知道两个数 a 和 b，使得 a² + b² = c（勾股定理）

3. **调试题**：以下代码有什么问题？
   ```javascript
   template BadCircuit() {
       signal input x;
       signal output y;
       y <-- x * x * x;  // 计算 x³
   }
   ```

---

<details>
<summary>点击查看答案</summary>

1. **`<==` vs `<--` 的区别**：
   - `<==`：赋值 + 约束（推荐使用）
   - `<--`：只赋值，不产生约束（危险）

   `<--` 的使用场景：
   - 当计算不是简单的二次表达式时（如除法、开方）
   - 必须配合单独的 `===` 约束使用

   ```javascript
   // 例：计算除法
   signal quotient;
   quotient <-- a / b;      // 赋值
   quotient * b === a;      // 约束：验证 quotient 确实是 a/b
   ```

2. **勾股定理电路**：
   ```javascript
   pragma circom 2.0.0;

   template Pythagorean() {
       signal input a;
       signal input b;
       signal input c;  // 公开输入

       signal a_squared;
       signal b_squared;

       a_squared <== a * a;
       b_squared <== b * b;

       // 约束：a² + b² = c
       a_squared + b_squared === c;
   }

   component main {public [c]} = Pythagorean();
   ```

   测试输入：`{"a": 3, "b": 4, "c": 25}`（因为 9 + 16 = 25）

3. **问题分析**：
   - `y <-- x * x * x` 只是赋值，没有约束
   - 恶意证明者可以给 y 任意值，声称它是 x³
   - 没有任何约束验证 y 确实等于 x³

   **正确做法**：
   ```javascript
   template GoodCircuit() {
       signal input x;
       signal output y;

       signal x_squared;
       x_squared <== x * x;    // 有约束
       y <== x_squared * x;    // 有约束
   }
   ```

</details>
