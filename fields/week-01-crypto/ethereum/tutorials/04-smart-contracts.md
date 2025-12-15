# 智能合约

## 一句话大白话

**智能合约就是存在区块链上的自动执行程序——你按按钮，它就按照写好的规则执行，谁都改不了，谁都骗不了。**

就像自动售货机：投币 + 按按钮 = 出货。没有人能干预这个过程，机器不会赖账，也不会多收你钱。

---

## 它解决什么问题

### 核心问题：如何让协议自动执行，无需信任对方？

传统合同的问题：
- 需要信任对方会履约
- 需要法律和法院来强制执行
- 跨国执行困难
- 中间人可能作恶

**智能合约的解决方案**：
- 规则写在代码里，部署后不可更改
- 满足条件自动执行，不需要任何人批准
- 全网节点执行同一段代码，结果必然一致
- 「代码即法律」—— Code is Law

### 经典应用场景

| 场景 | 传统方式 | 智能合约方式 |
|------|---------|-------------|
| 众筹 | 平台托管，可能跑路 | 达到目标自动转账，未达标自动退款 |
| 遗嘱 | 需要律师、法院 | 条件触发自动分配资产 |
| 保险 | 理赔需要申请、审核 | 条件满足自动赔付（如航班延误险） |
| 交易 | 需要交易所、担保 | 原子交换，要么全成功要么全失败 |

---

## 什么时候用 / 什么时候别用

### ✅ 适合用智能合约

| 场景 | 原因 |
|------|------|
| 资产托管和分配 | 规则透明，无需信任 |
| 去中心化金融（DeFi） | 24/7运行，无需许可 |
| 代币发行 | 标准化、可组合 |
| 链上治理投票 | 透明、不可篡改 |
| 数字身份和凭证 | 可验证、跨平台 |

### ❌ 不适合用智能合约

| 场景 | 原因 |
|------|------|
| 需要实时修改规则 | 合约部署后难以修改 |
| 涉及主观判断 | 代码只能处理客观条件 |
| 需要保密的业务逻辑 | 合约代码公开可见 |
| 高频、低延迟场景 | 区块链速度有限 |
| 需要依赖大量链外数据 | 预言机问题复杂 |

---

## 它不是什么

### 常见误解

| 误解 | 真相 |
|------|------|
| 「智能合约很智能」 | 它只是按代码执行，没有任何判断能力 |
| 「智能合约是法律合同」 | 它是程序代码，法律效力取决于司法管辖区 |
| 「智能合约无法更改」 | 可以通过代理模式、升级机制等设计为可升级 |
| 「智能合约是安全的」 | 代码可能有漏洞，历史上有大量被黑事件 |
| 「智能合约可以主动执行」 | 必须被交易触发，不会自己运行 |

---

## 最小例子

### 最简单的智能合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 这是一个最简单的存储合约
contract SimpleStorage {
    // 状态变量：存储在区块链上
    uint256 public storedNumber;

    // 函数：写入数据（需要发交易，消耗 Gas）
    function set(uint256 _number) public {
        storedNumber = _number;
    }

    // 函数：读取数据（不需要发交易，免费）
    function get() public view returns (uint256) {
        return storedNumber;
    }
}
```

### 合约结构解析

```
┌─────────────────────────────────────────────────────────────────┐
│  合约文件结构                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  // 1. 许可证声明（必须）                                        │
│  // SPDX-License-Identifier: MIT                                │
│                                                                  │
│  // 2. 编译器版本（必须）                                        │
│  pragma solidity ^0.8.0;                                        │
│                                                                  │
│  // 3. 导入其他合约（可选）                                      │
│  import "@openzeppelin/contracts/token/ERC20/ERC20.sol";        │
│                                                                  │
│  // 4. 合约定义                                                  │
│  contract MyContract {                                          │
│      // 4.1 状态变量（存储在链上）                               │
│      uint256 public value;                                      │
│      mapping(address => uint256) public balances;               │
│                                                                  │
│      // 4.2 事件（用于记录日志）                                 │
│      event ValueChanged(uint256 newValue);                      │
│                                                                  │
│      // 4.3 修饰器（复用的检查逻辑）                             │
│      modifier onlyOwner() { ... }                               │
│                                                                  │
│      // 4.4 构造函数（部署时执行一次）                           │
│      constructor() { ... }                                      │
│                                                                  │
│      // 4.5 函数                                                │
│      function doSomething() public { ... }                      │
│  }                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 一个实际的例子：简易众筹合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleCrowdfunding {
    // ============ 状态变量 ============
    address public owner;           // 项目方地址
    uint256 public goal;            // 众筹目标
    uint256 public deadline;        // 截止时间
    uint256 public totalRaised;     // 已筹集金额

    // 记录每个人的捐款
    mapping(address => uint256) public contributions;

    // 众筹状态
    bool public goalReached;
    bool public fundsClaimed;

    // ============ 事件 ============
    event ContributionMade(address indexed contributor, uint256 amount);
    event GoalReached(uint256 totalAmount);
    event FundsClaimed(address owner, uint256 amount);
    event RefundClaimed(address contributor, uint256 amount);

    // ============ 修饰器 ============
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    modifier beforeDeadline() {
        require(block.timestamp < deadline, "Crowdfunding has ended");
        _;
    }

    modifier afterDeadline() {
        require(block.timestamp >= deadline, "Crowdfunding still active");
        _;
    }

    // ============ 构造函数 ============
    constructor(uint256 _goal, uint256 _durationInDays) {
        owner = msg.sender;
        goal = _goal;
        deadline = block.timestamp + (_durationInDays * 1 days);
    }

    // ============ 核心功能 ============

    // 捐款
    function contribute() public payable beforeDeadline {
        require(msg.value > 0, "Must send some ETH");

        contributions[msg.sender] += msg.value;
        totalRaised += msg.value;

        emit ContributionMade(msg.sender, msg.value);

        // 检查是否达到目标
        if (totalRaised >= goal && !goalReached) {
            goalReached = true;
            emit GoalReached(totalRaised);
        }
    }

    // 项目方提取资金（仅在达到目标后）
    function claimFunds() public onlyOwner afterDeadline {
        require(goalReached, "Goal not reached");
        require(!fundsClaimed, "Funds already claimed");

        fundsClaimed = true;
        uint256 amount = address(this).balance;

        (bool success, ) = owner.call{value: amount}("");
        require(success, "Transfer failed");

        emit FundsClaimed(owner, amount);
    }

    // 退款（仅在未达目标时）
    function claimRefund() public afterDeadline {
        require(!goalReached, "Goal was reached, no refunds");
        require(contributions[msg.sender] > 0, "No contribution to refund");

        uint256 amount = contributions[msg.sender];
        contributions[msg.sender] = 0;  // 防止重入攻击

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Refund failed");

        emit RefundClaimed(msg.sender, amount);
    }

    // ============ 查询函数 ============

    function getTimeLeft() public view returns (uint256) {
        if (block.timestamp >= deadline) return 0;
        return deadline - block.timestamp;
    }

    function getProgress() public view returns (uint256) {
        return (totalRaised * 100) / goal;  // 返回百分比
    }
}
```

### 调用合约的 JavaScript 代码

```javascript
const { ethers } = require('ethers');

// 合约 ABI（应用二进制接口）
const abi = [
    "function contribute() payable",
    "function claimFunds()",
    "function claimRefund()",
    "function totalRaised() view returns (uint256)",
    "function goal() view returns (uint256)",
    "function contributions(address) view returns (uint256)",
    "event ContributionMade(address indexed contributor, uint256 amount)"
];

async function interactWithContract() {
    // 连接到以太坊
    const provider = new ethers.JsonRpcProvider('YOUR_RPC_URL');
    const wallet = new ethers.Wallet('YOUR_PRIVATE_KEY', provider);

    // 连接到合约
    const contractAddress = '0x...'; // 合约地址
    const contract = new ethers.Contract(contractAddress, abi, wallet);

    // 读取数据（免费，不需要 Gas）
    const goal = await contract.goal();
    const raised = await contract.totalRaised();
    console.log(`目标: ${ethers.formatEther(goal)} ETH`);
    console.log(`已筹: ${ethers.formatEther(raised)} ETH`);

    // 捐款（需要 Gas）
    const tx = await contract.contribute({
        value: ethers.parseEther("0.1")  // 捐 0.1 ETH
    });
    console.log('交易哈希:', tx.hash);

    // 等待确认
    const receipt = await tx.wait();
    console.log('交易已确认，区块号:', receipt.blockNumber);

    // 监听事件
    contract.on("ContributionMade", (contributor, amount, event) => {
        console.log(`${contributor} 捐款了 ${ethers.formatEther(amount)} ETH`);
    });
}
```

---

## 新手最常踩的 3 个坑

### 坑 1：重入攻击（Reentrancy）

**这是什么**：
```solidity
// 有漏洞的代码
function withdraw() public {
    uint256 amount = balances[msg.sender];

    // 危险！先转账后更新状态
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);

    balances[msg.sender] = 0;  // 如果攻击者在转账时再次调用 withdraw...
}
```

**攻击原理**：
```
攻击者合约的 receive() 函数：
┌────────────────────────────────────┐
│  receive() external payable {      │
│      if (目标合约余额 > 0) {        │
│          目标合约.withdraw();       │  <- 在收到 ETH 时再次调用
│      }                              │
│  }                                  │
└────────────────────────────────────┘

执行流程：
1. 攻击者调用 withdraw()
2. 合约检查余额：100 ETH ✓
3. 合约转账给攻击者
4. 攻击者的 receive() 被触发，再次调用 withdraw()
5. 合约检查余额：还是 100 ETH（还没更新！）
6. 合约再次转账...
7. 循环直到掏空
```

**正确做法**：
```solidity
// 方法1：检查-生效-交互模式（CEI Pattern）
function withdraw() public {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;  // 先更新状态！

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}

// 方法2：使用重入锁
bool private locked;
modifier noReentrant() {
    require(!locked, "No reentrancy");
    locked = true;
    _;
    locked = false;
}
```

### 坑 2：整数溢出（历史问题，0.8.0 后已修复）

```solidity
// Solidity 0.8.0 之前
uint8 x = 255;
x = x + 1;  // 结果是 0，不是 256！（溢出）

// Solidity 0.8.0 之后
// 默认会检查溢出并 revert
// 如果确定不会溢出且想省 Gas，可以用 unchecked
unchecked {
    x = x + 1;  // 不检查溢出
}
```

**建议**：
- 使用 Solidity 0.8.0 或更高版本
- 如果必须用旧版本，使用 OpenZeppelin 的 SafeMath 库

### 坑 3：不理解 `public` / `external` / `internal` / `private`

```solidity
contract VisibilityExample {
    // public: 任何人都可调用，自动生成 getter
    uint256 public publicVar;

    // private: 只有本合约可访问
    uint256 private privateVar;

    // internal: 本合约和继承合约可访问
    uint256 internal internalVar;

    // 函数可见性
    function publicFunc() public { }     // 任何人可调用
    function externalFunc() external { } // 只能从外部调用（不能内部调用）
    function internalFunc() internal { } // 本合约和继承合约
    function privateFunc() private { }   // 只有本合约

    // 常见错误：以为 private 就是「安全」的
    // 真相：区块链上的数据全部公开，private 只是不能通过合约调用读取
    // 但任何人都可以直接读取存储槽！
}
```

**重点理解**：
```
┌─────────────────────────────────────────────────────┐
│  private ≠ 加密                                     │
│                                                     │
│  区块链上没有隐私！                                  │
│  private 变量只是不能通过合约接口访问                │
│  但任何人都可以直接读取存储槽的数据                  │
│                                                     │
│  如果真的需要隐私：                                  │
│  - 使用零知识证明                                   │
│  - 使用链下计算 + 链上验证                          │
│  - 使用专门的隐私链                                 │
└─────────────────────────────────────────────────────┘
```

---

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                    智能合约在系统中的位置                            │
└─────────────────────────────────────────────────────────────────────┘

  用户/DApp
      │
      │ 发送交易（调用合约函数）
      v
┌─────────────┐
│   交易      │
│  ├─ to: 合约地址
│  ├─ data: 函数调用数据
│  └─ value: 附带的 ETH
└─────────────┘
      │
      │ 被打包进区块
      v
┌─────────────────────────────────────────────────────────────────────┐
│                           EVM 执行                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │ 加载合约    │ --> │ 解析调用    │ --> │ 执行字节码  │           │
│  │   代码      │     │   数据      │     │             │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│                                                 │                   │
│                                                 v                   │
│                           ┌─────────────────────────────────┐       │
│                           │  [你在这里学习的内容]            │       │
│                           │  智能合约的：                    │       │
│                           │  ├─ 状态变量（存储）             │       │
│                           │  ├─ 函数（逻辑）                 │       │
│                           │  ├─ 事件（日志）                 │       │
│                           │  └─ 修饰器（检查）               │       │
│                           └─────────────────────────────────┘       │
│                                                 │                   │
│                                                 v                   │
│                           ┌─────────────────────────────────┐       │
│                           │  更新状态 / 触发事件 / 返回结果  │       │
│                           └─────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 自测题

### 基础理解

1. **智能合约为什么叫「智能」？它真的智能吗？**

<details>
<summary>参考答案</summary>

「智能」其实是个历史误导。这个概念由 Nick Szabo 在 1990 年代提出，当时的「智能」指的是：
- 能够**自动执行**协议条款
- 不需要人工干预
- 条件满足就执行，像自动售货机

但它**不是**人工智能意义上的「智能」：
- 没有学习能力
- 没有判断能力
- 只是机械地执行代码
- 代码写错了也会「忠实」地执行错误逻辑

更准确的叫法应该是「自动执行合约」或「程序化合约」。
</details>

2. **为什么说智能合约一旦部署就「不可更改」？真的完全无法修改吗？**

<details>
<summary>参考答案</summary>

「不可更改」的含义：
- 合约的字节码部署到某个地址后，该地址的代码永远不变
- 这保证了规则的确定性

但可以通过设计实现「可升级」：
1. **代理模式**：用户和代理合约交互，代理合约把调用转发给逻辑合约，可以更换逻辑合约地址
2. **数据分离**：数据存在一个合约，逻辑存在另一个合约
3. **治理机制**：通过投票决定是否升级

权衡：
- 可升级 = 灵活，但引入了信任假设（谁能升级？）
- 不可升级 = 去信任化，但有 bug 也无法修复

DeFi 项目通常会：
- 初期可升级（快速迭代）
- 成熟后放弃升级权限（完全去信任化）
</details>

3. **什么是 ABI？为什么调用合约需要 ABI？**

<details>
<summary>参考答案</summary>

ABI = Application Binary Interface（应用二进制接口）

它是什么：
- 描述合约有哪些函数、参数类型、返回值
- 定义如何编码/解码调用数据
- 类似于 API 文档，但是机器可读的格式

为什么需要：
- 合约在链上是字节码，人类看不懂
- 调用合约时，需要把 `transfer(address,uint256)` 编码成字节
- ABI 告诉客户端如何做这个编码

例子：
```javascript
// 调用 transfer(0x123..., 100)
// 编码后的 data:
// 0xa9059cbb  <- 函数选择器（函数签名的前4字节哈希）
// 000000000000000000000000123...  <- 地址参数（32字节）
// 0000000000000000000000000000000000000000000000000000000000000064  <- 数量（100的十六进制）
```
</details>

### 进阶思考

4. **如果让你设计一个去中心化的遗嘱合约，你会考虑哪些问题？**

<details>
<summary>参考答案</summary>

核心问题：

1. **如何证明持有人已经去世？**
   - 预言机？但谁来提供这个数据？
   - 死人开关：N 天不活动就触发
   - 多签见证人机制

2. **隐私问题**
   - 遗嘱内容是否应该公开？
   - 受益人地址公开会有问题
   - 可能需要零知识证明

3. **执行时机**
   - 区块链合约无法主动执行
   - 需要有人（或 Keeper）来触发

4. **资产类型**
   - 只能处理链上资产
   - 现实资产（房产、股票）需要法律配合

5. **争议处理**
   - 如果受益人对分配有异议怎么办？
   - 可能需要链下仲裁机制

6. **可撤销性**
   - 遗嘱应该可以更新
   - 但要防止被强迫修改

这个例子展示了智能合约的局限：
- 链上只能处理链上资产
- 依赖链外数据就要信任预言机
- 涉及人的行为就有不确定性
</details>
