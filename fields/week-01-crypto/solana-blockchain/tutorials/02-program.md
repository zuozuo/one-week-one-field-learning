# Program（程序/智能合约）

## 一句话大白话

**Program 是 Solana 上的智能合约，它只存代码逻辑，不存数据——数据全放在 Account 里。Program 就像一个"纯函数"，给它输入，它处理，然后修改 Account。**

你可以把它想象成：自动售货机 —— 机器（Program）不存饮料（数据），饮料在仓库（Account）里，你投币（交易），机器执行程序，从仓库拿出饮料给你。

## 它解决什么问题

智能合约需要解决：
1. **定义规则**：什么操作是允许的（比如只有持有者才能转账）
2. **自动执行**：不需要人工干预，代码即法律
3. **可组合性**：不同合约可以互相调用

Solana 的 Program 通过"代码和数据分离"的设计，实现了：
- **更高效**：Program 代码只存一份，可以操作无数个 Account
- **更灵活**：升级 Program 不影响已有数据
- **可并行**：不同 Account 可以同时被处理

## 什么时候用 / 什么时候别用

### 什么时候需要写 Program
- 创建新的链上逻辑（DeFi、NFT 市场、游戏等）
- 现有 Program 不能满足需求

### 什么时候不需要
- 只是转账 SOL（用 System Program）
- 只是创建/转账代币（用 SPL Token Program）
- 只是铸造 NFT（用 Metaplex）

### Solana 内置的常用 Program

| Program | 地址 | 用途 |
|---------|------|------|
| System Program | `11111111111111111111111111111111` | 创建账户、转账 SOL |
| Token Program | `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` | 代币操作 |
| Associated Token | `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL` | 管理 ATA |
| Memo Program | `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr` | 添加备注 |

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| Program 存储合约状态 | Program 只存代码，状态在 Account 里 |
| Program = 以太坊的合约 | 类似但不同：以太坊合约代码+数据一体，Solana 分离 |
| 每次调用都要部署 | Program 部署一次，可调用无限次 |

### 和以太坊合约的核心区别

```
以太坊 (EVM)：
┌─────────────────────────┐
│   智能合约地址 0x123    │
│  ├── 代码 (bytecode)    │
│  ├── 状态变量 balances  │  ← 代码和数据在一起
│  └── 状态变量 owner     │
└─────────────────────────┘
调用：contract.transfer(to, amount)


Solana：
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Token Program │     │ Token Account  │     │ Token Account  │
│    (代码)      │     │    (数据)      │     │    (数据)      │
│  地址: Prog1   │     │  余额: 100     │     │  余额: 50      │
│                │     │  Owner: Prog1  │     │  Owner: Prog1  │
└────────────────┘     └────────────────┘     └────────────────┘
        │                      │                      │
        └──────── Program 操作这些 Account ───────────┘

调用：传入 [Program地址, Account1, Account2, 指令数据]
```

## 最小例子

### 调用系统 Program 转账 SOL

```javascript
import {
  Connection,
  PublicKey,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
  Keypair,
} from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');

// 创建转账指令
const transferInstruction = SystemProgram.transfer({
  fromPubkey: sender.publicKey,   // 发送方账户
  toPubkey: receiver.publicKey,   // 接收方账户
  lamports: 1000000000,           // 1 SOL
});

// 构造交易
const transaction = new Transaction().add(transferInstruction);

// 发送并确认
const signature = await sendAndConfirmTransaction(
  connection,
  transaction,
  [sender]  // 签名者
);

console.log('交易签名:', signature);
```

### 一个最简单的 Anchor Program

```rust
// programs/hello/src/lib.rs
use anchor_lang::prelude::*;

declare_id!("你的Program地址");

#[program]
pub mod hello {
    use super::*;

    // 初始化：创建一个存储数据的 Account
    pub fn initialize(ctx: Context<Initialize>, data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = data;
        Ok(())
    }

    // 更新数据
    pub fn update(ctx: Context<Update>, data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = data;
        Ok(())
    }
}

// 定义 Account 结构
#[account]
pub struct MyAccount {
    pub data: u64,
}

// 定义 Initialize 指令需要的账户
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = user, space = 8 + 8)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

// 定义 Update 指令需要的账户
#[derive(Accounts)]
pub struct Update<'info> {
    #[account(mut)]
    pub my_account: Account<'info, MyAccount>,
}
```

### Program 的执行流程

```
1. 用户构造交易
   ┌────────────────────────────────────────┐
   │ Transaction                           │
   │ ├── 指令 1                            │
   │ │   ├── program_id: Token Program     │
   │ │   ├── accounts: [A, B, C]           │
   │ │   └── data: [transfer, 100]         │
   │ └── 签名: [用户私钥签名]              │
   └────────────────────────────────────────┘
                    │
                    ▼
2. 验证节点执行
   ┌────────────────────────────────────────┐
   │ Runtime (Sealevel)                    │
   │ ├── 加载 Program 代码                 │
   │ ├── 加载涉及的 Account                │
   │ ├── 验证签名                          │
   │ ├── 执行 Program 逻辑                 │
   │ └── 更新 Account 数据                 │
   └────────────────────────────────────────┘
                    │
                    ▼
3. 结果
   - 成功：Account 状态更新，扣除 gas 费
   - 失败：回滚所有更改，仍扣 gas 费
```

## 新手最常踩的 3 个坑

### 坑 1：忘记传入所有需要的 Account

**问题**：调用 Program 时报错 "Account not found"

**原因**：Solana 要求调用时**显式传入所有涉及的 Account**，包括要读的和要写的。

**错误示例**：
```javascript
// 只传了发送方，忘了接收方
const instruction = new TransactionInstruction({
  keys: [
    { pubkey: sender, isSigner: true, isWritable: true }
    // 漏了 receiver!
  ],
  programId: TOKEN_PROGRAM_ID,
  data: transferData
});
```

**正确示例**：
```javascript
const instruction = new TransactionInstruction({
  keys: [
    { pubkey: sender, isSigner: true, isWritable: true },
    { pubkey: receiver, isSigner: false, isWritable: true },  // 加上接收方
    { pubkey: mint, isSigner: false, isWritable: false },     // 可能还需要 mint
  ],
  programId: TOKEN_PROGRAM_ID,
  data: transferData
});
```

### 坑 2：混淆 Program ID 和 Account 地址

**问题**：把 Account 地址当 Program ID 用，或者反过来。

**区分方法**：
- **Program ID**：可执行代码的地址，`executable = true`
- **Account 地址**：存储数据的地址，`executable = false`

```javascript
// 查看是不是 Program
const accountInfo = await connection.getAccountInfo(address);
console.log('是 Program 吗?', accountInfo.executable);
```

### 坑 3：不理解 CPI（跨程序调用）

**问题**：想让自己的 Program 调用 Token Program 转账，不知道怎么做。

**解释**：Program 可以调用其他 Program，叫 CPI（Cross-Program Invocation）。

```rust
// 在你的 Program 里调用 Token Program
use anchor_spl::token::{self, Transfer, Token};

pub fn transfer_tokens(ctx: Context<TransferTokens>, amount: u64) -> Result<()> {
    let cpi_accounts = Transfer {
        from: ctx.accounts.from.to_account_info(),
        to: ctx.accounts.to.to_account_info(),
        authority: ctx.accounts.authority.to_account_info(),
    };
    let cpi_program = ctx.accounts.token_program.to_account_info();
    let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

    token::transfer(cpi_ctx, amount)?;
    Ok(())
}
```

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │    │  钱包    │    │  RPC     │    │ 验证节点  │
│  发起    │───▶│  签名    │───▶│  广播    │───▶│  执行    │
│  交易    │    │  交易    │    │  交易    │    │  交易    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                                               │
     ▼                                               ▼
  指定调用                                      【Program】
  哪个 Program                                   执行代码逻辑
  传入指令数据                                   修改 Account
```

## 自测题

1. **基础题**：为什么 Solana 的 Program 被称为"无状态"的？
   <details>
   <summary>答案</summary>
   因为 Program 本身不存储数据，所有状态都存在独立的 Account 里。Program 只定义逻辑，执行时读写 Account。
   </details>

2. **理解题**：如果一个 Token Program 代码有 bug，需要修复，已有用户的代币数据会丢失吗？
   <details>
   <summary>答案</summary>
   不会。因为代币数据存在 Account 里，不在 Program 里。升级 Program 只是替换代码，Account 数据不受影响（这也是代码和数据分离的好处）。
   </details>

3. **实践题**：调用一个 Program 时，传入的 Account 列表顺序重要吗？
   <details>
   <summary>答案</summary>
   非常重要！Program 按照固定顺序解析 Account 列表。顺序错误会导致 Program 读错数据或执行失败。
   </details>
