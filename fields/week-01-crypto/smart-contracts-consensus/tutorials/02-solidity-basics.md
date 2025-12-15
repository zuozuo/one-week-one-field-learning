# Solidity 基础

## 一句话大白话

**Solidity 就是用来写以太坊智能合约的编程语言**，语法长得像 JavaScript，但骨子里更像一个严格的"合同模板语言"——每一行代码都可能涉及真金白银。

---

## 它解决什么问题

### 为什么需要专门的语言？

普通编程语言（JavaScript、Python）无法满足智能合约的特殊需求：

| 需求 | 普通语言 | Solidity |
|------|----------|----------|
| 确定性执行 | 可能有随机性 | 同样输入必须同样输出 |
| Gas 计量 | 无此概念 | 每个操作都有 Gas 成本 |
| 货币原生支持 | 需要额外处理 | 内置 ETH 转账 |
| 安全类型系统 | 通常宽松 | 严格的类型检查 |
| 不可变性 | 可随时修改 | 编译后不可改 |

### Solidity 的定位

```
开发者 ─── 写 Solidity 代码 ──▶ 编译器 ──▶ 字节码 ──▶ EVM 执行
                                  │
                                  ▼
                           人能读懂            机器执行
```

---

## 什么时候用 / 什么时候别用

### ✅ 使用 Solidity

- 开发以太坊/EVM 兼容链的合约（Polygon、BSC、Arbitrum 等）
- 需要与现有 DeFi 协议交互
- 团队熟悉 JavaScript/Java 风格语法

### ❌ 考虑其他选择

| 场景 | 替代方案 |
|------|----------|
| 更安全/更严格 | Vyper（Python 风格，功能受限但更安全） |
| Solana 链 | Rust |
| Cosmos 链 | Go / Rust |
| 只是学习原理 | 先理解概念再学语法 |

---

## 它不是什么（常见混淆点）

### ❌ Solidity ≠ JavaScript

虽然语法相似，但：

```javascript
// JavaScript：这样写没问题
let x = 1;
x = "hello";  // 可以，动态类型

// Solidity：这样写直接报错
uint x = 1;
x = "hello";  // 错误！类型不匹配
```

### ❌ Solidity 不是图灵完备的

理论上 EVM 是图灵完备的，但实际上：
- Gas 限制了计算量
- 无法做到"无限循环"
- 这是**故意的**，防止网络被卡死

### ❌ Solidity 代码不是"私有"的

```
你以为：代码编译成字节码，别人看不懂
实际上：有工具可以反编译，而且源码通常会验证公开
```

---

## 最小例子

### 合约基本结构

```solidity
// SPDX-License-Identifier: MIT          // 1. 许可证声明（必须）
pragma solidity ^0.8.0;                   // 2. 版本声明（必须）

// 3. 引入其他文件（可选）
// import "./OtherContract.sol";

// 4. 合约定义
contract MyFirstContract {
    // ==================== 状态变量 ====================
    // 永久存储在区块链上，修改需要 Gas

    uint256 public count;           // 公开的计数器
    address public owner;           // 合约拥有者
    mapping(address => uint) public balances;  // 地址到余额的映射

    // ==================== 事件 ====================
    // 用于记录日志，方便前端监听

    event CountChanged(uint256 newCount, address changedBy);

    // ==================== 修饰符 ====================
    // 可复用的权限检查

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;  // 这里放被修饰的函数体
    }

    // ==================== 构造函数 ====================
    // 部署时执行一次

    constructor() {
        owner = msg.sender;
        count = 0;
    }

    // ==================== 函数 ====================

    // 增加计数（会修改状态，需要 Gas）
    function increment() public {
        count += 1;
        emit CountChanged(count, msg.sender);
    }

    // 读取计数（不修改状态，免费）
    function getCount() public view returns (uint256) {
        return count;
    }

    // 只有 owner 能调用的函数
    function reset() public onlyOwner {
        count = 0;
    }

    // 接收 ETH 的函数
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}
```

### 数据类型速查

```solidity
// ===== 值类型 =====
bool isActive = true;              // 布尔
uint256 amount = 100;              // 无符号整数（0 到 2^256-1）
int256 temperature = -10;          // 有符号整数
address wallet = 0x123...;         // 地址（20字节）
bytes32 hash = keccak256("hello"); // 固定长度字节

// ===== 引用类型 =====
string name = "Alice";             // 字符串
bytes data = hex"001122";          // 动态字节数组
uint[] numbers;                    // 动态数组
uint[5] fixedNumbers;              // 固定长度数组

// ===== 映射（最常用！）=====
mapping(address => uint) balances;           // 地址 → 余额
mapping(address => mapping(address => uint)) allowances; // 嵌套映射
```

### 函数可见性

```solidity
contract Visibility {
    // public: 内外都能调用，自动生成 getter
    function publicFunc() public {}

    // external: 只能从外部调用（不能用 this.）
    function externalFunc() external {}

    // internal: 只能内部或子合约调用
    function internalFunc() internal {}

    // private: 只能本合约内部调用
    function privateFunc() private {}
}
```

### 函数修饰符

```solidity
contract FunctionTypes {
    uint public data;

    // view: 读取状态但不修改
    function getData() public view returns (uint) {
        return data;  // ✅ 可以读
        // data = 1;  // ❌ 不能写
    }

    // pure: 不读也不写状态
    function add(uint a, uint b) public pure returns (uint) {
        return a + b;  // ✅ 只做计算
        // return data; // ❌ 不能读状态
    }

    // payable: 可以接收 ETH
    function deposit() public payable {
        // msg.value 是发送的 ETH 数量
    }

    // 默认（不写修饰符）: 可读可写，不能收 ETH
    function setData(uint _data) public {
        data = _data;
    }
}
```

---

## 新手最常踩的 3 个坑

### 坑 1：整数溢出（0.8.0 之前版本）

```solidity
// Solidity 0.7.x 及之前
uint8 x = 255;
x = x + 1;  // x 变成 0！（溢出）

// Solidity 0.8.0+ 自动检查溢出，会 revert
uint8 x = 255;
x = x + 1;  // 交易失败，抛出错误
```

**教训**：始终使用 0.8.0 以上版本，或使用 SafeMath 库。

### 坑 2：重入攻击

```solidity
// ❌ 危险代码！
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success, ) = msg.sender.call{value: amount}("");  // 先转账
    require(success);
    balances[msg.sender] = 0;  // 后更新状态
}

// 攻击者合约可以在收到钱时再次调用 withdraw()
// 因为 balances 还没更新，可以重复取钱！
```

```solidity
// ✅ 正确做法：先更新状态，再转账
function withdraw() public {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // 先更新状态
    (bool success, ) = msg.sender.call{value: amount}("");  // 后转账
    require(success);
}
```

**教训**：遵循"检查-生效-交互"（Checks-Effects-Interactions）模式。

### 坑 3：Gas 估算错误

```solidity
// ❌ 危险！循环次数不确定
function distributeToAll(address[] memory recipients) public {
    for (uint i = 0; i < recipients.length; i++) {
        // 如果 recipients 有 1000 人，可能超过区块 Gas 上限！
        payable(recipients[i]).transfer(1 ether);
    }
}

// ✅ 改用分批处理或让用户主动领取
mapping(address => uint) public pendingWithdrawals;

function claimReward() public {
    uint amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    payable(msg.sender).transfer(amount);
}
```

**教训**：
- 避免不确定长度的循环
- 让用户主动拉取（pull）而非合约主动推送（push）

---

## 流程图定位

Solidity 在开发流程中的位置：

```
需求分析 ──▶ 【编写 Solidity】 ──▶ 编译 ──▶ 部署 ──▶ 交互
                   │
                   │
           ┌───────▼───────┐
           │  .sol 文件    │
           │               │
           │  contract {   │
           │    ...        │
           │  }            │
           └───────────────┘
                   │
                   ▼
           ┌───────────────┐
           │  solc 编译器  │
           └───────────────┘
                   │
                   ▼
           ┌───────────────┐
           │  字节码 + ABI │
           └───────────────┘
```

---

## 自测题

### 基础题

1. **填空**：`view` 函数可以 ______ 状态变量，但不能 ______ 状态变量。
   <details>
   <summary>答案</summary>
   读取；修改
   </details>

2. **选择**：以下哪个函数可以接收 ETH？
   ```solidity
   function a() public {}
   function b() public view {}
   function c() public pure {}
   function d() public payable {}
   ```
   <details>
   <summary>答案</summary>
   D。只有 `payable` 修饰的函数才能接收 ETH。
   </details>

3. **判断**：`mapping` 可以遍历所有的键。（ ）
   <details>
   <summary>答案</summary>
   错误。Solidity 的 mapping 不支持遍历，如果需要遍历，需要额外维护一个键的数组。
   </details>

### 编码题

4. 写一个函数，实现"只有存过钱的人才能调用"的权限控制。

   <details>
   <summary>答案</summary>

   ```solidity
   mapping(address => uint) public deposits;

   modifier onlyDepositor() {
       require(deposits[msg.sender] > 0, "Must deposit first");
       _;
   }

   function deposit() public payable {
       deposits[msg.sender] += msg.value;
   }

   function specialFunction() public onlyDepositor {
       // 只有存过钱的人才能执行
   }
   ```
   </details>

---

## 延伸阅读

- 上一篇：[智能合约概念](01-smart-contract.md)
- 下一篇：[Gas 和交易费用](03-gas-and-fees.md)
- 相关：[实战案例 - ERC20 代币](case-study-erc20.md)
