# 单点穿透案例：证明你知道一个数的平方根

## 案例背景

### 业务场景

想象你正在参加一个数学竞赛的资格赛。主办方给出一个大数 N（比如 961），要求参赛者证明自己能算出它的平方根，但不能直接说出答案（防止其他人抄答案）。

**需求**：
- 证明你知道 x 使得 x² = 961
- 不告诉任何人 x 的值
- 主办方能验证你确实知道答案

### 为什么这是一个好的学习案例？

```
复杂度适中:
  ✓ 简单到能完整理解每一步
  ✓ 复杂到能展示 ZKP 的所有核心概念

涵盖全流程:
  问题定义 → 电路设计 → R1CS → 可信设置 → 证明 → 验证
```

---

## 流程演练

### 节点 1：问题定义 (Statement)

**输入**：
- 业务需求："证明我知道 961 的平方根"

**加工**：
- 形式化为数学命题

**输出**：
```
Statement: 我知道秘密 x，使得 x² = 961

其中:
- 公开输入: y = 961
- 私密输入 (witness): x = ?（只有证明者知道是 31）
- 关系: x² = y
```

**检查点**：
- [x] 公开输入是什么？→ 961
- [x] 私密输入是什么？→ 平方根 x
- [x] 约束关系是什么？→ x² = y

**常见失败原因**：
1. 把应该保密的值放到公开输入中
2. 约束关系写错（比如写成 x = y²）
3. 忘记考虑负数（-31 也是 961 的平方根）

---

### 节点 2：电路设计 (Circuit)

**输入**：
- Statement: x² = y

**加工**：
- 把数学关系转换为算术电路

**输出**：

```javascript
// square_root.circom
pragma circom 2.0.0;

template SquareRoot() {
    // 私密输入：平方根
    signal input x;

    // 公开输入：被开方数
    signal input y;

    // 中间变量：平方结果
    signal x_squared;

    // 计算 x²
    x_squared <== x * x;

    // 约束：x² 必须等于 y
    x_squared === y;
}

component main {public [y]} = SquareRoot();
```

**电路图表示**：

```
         x (私密输入)
         │
         │
    ┌────┴────┐
    │         │
    ↓         ↓
┌───────────────┐
│       ×       │  乘法门
└───────┬───────┘
        │
        ↓
    x² (中间变量)
        │
        ↓
┌───────────────┐
│      ===      │  等式约束
└───────┬───────┘
        │
        ↓
    y (公开输入 = 961)
```

**检查点**：
- [x] 电路有几个门？→ 1 个乘法门 + 1 个等式约束
- [x] 需要几个信号？→ 3 个 (x, y, x_squared)
- [x] 约束数量？→ 2 个

**常见失败原因**：
1. 使用 `<--` 而不是 `<==`，导致没有约束
2. 忘记标记公开输入 `{public [y]}`
3. 试图直接用 `x * x === y`（语法错误）

---

### 节点 3：编译为 R1CS

**输入**：
- circom 电路代码

**加工**：
```bash
# 编译命令
circom square_root.circom --r1cs --wasm --sym -o build
```

**输出**：
- `build/square_root.r1cs`：约束系统
- `build/square_root.wasm`：witness 计算器
- `build/square_root.sym`：符号表

**R1CS 约束分析**：

```
见证向量: w = [1, y, x, x_squared]
             [常数, 公开输入, 私密输入, 中间变量]

约束 1: x × x = x_squared
  L = [0, 0, 1, 0]  → L·w = x
  R = [0, 0, 1, 0]  → R·w = x
  O = [0, 0, 0, 1]  → O·w = x_squared

约束 2: x_squared × 1 = y
  L = [0, 0, 0, 1]  → L·w = x_squared
  R = [1, 0, 0, 0]  → R·w = 1
  O = [0, 1, 0, 0]  → O·w = y

实际数值验证 (x=31, y=961):
  w = [1, 961, 31, 961]

  约束 1: 31 × 31 = 961 ✓
  约束 2: 961 × 1 = 961 ✓
```

**检查点**：
- [x] R1CS 生成成功？→ 查看 `snarkjs r1cs info`
- [x] 约束数量符合预期？→ 2 个约束
- [x] 信号数量正确？→ 4 个信号

**常见失败原因**：
1. circom 版本不对
2. 路径问题导致文件找不到
3. 语法错误没有修复

---

### 节点 4：可信设置 (Trusted Setup)

**输入**：
- R1CS 文件

**加工**：

```bash
# 阶段 1: Powers of Tau
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau \
    --name="First contribution" -v
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v

# 阶段 2: 电路特定设置
snarkjs groth16 setup build/square_root.r1cs pot12_final.ptau \
    square_root_0000.zkey
snarkjs zkey contribute square_root_0000.zkey square_root_final.zkey \
    --name="Final contribution" -v

# 导出验证密钥
snarkjs zkey export verificationkey square_root_final.zkey \
    verification_key.json
```

**输出**：
- `square_root_final.zkey`：证明密钥 (pk)
- `verification_key.json`：验证密钥 (vk)

**检查点**：
- [x] ptau 文件生成成功？
- [x] zkey 文件生成成功？
- [x] verification_key.json 存在？

**常见失败原因**：
1. ptau 的 power (12) 太小，不够支持电路大小
2. 忘记 prepare phase2 步骤
3. 贡献随机性时中断

---

### 节点 5：生成 Witness

**输入**：
- 私密值：x = 31
- 公开值：y = 961

**加工**：

```bash
# 准备输入文件
echo '{"x": 31, "y": 961}' > input.json

# 计算 witness
snarkjs wtns calculate build/square_root.wasm input.json witness.wtns

# (可选) 查看 witness
snarkjs wtns export json witness.wtns witness.json
```

**输出**：
- `witness.wtns`：完整的 witness 向量

```json
// witness.json 内容
[
    "1",      // 常数
    "961",    // y (公开输入)
    "31",     // x (私密输入)
    "961"     // x_squared (中间变量)
]
```

**检查点**：
- [x] witness 生成成功？
- [x] 中间变量计算正确？→ 31² = 961 ✓
- [x] 约束满足？

**常见失败原因**：
1. 输入 JSON 格式错误
2. 字段名拼写错误
3. 输入值不满足约束（比如 x=30 就会失败）

---

### 节点 6：生成证明 (Prove)

**输入**：
- witness.wtns
- square_root_final.zkey（证明密钥）

**加工**：

```bash
snarkjs groth16 prove square_root_final.zkey witness.wtns \
    proof.json public.json
```

**输出**：
- `proof.json`：零知识证明
- `public.json`：公开输入/输出

```json
// proof.json 结构
{
    "pi_a": ["12345...", "67890...", "1"],
    "pi_b": [["...", "..."], ["...", "..."], ["1", "0"]],
    "pi_c": ["...", "...", "1"],
    "protocol": "groth16",
    "curve": "bn128"
}

// public.json
["961"]  // 只有公开输入 y
```

**检查点**：
- [x] proof.json 生成成功？
- [x] public.json 只包含公开值？→ 不包含 x=31
- [x] proof 大小？→ 约 200 字节

**常见失败原因**：
1. zkey 和 witness 不匹配
2. witness 不满足约束
3. 内存不足（大电路）

---

### 节点 7：验证证明 (Verify)

**输入**：
- proof.json
- public.json
- verification_key.json

**加工**：

```bash
snarkjs groth16 verify verification_key.json public.json proof.json
```

**输出**：
```
[INFO]  snarkJS: OK!
```

**链上验证**：

```bash
# 导出 Solidity 验证合约
snarkjs zkey export solidityverifier square_root_final.zkey verifier.sol

# 生成调用参数
snarkjs zkey export soliditycalldata public.json proof.json
```

```solidity
// verifier.sol 使用示例
contract ProofVerifier {
    Groth16Verifier verifier = new Groth16Verifier();

    function verifySquareRoot(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[1] memory input  // input[0] = 961
    ) public view returns (bool) {
        return verifier.verifyProof(a, b, c, input);
    }
}
```

**检查点**：
- [x] 本地验证通过？→ OK!
- [x] Solidity 合约生成？
- [x] 验证者不知道 x=31？→ public.json 只有 961

**常见失败原因**：
1. verification_key 和 proof 不匹配（用了不同的 zkey）
2. public.json 被篡改
3. 网络问题导致文件下载不完整

---

## 完整脚本

```bash
#!/bin/bash

# 完整的零知识证明演示脚本

echo "========== 1. 创建电路 =========="
mkdir -p zkp_demo && cd zkp_demo

cat > square_root.circom << 'EOF'
pragma circom 2.0.0;

template SquareRoot() {
    signal input x;
    signal input y;
    signal x_squared;

    x_squared <== x * x;
    x_squared === y;
}

component main {public [y]} = SquareRoot();
EOF

echo "========== 2. 编译电路 =========="
circom square_root.circom --r1cs --wasm --sym -o build

echo "========== 3. 可信设置 =========="
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau \
    --name="Demo" -v -e="random entropy"
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v

snarkjs groth16 setup build/square_root.r1cs pot12_final.ptau sr_0000.zkey
snarkjs zkey contribute sr_0000.zkey sr_final.zkey \
    --name="Demo" -v -e="more entropy"
snarkjs zkey export verificationkey sr_final.zkey vkey.json

echo "========== 4. 生成 Witness =========="
echo '{"x": 31, "y": 961}' > input.json
snarkjs wtns calculate build/square_root.wasm input.json witness.wtns

echo "========== 5. 生成证明 =========="
snarkjs groth16 prove sr_final.zkey witness.wtns proof.json public.json

echo "========== 6. 验证证明 =========="
snarkjs groth16 verify vkey.json public.json proof.json

echo ""
echo "========== 完成! =========="
echo "证明文件: proof.json"
echo "公开输入: $(cat public.json)"
echo "私密输入 x=31 没有泄露！"
```

---

## 常见坑点提醒

### 坑点 1：把私密值标记为公开

```javascript
// 错误示例
component main {public [x, y]} = SquareRoot();
// x 应该是私密的！

// 正确示例
component main {public [y]} = SquareRoot();
```

### 坑点 2：忘记检查负数

```javascript
// 问题：-31 也是 961 的平方根
// 如果业务需要正数，要添加约束

template PositiveSquareRoot() {
    signal input x;
    signal input y;

    // 范围检查：确保 x 在合理范围内
    // 使用 circomlib 的 LessThan
    component lt = LessThan(64);
    lt.in[0] <== x;
    lt.in[1] <== 2**63;  // 确保不是负数的模表示
    lt.out === 1;

    signal x_squared;
    x_squared <== x * x;
    x_squared === y;
}
```

### 坑点 3：测试用例不充分

```javascript
// 应该测试的用例：
// 1. 正确答案: x=31, y=961 ✓
// 2. 错误答案: x=30, y=961 ✗ (应该失败)
// 3. 边界情况: x=0, y=0 ✓
// 4. 大数: x=1000000, y=1000000000000 ✓
```

---

## 复盘

### 我学到的 3 件事

1. **ZKP 流程是固定的**
   - 不管多复杂的问题，都是：电路 → R1CS → 设置 → 证明 → 验证
   - 掌握这个流程，就能处理各种 ZKP 应用

2. **约束是安全的核心**
   - `<==` 同时做赋值和约束
   - `<--` 只赋值不约束，必须谨慎使用
   - 每个计算都需要约束来保证正确性

3. **工具链很重要**
   - circom 写电路，snarkjs 做证明
   - 理解工具的输入输出，调试更容易

### 仍不确定的 3 件事

1. **可信设置的 Power 怎么选？**
   - `bn128 12` 中的 12 代表什么？
   - → 答：2^12 = 4096，决定了支持的最大约束数

2. **大规模电路怎么优化？**
   - 这个例子只有 2 个约束，真实应用有几十万个
   - → 研究方向：并行计算、GPU 加速、电路优化

3. **递归证明是什么？**
   - 听说可以"证明证明"，用于压缩更多数据
   - → 下一步学习方向

### 下一步要查的 3 个点

1. **circomlib 库的使用**
   - 学习现成的组件：比较器、哈希、签名验证
   - 链接：https://github.com/iden3/circomlib

2. **Groth16 协议原理**
   - 理解 QAP 转换
   - 理解配对运算为什么能验证

3. **实际应用案例**
   - 研究 Tornado Cash 的电路
   - 研究 zkSync 的架构

---

## 验收任务回顾

回到最初的验收任务：

> **独立使用 circom 编写一个"证明你知道某个数的平方根"的零知识电路，生成证明并验证，同时能解释为什么验证者无法从证明中获取原始数值。**

### 完成情况

1. ✅ 使用 circom 编写了电路
2. ✅ 成功生成并验证了证明
3. ✅ 能解释零知识性

### 为什么验证者学不到 x=31？

```
验证者拿到的信息:
  - verification_key.json (公开参数)
  - public.json: ["961"]
  - proof.json: {pi_a, pi_b, pi_c}

验证者不知道的信息:
  - x = 31 (在 witness 中，从未发送)
  - x_squared 的计算过程

零知识性的保证:
  1. witness 从未离开证明者的机器
  2. 证明 π 是由随机数混淆的
  3. 从 π 中反推 witness 在计算上不可行
  4. 即使验证者想穷举，也没有任何优势
```

恭喜完成零知识证明的入门学习！
