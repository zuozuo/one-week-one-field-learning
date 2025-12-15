# SPL Token（Solana 代币标准）

## 一句话大白话

**SPL Token 是 Solana 上创建和管理代币的官方标准，就像以太坊的 ERC-20。用它你可以创建自己的加密货币、稳定币、积分、游戏币等任何同质化代币。**

你可以把它想象成：一个"代币工厂"——你告诉工厂（Token Program）你想造什么币，它帮你造好，还提供转账、销毁、冻结等标准功能。

## 它解决什么问题

在区块链上发行代币需要：
1. **标准化**：让所有钱包、交易所都能识别你的代币
2. **安全性**：转账逻辑经过审计，不用自己写
3. **互操作性**：不同 DApp 都能使用你的代币

SPL Token Program 就是 Solana 官方提供的"代币解决方案"。

## 什么时候用 / 什么时候别用

### 什么时候用 SPL Token
- 发行自己的代币（项目币、治理币）
- 创建稳定币
- 游戏内积分系统
- 任何需要可转让的同质化资产

### 什么时候不用
- NFT（用 Metaplex 或 Token-2022）
- 只是转账 SOL（用 System Program）

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| SPL Token = 代币本身 | SPL Token 是**标准/程序**，不是具体的币 |
| 每种代币有独立的合约 | 所有 SPL Token 共用一个 Token Program |
| 代币数据存在 Program 里 | 数据存在独立的 Account（Mint 和 Token Account） |

### SPL Token 的核心概念

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SPL Token 架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Token Program  │ ← 只有一个，处理所有 SPL Token
│  (代码逻辑)      │
└────────┬────────┘
         │ 管理
         ▼
┌─────────────────┐         ┌─────────────────┐
│   Mint Account  │ ← 定义  │   Mint Account  │ ← 另一种代币
│   (USDC 定义)   │  代币   │   (RAY 定义)    │
│ - supply: 10B   │         │ - supply: 500M  │
│ - decimals: 6   │         │ - decimals: 6   │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ 持有关系                   │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Token Account  │         │  Token Account  │
│   (用户 A 的    │         │   (用户 A 的    │
│    USDC 余额)   │         │    RAY 余额)    │
│ - balance: 100  │         │ - balance: 50   │
│ - owner: A      │         │ - owner: A      │
└─────────────────┘         └─────────────────┘
```

## 最小例子

### 1. 创建代币（Mint）

```bash
# 使用 spl-token CLI
# 首先确保有足够的 SOL
solana airdrop 2 --url devnet

# 创建一个新的代币
spl-token create-token --url devnet

# 输出示例:
# Creating token 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
# Address: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
# Decimals: 9
```

### 2. 创建 Token Account 并铸造

```bash
# 创建用于接收代币的 Token Account
spl-token create-account 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU --url devnet

# 铸造 1000 个代币
spl-token mint 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 1000 --url devnet

# 查看余额
spl-token balance 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU --url devnet
# 输出: 1000
```

### 3. 转账代币

```bash
# 转 100 个代币给另一个地址
spl-token transfer 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU 100 <接收方地址> --url devnet
```

### 4. 使用 JavaScript

```javascript
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
} from '@solana/web3.js';
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
  transfer,
  TOKEN_PROGRAM_ID,
} from '@solana/spl-token';

const connection = new Connection('https://api.devnet.solana.com');
const payer = Keypair.generate(); // 或从钱包导入

// 1. 创建代币 (Mint)
const mint = await createMint(
  connection,
  payer,           // 付费者
  payer.publicKey, // Mint Authority（谁能铸币）
  null,            // Freeze Authority（谁能冻结，null = 无）
  9                // 小数位数
);
console.log('代币地址:', mint.toBase58());

// 2. 创建 Token Account
const tokenAccount = await getOrCreateAssociatedTokenAccount(
  connection,
  payer,
  mint,
  payer.publicKey  // Token Account 的所有者
);
console.log('Token Account:', tokenAccount.address.toBase58());

// 3. 铸造代币
await mintTo(
  connection,
  payer,
  mint,
  tokenAccount.address,
  payer,           // Mint Authority
  1000_000_000_000 // 1000 个代币 (9位小数)
);

// 4. 转账
const toTokenAccount = await getOrCreateAssociatedTokenAccount(
  connection,
  payer,
  mint,
  receiverPublicKey
);

await transfer(
  connection,
  payer,
  tokenAccount.address,     // 发送方 Token Account
  toTokenAccount.address,   // 接收方 Token Account
  payer,                    // 发送方签名
  100_000_000_000           // 100 个代币
);
```

### 5. Token Account 结构详解

```javascript
// Token Account 的数据结构
{
  // 这个 Token Account 存储的是哪种代币
  mint: PublicKey,        // 指向 Mint Account

  // 谁拥有这个 Token Account（谁能转出代币）
  owner: PublicKey,

  // 代币余额（最小单位）
  amount: u64,

  // 可选：授权另一个地址代为操作
  delegate: Option<PublicKey>,
  delegated_amount: u64,

  // 是否被冻结（如果 Mint 有 Freeze Authority）
  is_frozen: bool,

  // 是否是原生 SOL 包装
  is_native: bool,
}
```

## 新手最常踩的 3 个坑

### 坑 1：忘记创建接收方的 Token Account

**问题**：给别人转代币失败，报错 "Account not found"

**原因**：Solana 上接收代币需要预先存在 Token Account

**解决**：使用 `getOrCreateAssociatedTokenAccount`

```javascript
// 会自动创建 ATA（如果不存在）
const receiverATA = await getOrCreateAssociatedTokenAccount(
  connection,
  payer,      // 谁付创建费用（可以是发送方）
  mint,
  receiver
);
```

### 坑 2：混淆 Decimals

**问题**：想转 1 个代币，结果转了 0.000000001 个

**原因**：代币的 decimals 决定了最小单位

```javascript
// 假设 decimals = 9
// 1 个代币 = 1_000_000_000 最小单位

// 错误
await mintTo(..., 1);  // 只铸造了 0.000000001 个

// 正确
const DECIMALS = 9;
const amount = 1 * Math.pow(10, DECIMALS);  // 1_000_000_000
await mintTo(..., amount);
```

### 坑 3：不理解 Authority

**问题**：创建代币后无法铸造新币或想放弃铸造权

**概念**：
- **Mint Authority**：有权铸造新代币的地址
- **Freeze Authority**：有权冻结 Token Account 的地址

```javascript
// 创建时指定 Authority
const mint = await createMint(
  connection,
  payer,
  mintAuthority,    // 谁能铸币
  freezeAuthority,  // 谁能冻结（传 null = 永久无冻结功能）
  decimals
);

// 放弃铸造权（让代币总量固定）
import { setAuthority, AuthorityType } from '@solana/spl-token';

await setAuthority(
  connection,
  payer,
  mint,
  currentAuthority,
  AuthorityType.MintTokens,
  null  // 设为 null = 永久放弃
);
```

## 流程图定位

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        SPL Token 在 Solana 架构中的位置                       │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │           应用层 (DApps)            │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
                    │  │ DeFi│ │ DEX │ │钱包 │ │NFT  │   │
                    │  └─────┘ └─────┘ └─────┘ └─────┘   │
                    └───────────────┬─────────────────────┘
                                    │ 调用
                    ┌───────────────▼─────────────────────┐
                    │           Program 层                │
                    │  ┌──────────────────────────────┐  │
                    │  │      【SPL Token Program】   │  │
                    │  │   - 创建代币 (Mint)          │  │
                    │  │   - 铸造/销毁               │  │
                    │  │   - 转账                    │  │
                    │  │   - 冻结/解冻               │  │
                    │  └──────────────────────────────┘  │
                    └───────────────┬─────────────────────┘
                                    │ 操作
                    ┌───────────────▼─────────────────────┐
                    │           Account 层                │
                    │  ┌─────────────┐ ┌─────────────┐   │
                    │  │Mint Account │ │Token Account│   │
                    │  │  (代币定义)  │ │  (用户余额) │   │
                    │  └─────────────┘ └─────────────┘   │
                    └─────────────────────────────────────┘
```

## Associated Token Account (ATA)

### 什么是 ATA

**问题**：每个用户每种代币都要手动创建 Token Account，地址还不确定，太麻烦！

**解决**：ATA 是一种"可预测"的 Token Account，通过钱包地址 + Mint 地址计算出来。

```
ATA 地址 = PDA(钱包地址, Token Program, Mint 地址)

示例：
用户钱包：7xKXt...
USDC Mint：EPjFW...
─────────────────
用户的 USDC ATA：可以提前计算出来！
```

### 为什么用 ATA

```javascript
// 不用 ATA（麻烦）
// 1. 创建一个随机地址的 Token Account
// 2. 告诉别人这个地址
// 3. 别人才能给你转账

// 用 ATA（简单）
import { getAssociatedTokenAddressSync } from '@solana/spl-token';

// 任何人都能计算出你的 USDC 账户地址
const myUSDCAddress = getAssociatedTokenAddressSync(
  USDC_MINT,
  myWalletAddress
);
// 别人直接转到这个地址就行
```

## 自测题

1. **基础题**：一个用户想持有 3 种不同的 SPL Token，需要几个 Account？
   <details>
   <summary>答案</summary>
   4 个：1 个钱包账户（存 SOL）+ 3 个 Token Account（每种代币一个）。注意 Mint Account 不算，那是代币本身的定义，不是用户的。
   </details>

2. **理解题**：为什么 Solana 所有 SPL Token 共用一个 Token Program，而以太坊每种 ERC-20 都是独立合约？
   <details>
   <summary>答案</summary>
   设计理念不同：
   - Solana：代码和数据分离，一份代码（Token Program）+ 无数个数据账户（Mint/Token Account）
   - 以太坊：代码和数据一体，每种代币都部署一份合约代码

   Solana 的方式节省空间，统一标准，安全性更高（代码经过充分审计）。
   </details>

3. **实践题**：如何创建一个总量固定、无法增发的代币？
   <details>
   <summary>答案</summary>
   1. 创建 Mint 时正常设置 Mint Authority
   2. 铸造你需要的总量
   3. 调用 setAuthority 将 Mint Authority 设为 null

   这样就没有人能再铸造新币了。
   </details>
