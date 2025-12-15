# 智能合约 (Smart Contract)

## 一句话大白话

**智能合约就是存在区块链上的自动执行程序——满足条件就执行，谁也拦不住，谁也改不了。**

打个比方：自动贩卖机。你投币（满足条件）→ 掉出饮料（执行结果）。不需要店员，不需要信任，机器说了算。智能合约就是区块链上的「自动贩卖机」，但可以做比卖饮料复杂得多的事情。

---

## 它解决什么问题

### 传统问题：合约执行依赖信任

传统合约的问题：
- 「我付钱，你发货」→ 谁先？万一对方不履约？
- 需要中间人（担保、公证、法院）
- 执行成本高、速度慢、跨境更难

### 智能合约的解决方案

```
传统方式:
甲方 ←——信任?——→ 乙方
      ↓
    中间人（银行/法院）
      ↓
   高成本、慢、可能违约

智能合约方式:
甲方 ←——代码——→ 乙方
      ↓
   自动执行（无法违约）
      ↓
   低成本、快、确定性
```

**核心价值**：代码即法律，执行即结算，不可篡改，不可阻止。

---

## 什么时候用 / 什么时候别用

### 适合用智能合约的场景

| 场景 | 原因 |
|------|------|
| 金融交易 (DeFi) | 自动化、无需信任第三方 |
| 数字资产发行 | 代币、NFT 的创建和转移 |
| DAO 治理 | 投票结果自动执行 |
| 托管服务 | 条件满足自动释放资金 |

### 不适合用智能合约的场景

| 场景 | 原因 |
|------|------|
| 需要主观判断 | 合约只能处理链上数据和确定性逻辑 |
| 需要链下信息 | 合约无法直接访问现实世界（需要预言机） |
| 需要可撤销/修改 | 一旦部署，代码不可改变 |
| 复杂业务逻辑 | Gas 成本高，出错代价大 |

### 判断口诀
> 规则明确 + 条件可验证 + 执行确定 = 适合智能合约
> 需要人为判断 + 链下数据 + 可能反悔 = 不适合

---

## 它不是什么

### 常见误解

| 误解 | 事实 |
|------|------|
| 智能合约很「智能」 | 其实很「笨」，只能执行预设逻辑，没有 AI 能力 |
| 智能合约是法律合同 | 只是代码，不受法律直接约束（但执行结果可能有法律后果） |
| 智能合约不会出错 | 代码 bug 会被永久利用，已造成数十亿美元损失 |
| 部署后可以修改 | 默认不可修改（有可升级模式，但复杂且有风险） |
| 智能合约能获取任何数据 | 只能访问链上数据，链下数据需要预言机 |

---

## 最小例子

### 最简单的智能合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 一个最简单的存储合约
contract SimpleStorage {
    // 状态变量（存储在区块链上）
    uint256 public storedNumber;

    // 写入函数（改变状态，需要 Gas）
    function set(uint256 _number) public {
        storedNumber = _number;
    }

    // 读取函数（不改变状态，免费）
    function get() public view returns (uint256) {
        return storedNumber;
    }
}

/*
工作原理：
1. 合约部署到区块链，获得一个地址
2. 任何人调用 set(42) → storedNumber 变成 42 → 付 Gas
3. 任何人调用 get() → 返回 42 → 免费
4. storedNumber 永久存储在区块链上
*/
```

### ERC-20 代币合约简化版

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    string public name = "MyToken";
    string public symbol = "MTK";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    // 余额映射：地址 → 余额
    mapping(address => uint256) public balanceOf;

    // 授权映射：所有者 → (被授权者 → 额度)
    mapping(address => mapping(address => uint256)) public allowance;

    // 事件（用于前端监听）
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    // 构造函数：创建代币时调用一次
    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply * 10**decimals;
        balanceOf[msg.sender] = totalSupply;  // 全部给创建者
    }

    // 转账
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balanceOf[msg.sender] >= _value, "余额不足");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    // 授权：允许 _spender 从我账户转走最多 _value 的代币
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    // 代转：被授权者从 _from 转给 _to
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(balanceOf[_from] >= _value, "余额不足");
        require(allowance[_from][msg.sender] >= _value, "授权额度不足");
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }
}
```

### 合约交互流程

```
用户想调用合约的 transfer 函数:

┌─────────────────────────────────────────────────────────┐
│ 1. 构造交易                                              │
├─────────────────────────────────────────────────────────┤
│ to: 合约地址 (0x1234...)                                │
│ value: 0 (不转 ETH)                                     │
│ data: 0xa9059cbb...  (函数签名 + 参数编码)               │
│       ↓                                                 │
│   transfer(address,uint256) 的函数选择器                │
│   + 接收地址编码                                         │
│   + 转账金额编码                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 签名并广播                                            │
├─────────────────────────────────────────────────────────┤
│ 用户用私钥签名交易                                        │
│ 发送到区块链网络                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. EVM 执行                                              │
├─────────────────────────────────────────────────────────┤
│ 验证者收到交易                                           │
│ EVM (以太坊虚拟机) 执行合约代码                           │
│ - 检查发送者余额                                         │
│ - 扣减发送者余额                                         │
│ - 增加接收者余额                                         │
│ - 触发 Transfer 事件                                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 状态更新                                              │
├─────────────────────────────────────────────────────────┤
│ 新状态写入区块链                                          │
│ 事件日志记录                                             │
│ 交易收据生成                                             │
└─────────────────────────────────────────────────────────┘
```

### 合约安全：常见漏洞示例

```solidity
// ❌ 危险：重入攻击示例

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        // 危险：先转账，再更新余额
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;  // 太晚了！
    }
}

/*
攻击原理：
1. 攻击者存入 1 ETH
2. 攻击者调用 withdraw()
3. 合约发送 1 ETH 给攻击者
4. 攻击者的 receive() 函数再次调用 withdraw()
5. 因为 balances 还没更新，又能取 1 ETH
6. 循环直到合约被掏空
*/

// ✅ 安全：检查-生效-交互模式 (CEI Pattern)

contract SafeBank {
    mapping(address => uint256) public balances;

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        // 先更新余额（生效）
        balances[msg.sender] = 0;
        // 再转账（交互）
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
    }
}
```

---

## 新手最常踩的 3 个坑

### 1. 无限授权 (Infinite Approval)

**坑**：DApp 请求授权时默认是「无限额度」，很多人不看就点确认。

**风险**：
```
你授权 Uniswap 无限 USDC 额度
→ Uniswap 合约被黑 / 有后门
→ 黑客可以转走你所有 USDC
```

**正解**：
- 只授权需要的额度
- 定期检查和撤销授权（revoke.cash）
- 用不同钱包隔离风险

### 2. 以为合约经过「审计」就安全

**坑**：看到「已审计」就放心大胆投钱。

**现实**：
- 审计只能发现部分问题
- 审计后代码可能被改
- 很多被黑项目都有审计报告

**正解**：
- 审计是必要但不充分条件
- 关注审计公司声誉
- 小资金试水，观察一段时间
- 分散风险

### 3. 不理解合约不可修改

**坑**：以为出问题可以「修 bug」。

**现实**：
```
合约部署后代码不可改
→ 发现漏洞只能眼睁睁看着被利用
→ 或者紧急「迁移」（如果有这个功能）
```

**正解**：
- 部署前充分测试和审计
- 考虑是否需要可升级架构
- 了解紧急暂停机制
- 不要把所有资金放一个合约

---

## 流程图定位

```
┌──────┐    ┌──────────┐    ┌────────┐    ┌──────────┐    ┌────────────┐
│ 用户 │───▶│ 创建钱包 │───▶│ 签名   │───▶│ 广播交易 │───▶│ ★合约    │
│ 意图 │    │ (私钥)   │    │ 交易   │    │ 到网络   │    │  执行★    │
└──────┘    └──────────┘    └────────┘    └──────────┘    └────────────┘

智能合约的位置：
1. 部署阶段：合约代码被打包进交易，发送到区块链
2. 调用阶段：用户发送交易，包含调用哪个函数、什么参数
3. 执行阶段：EVM 执行合约代码，更新状态

合约就像区块链上的「服务」：
- 有自己的地址
- 有自己的存储空间
- 有自己的逻辑代码
- 被调用时执行
```

---

## 自测题

1. **为什么智能合约被称为「智能」，它真的智能吗？**

   <details>
   <summary>点击查看答案</summary>
   「智能合约」这个名字有误导性。它并不「智能」——没有 AI、没有学习能力、不能自主决策。它只是「自动执行的合约」：预设条件满足就执行预设动作，完全是确定性的。叫「自动化合约」或「程序化合约」更准确。
   </details>

2. **一个 DeFi 协议说「代码即法律」，这意味着什么？有什么风险？**

   <details>
   <summary>点击查看答案</summary>
   「代码即法律」意味着：
   - 合约的行为完全由代码决定
   - 没有人工干预或「客服」
   - 出了问题没有申诉渠道

   风险：
   - 代码 bug = 资金损失
   - 被黑客利用 = 无法追回
   - 与实际法律可能冲突
   - 操作失误无法撤销
   </details>

3. **为什么调用合约的「写」函数要付 Gas，但「读」函数免费？**

   <details>
   <summary>点击查看答案</summary>
   - 「写」函数（改变状态）需要全网共识：所有节点都要执行、验证、存储新状态，消耗大量资源，所以要付费
   - 「读」函数（只读取状态）可以在本地执行：只需要查询本地数据，不需要全网参与，不消耗网络资源，所以免费

   这也是为什么区块链上存储数据很贵——每写一次，全网都要永久保存一份。
   </details>
