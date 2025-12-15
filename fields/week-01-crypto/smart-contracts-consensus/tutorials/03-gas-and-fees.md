# Gas 和交易费用

## 一句话大白话

**Gas 就是以太坊的"汽油费"**：你想让网络帮你执行代码，就得付费。代码越复杂、存储越多，Gas 就越贵——这是防止有人写死循环卡死整个网络的机制。

---

## 它解决什么问题

### 如果没有 Gas 会怎样？

```
恶意用户写了一个合约：

while (true) {
    // 无限循环，永远不停
}

没有 Gas 的世界：
- 这段代码会永远运行
- 所有节点都卡死
- 整个网络瘫痪

有 Gas 的世界：
- 每执行一步都要付钱
- 钱花光了自动停止
- 网络继续正常运行
```

### Gas 的三个核心作用

| 作用 | 说明 |
|------|------|
| 防止滥用 | 恶意代码会因为 Gas 耗尽而停止 |
| 激励矿工/验证者 | Gas 费是节点的收入来源 |
| 资源定价 | 让计算和存储有合理的市场价格 |

---

## 什么时候用 / 什么时候别用

### ✅ 需要关注 Gas 的场景

- 部署合约时（部署很贵！）
- 设计合约架构时（影响长期成本）
- 用户体验优化（用户直接感受到费用）
- DeFi 交互时（热门时段可能极贵）

### ❌ 不需要关注 Gas 的场景

- 读取数据（`view`/`pure` 函数调用免费）
- 使用测试网（测试币免费领取）
- 链下计算（不上链的操作不花 Gas）

---

## 它不是什么（常见混淆点）

### ❌ Gas ≠ ETH

```
Gas 是计量单位，类似"公里数"
ETH 是支付货币，类似"人民币"

你不能说"这笔交易花了 100 Gas"
你应该说"这笔交易花了 21000 Gas，花费 0.001 ETH"

关系：
实际花费(ETH) = Gas 用量 × Gas 价格(Gwei)
```

### ❌ Gas Limit ≠ 实际消耗

```
Gas Limit：你愿意最多付多少（类似预算上限）
Gas Used：实际消耗了多少（类似实际花费）

例如：
- 你设置 Gas Limit = 100000
- 实际执行只用了 50000
- 你只付 50000 的费用，剩余 50000 退还
```

### ❌ Gas Price 高 ≠ 执行更快

```
错误理解：Gas 贵 = 代码跑得快
正确理解：Gas 贵 = 交易更快被打包

执行速度由代码决定，与 Gas Price 无关
Gas Price 影响的是：你的交易多快被矿工选中
```

---

## 最小例子

### Gas 计算公式

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   交易费用 = Gas Used × Gas Price                              │
│                                                                │
│   其中：                                                        │
│   - Gas Used: 实际消耗的计算量（由操作决定）                     │
│   - Gas Price: 单位 Gas 的价格（由市场供需决定）                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### EIP-1559 之后的费用结构

```
┌────────────────────────────────────────────────────────────────┐
│                    EIP-1559 费用模型                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   总费用 = Gas Used × (Base Fee + Priority Fee)                │
│                                                                │
│   ┌─────────────┐  ┌──────────────┐                           │
│   │  Base Fee   │  │ Priority Fee │                           │
│   │  (基础费)   │  │  (小费)      │                           │
│   ├─────────────┤  ├──────────────┤                           │
│   │ 由网络自动  │  │ 你自己设置   │                           │
│   │ 根据拥堵度  │  │ 越高越优先   │                           │
│   │ 调整        │  │ 被打包       │                           │
│   ├─────────────┤  ├──────────────┤                           │
│   │ 被销毁🔥    │  │ 给验证者     │                           │
│   └─────────────┘  └──────────────┘                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 常见操作的 Gas 消耗

| 操作 | Gas 消耗（大约） | 说明 |
|------|-----------------|------|
| 简单转账 | 21,000 | 最基础的操作 |
| ERC-20 转账 | 65,000 | 调用合约函数 |
| Uniswap 交易 | 150,000~300,000 | 复杂 DeFi 操作 |
| 部署简单合约 | 200,000~500,000 | 取决于代码长度 |
| NFT 铸造 | 100,000~200,000 | 包含存储操作 |

### 代码层面的 Gas 消耗

```solidity
// ===== 存储操作最贵！ =====

// 首次写入存储槽：20,000 Gas
uint256 public value;  // 从 0 改为非 0

// 修改已有存储：5,000 Gas
value = newValue;  // 从非 0 改为非 0

// 清零可以退还：退还 15,000 Gas（有上限）
value = 0;  // 从非 0 改为 0


// ===== 内存操作便宜 =====

function calculate() public pure returns (uint) {
    uint a = 1;      // 内存操作：3 Gas
    uint b = 2;      // 内存操作：3 Gas
    return a + b;    // 加法：3 Gas
}


// ===== 常见操作的 Gas 成本 =====

// 加减乘除：3 Gas
// 比较操作：3 Gas
// Keccak256：30 Gas + 6 Gas/字
// SLOAD（读存储）：2100 Gas（冷）/ 100 Gas（热）
// SSTORE（写存储）：20000 Gas（新）/ 5000 Gas（改）
```

### Gas 优化技巧示例

```solidity
// ===== 技巧1：用 calldata 代替 memory =====

// ❌ 消耗更多 Gas
function bad(string memory data) external { }

// ✅ 对于只读的外部函数参数
function good(string calldata data) external { }


// ===== 技巧2：打包存储变量 =====

// ❌ 占用 3 个存储槽（每槽 32 字节）
contract Bad {
    uint256 a;  // 槽 0
    uint128 b;  // 槽 1
    uint128 c;  // 槽 2
}

// ✅ 只占用 2 个存储槽
contract Good {
    uint256 a;  // 槽 0
    uint128 b;  // 槽 1（前 16 字节）
    uint128 c;  // 槽 1（后 16 字节）—— 打包在一起！
}


// ===== 技巧3：用 mapping 代替数组查找 =====

// ❌ O(n) 遍历，Gas 随数组增长
function findInArray(uint id) public view returns (bool) {
    for (uint i = 0; i < items.length; i++) {
        if (items[i].id == id) return true;
    }
    return false;
}

// ✅ O(1) 查找，Gas 固定
mapping(uint => bool) public exists;
function findInMapping(uint id) public view returns (bool) {
    return exists[id];
}


// ===== 技巧4：缓存存储变量 =====

// ❌ 多次读取存储（每次 2100 Gas）
function bad() public {
    for (uint i = 0; i < count; i++) {  // 读取 count N 次
        doSomething(i);
    }
}

// ✅ 缓存到内存（只读一次存储）
function good() public {
    uint _count = count;  // 读取一次到内存
    for (uint i = 0; i < _count; i++) {
        doSomething(i);
    }
}
```

---

## 新手最常踩的 3 个坑

### 坑 1：Gas Limit 设太低导致交易失败

**场景**：
```
你设置 Gas Limit = 21000（普通转账的量）
但你调用的是一个复杂合约函数
实际需要 80000 Gas
```

**结果**：
- 交易失败（Out of Gas）
- Gas 费照扣，一分不退！
- 什么也没干成，白花钱

**教训**：让钱包自动估算，或设置足够高的上限（多余会退还）

### 坑 2：高峰期发交易不看 Gas 价格

**场景**：
```
NFT 热门项目 mint 时
正常 Gas Price：30 Gwei
高峰期 Gas Price：300 Gwei

你没看价格直接发交易
一笔简单操作花了平时 10 倍的钱
```

**教训**：
- 使用 [etherscan.io/gastracker](https://etherscan.io/gastracker) 查看实时 Gas 价格
- 非紧急操作等低峰期（如美国凌晨）

### 坑 3：链上存储大量数据

**场景**：
```solidity
// 把用户的完整资料存链上
struct User {
    string name;        // 可能很长
    string bio;         // 可能更长
    string avatarUrl;   // 又一个长字符串
}
```

**结果**：
- 存一个用户可能花费几美元
- 合约很快变得无人用得起

**正确做法**：
```solidity
// 只存必要数据，其他放 IPFS
struct User {
    bytes32 contentHash;  // IPFS 哈希，固定 32 字节
    uint256 reputation;   // 必须上链的数据
}
```

---

## 流程图定位

Gas 在交易流程中的位置：

```
用户发起交易
      │
      ▼
┌─────────────────┐
│  设置 Gas 参数  │◀── Gas Limit（最多花多少）
│                 │◀── Max Fee（愿付的最高单价）
│                 │◀── Priority Fee（给验证者的小费）
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  交易进入       │
│  交易池(Mempool)│
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  验证者根据     │
│  Priority Fee   │──▶ 优先打包出价高的
│  排序选择       │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  EVM 执行合约   │
│  逐步消耗 Gas   │──▶ 每个操作都有 Gas 成本
└─────────────────┘
      │
      ├── Gas 用完前执行完成 ──▶ 成功，退还剩余 Gas
      │
      └── Gas 用完未执行完 ──▶ 失败，状态回滚，Gas 不退
```

---

## 自测题

### 基础题

1. **计算题**：一笔交易消耗了 50,000 Gas，Gas Price 是 30 Gwei。请问总费用是多少 ETH？
   <details>
   <summary>答案</summary>
   50,000 × 30 = 1,500,000 Gwei = 0.0015 ETH

   （1 ETH = 1,000,000,000 Gwei）
   </details>

2. **判断题**：如果交易因为 Gas 不足失败了，已消耗的 Gas 费会退还。（ ）
   <details>
   <summary>答案</summary>
   错误。即使交易失败，已消耗的 Gas 费不会退还。这是为了防止有人故意发送会失败的交易来消耗网络资源。
   </details>

3. **选择题**：以下哪个操作 Gas 消耗最高？
   - A. 两个数相加
   - B. 读取一个存储变量
   - C. 首次写入一个存储变量
   - D. 调用一个 pure 函数
   <details>
   <summary>答案</summary>
   C。首次写入存储槽需要约 20,000 Gas，是最昂贵的操作之一。
   </details>

### 优化题

4. **代码优化**：以下代码有什么 Gas 优化空间？

   ```solidity
   function sum(uint[] memory numbers) public pure returns (uint) {
       uint total = 0;
       for (uint i = 0; i < numbers.length; i++) {
           total += numbers[i];
       }
       return total;
   }
   ```

   <details>
   <summary>答案</summary>

   1. `memory` 改成 `calldata`（对于外部调用）
   2. 缓存 `numbers.length`
   3. 使用 `unchecked` 块（如果确定不会溢出）

   ```solidity
   function sum(uint[] calldata numbers) external pure returns (uint) {
       uint total = 0;
       uint len = numbers.length;
       for (uint i = 0; i < len; ) {
           total += numbers[i];
           unchecked { ++i; }  // 0.8.0+ 默认检查溢出，这里显式跳过
       }
       return total;
   }
   ```
   </details>

---

## 延伸阅读

- 上一篇：[Solidity 基础](02-solidity-basics.md)
- 下一篇：[ABI](04-abi.md)
- 工具：[Gas 追踪器](https://etherscan.io/gastracker)
