# Account（账户）

## 一句话大白话

**Account 就是 Solana 上存储数据的"容器"，每个容器都有一个地址（公钥），里面可以放 SOL、代币、NFT 或任何自定义数据。**

你可以把它想象成：银行的保险箱 + 每个箱子都有唯一编号 + 箱子里能存任何东西。

## 它解决什么问题

在区块链上，我们需要一种方式来：
1. **存储数据**：余额、代币、NFT、合约状态
2. **证明所有权**：谁有权限修改这些数据
3. **保证安全**：防止未授权的修改

Account 模型是 Solana 给出的答案，它和以太坊的方式完全不同。

### 使用场景

| 场景 | Account 的作用 |
|------|---------------|
| 存 SOL | 你的钱包地址就是一个 Account，里面存着 SOL 余额 |
| 存代币 | 每种代币都需要一个专门的 Token Account |
| NFT | 每个 NFT 也是一个 Account |
| 合约数据 | 智能合约的状态存在独立的 Account 里 |

## 什么时候用 / 什么时候别用

### 什么时候需要创建 Account
- 第一次接收某种代币
- 部署新的智能合约
- 存储新的链上数据

### 什么时候不需要
- 只是发送 SOL（用现有钱包账户）
- 调用已存在的合约（合约账户已存在）

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| Account = 钱包 | Account 是更广的概念，钱包只是 Account 的一种 |
| Account = 智能合约 | 智能合约（Program）也是一种 Account，但 Account 不只是合约 |
| 一个地址只能存一种东西 | 一个地址确实只是一个 Account，但你需要多个 Account 存不同东西 |

### 和以太坊的核心区别

```
以太坊：
┌─────────────────────────┐
│     一个地址            │
│  ├── ETH 余额           │
│  ├── ERC20 Token A 余额 │
│  ├── ERC20 Token B 余额 │  ← 所有数据存在一个"账户"里
│  └── NFT 持有记录       │
└─────────────────────────┘

Solana：
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 钱包 Account │  │Token Account │  │Token Account │
│   (存 SOL)   │  │  (存 USDC)   │  │  (存 RAY)    │
│  地址: A1    │  │   地址: A2   │  │   地址: A3   │
└──────────────┘  └──────────────┘  └──────────────┘
       ↑                 ↑                 ↑
       └─────── 都属于同一个用户 ───────────┘
```

## 最小例子

### 查看一个 Account

```bash
# 安装 Solana CLI 后，查看任意账户
solana account <地址>

# 例如查看一个真实账户
solana account 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU --url mainnet-beta
```

输出示例：
```
Public Key: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
Balance: 1.5 SOL
Owner: 11111111111111111111111111111111
Executable: false
Rent Epoch: 123
Data Length: 0
```

### Account 的核心字段

```javascript
{
  // 公钥：Account 的唯一标识（地址）
  pubkey: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",

  // lamports：余额（1 SOL = 1,000,000,000 lamports）
  lamports: 1500000000,

  // owner：谁有权修改这个 Account（是个 Program 的地址）
  owner: "11111111111111111111111111111111",  // System Program

  // executable：是否是可执行程序
  executable: false,

  // data：存储的实际数据（字节数组）
  data: []
}
```

### 用 JavaScript 读取 Account

```javascript
import { Connection, PublicKey } from '@solana/web3.js';

const connection = new Connection('https://api.mainnet-beta.solana.com');
const publicKey = new PublicKey('你的地址');

// 获取账户信息
const accountInfo = await connection.getAccountInfo(publicKey);

console.log('余额:', accountInfo.lamports / 1e9, 'SOL');
console.log('所有者:', accountInfo.owner.toString());
console.log('数据长度:', accountInfo.data.length, '字节');
```

## 新手最常踩的 3 个坑

### 坑 1：忘记创建 Token Account

**问题**：别人给你转 USDC，但你从来没收过 USDC，交易会失败！

**原因**：Solana 上接收代币需要先有对应的 Token Account。

**解决**：
```javascript
// 使用 Associated Token Account（ATA）自动创建
import { getOrCreateAssociatedTokenAccount } from '@solana/spl-token';

const tokenAccount = await getOrCreateAssociatedTokenAccount(
  connection,
  payer,        // 谁付创建费用
  mintAddress,  // 代币的 Mint 地址
  ownerAddress  // 谁拥有这个 Token Account
);
```

### 坑 2：混淆 Owner 和 Signer

**问题**：以为 Owner 是"拥有者"的意思。

**实际**：
- **Owner**：有权修改 Account 数据的 **Program**（不是人！）
- **Signer**：用私钥签名交易的人

```
普通钱包账户：
Owner = System Program（系统程序才能改余额）
Signer = 你（你签名才能花钱）

Token 账户：
Owner = Token Program（Token 程序才能改代币余额）
Authority = 你（你授权 Token Program 操作）
```

### 坑 3：不理解 Rent（租金）

**问题**：创建 Account 后，余额莫名其妙减少。

**原因**：Solana 账户需要支付"租金"来存储数据。

**解决**：确保账户余额超过"免租金额度"（rent-exempt）：
```bash
# 查看存储 100 字节数据需要多少 SOL
solana rent 100

# 输出：Rent per byte-year: 0.00000348 SOL
# Rent per epoch: 0.000002439 SOL
# Rent-exempt minimum: 0.00089088 SOL
```

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │    │  钱包    │    │  RPC     │
│  发起    │───▶│  签名    │───▶│  广播    │
│  交易    │    │  交易    │    │  交易    │
└──────────┘    └──────────┘    └──────────┘
     │               │
     ▼               ▼
  【Account】    【Account】
  构造指令时      签名需要
  必须指定       Account 的
  涉及的账户      私钥
```

Account 在流程中的角色：
1. **构造交易时**：必须明确指定所有涉及的 Account
2. **签名时**：需要相关 Account 的私钥
3. **执行时**：Program 读写指定的 Account
4. **确认后**：Account 的状态被永久更新

## 自测题

1. **基础题**：一个用户想同时持有 SOL、USDC、RAY 三种资产，至少需要几个 Account？
   <details>
   <summary>答案</summary>
   3个。一个钱包 Account 存 SOL，两个 Token Account 分别存 USDC 和 RAY。
   </details>

2. **理解题**：为什么 Solana 的设计是让 Program 当 Owner，而不是让用户当 Owner？
   <details>
   <summary>答案</summary>
   因为 Program 定义了数据的修改规则。比如 Token Program 规定"只有有效签名才能转账"，这比让用户直接改数据更安全、更规范。
   </details>

3. **实践题**：如何判断一个 Account 是普通钱包还是智能合约？
   <details>
   <summary>答案</summary>
   看 `executable` 字段：true 是智能合约（Program），false 是普通数据账户。
   </details>
