# Rent（租金机制）

## 一句话大白话

**Rent 是 Solana 账户存储数据需要支付的"房租"。账户里必须存够一定数量的 SOL，否则会被"清理"掉。存够了就永久免租，数据永远保留。**

你可以把它想象成：区块链上的"仓储费"——你在区块链上存数据就像租仓库，要么每期交租金，要么一次性交够押金（免租金额度），押金交够了仓库永久属于你。

## 它解决什么问题

区块链面临的问题：
1. **存储成本**：验证节点需要存储所有账户数据
2. **状态膨胀**：如果免费存储，链上数据会无限增长
3. **垃圾数据**：废弃的账户占用宝贵存储空间

Solana 的解决方案：
- **按存储收费**：数据越多，需要的 SOL 越多
- **免租机制**：存够 2 年租金，账户永久有效
- **回收机制**：余额归零的账户会被清理，空间释放

## 什么时候用 / 什么时候别用

### 什么时候需要考虑 Rent
- 创建新账户时（需要计算最低余额）
- 关闭账户时（可以回收 SOL）
- 设计数据结构时（大小影响成本）

### 作为开发者需要知道
- 创建账户时确保余额超过免租金额度
- 关闭不用的账户可以回收 SOL
- 账户大小直接影响成本

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| Rent 每天扣钱 | 只要达到免租金额度，永远不扣钱 |
| Rent 是 gas 费 | Rent 是存储费，gas 是执行费，不同 |
| 账户被删后数据能恢复 | 一旦清理，数据永久丢失 |

### Rent vs Gas Fee

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Rent vs Gas Fee                                      │
├──────────────────────────────────────┬──────────────────────────────────────┤
│              Rent（租金）             │            Gas Fee（燃料费）          │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 目的：为账户存储付费                  │ 目的：为交易执行付费                  │
│ 支付时机：创建账户时                  │ 支付时机：每次交易时                  │
│ 计算依据：账户数据大小                │ 计算依据：计算复杂度（CU）            │
│ 可回收：关闭账户时返还                │ 不可回收：执行后消耗                  │
│ 锁定在：账户余额里                    │ 从：交易发起者扣除                    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

## 最小例子

### 1. 查看租金费率

```bash
# 查看存储 100 字节需要多少 SOL
solana rent 100

# 输出示例：
# Rent per byte-year: 0.00000348 SOL
# Rent per epoch: 0.000002439 SOL
# Rent-exempt minimum: 0.00089088 SOL
```

### 2. 计算免租金额度

```javascript
import { Connection, LAMPORTS_PER_SOL } from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');

// 获取存储特定大小数据需要的最低余额
const dataSize = 100; // 字节
const rentExemptBalance = await connection.getMinimumBalanceForRentExemption(dataSize);

console.log('免租金额度:', rentExemptBalance / LAMPORTS_PER_SOL, 'SOL');
// 约 0.00089 SOL
```

### 3. 常见账户的租金

```
账户类型                 数据大小      免租金额度（约）
────────────────────────────────────────────────────
钱包账户（无数据）       0 字节       0.00089 SOL
Token Account           165 字节      0.00203 SOL
Mint Account            82 字节       0.00144 SOL
NFT Metadata            ~679 字节     0.0056 SOL
Anchor 空账户           8 字节        0.00090 SOL
```

### 4. 创建账户时确保足够余额

```javascript
import {
  Connection,
  Keypair,
  SystemProgram,
  Transaction,
  sendAndConfirmTransaction,
} from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');
const payer = Keypair.generate();
const newAccount = Keypair.generate();

// 账户数据大小
const dataSize = 100;

// 获取免租金额度
const rentExemptBalance = await connection.getMinimumBalanceForRentExemption(dataSize);

// 创建账户
const transaction = new Transaction().add(
  SystemProgram.createAccount({
    fromPubkey: payer.publicKey,
    newAccountPubkey: newAccount.publicKey,
    lamports: rentExemptBalance,  // 必须 >= 免租金额度
    space: dataSize,
    programId: yourProgramId,
  })
);

await sendAndConfirmTransaction(connection, transaction, [payer, newAccount]);
```

### 5. 关闭账户回收 SOL

```rust
// Anchor 中关闭账户
#[derive(Accounts)]
pub struct CloseAccount<'info> {
    #[account(
        mut,
        close = receiver  // 关闭账户，余额转给 receiver
    )]
    pub data_account: Account<'info, MyData>,

    #[account(mut)]
    pub receiver: SystemAccount<'info>,
}

pub fn close(ctx: Context<CloseAccount>) -> Result<()> {
    // Anchor 自动处理：
    // 1. 将账户余额转给 receiver
    // 2. 将账户数据清零
    // 3. 将账户 owner 设为 System Program
    // 4. 将账户标记为可回收
    Ok(())
}
```

```javascript
// JavaScript 调用
await program.methods
  .close()
  .accounts({
    dataAccount: dataAccountPubkey,
    receiver: wallet.publicKey,
  })
  .rpc();

// 回收的 SOL 会转到 receiver 账户
```

## Rent 工作机制详解

### 免租状态 (Rent-Exempt)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Rent 状态判断                                        │
└─────────────────────────────────────────────────────────────────────────────┘

账户余额 >= 免租金额度
    │
    ├── 是 ──→ Rent-Exempt（免租）
    │         ✓ 账户永久有效
    │         ✓ 不会被扣租金
    │         ✓ 不会被清理
    │
    └── 否 ──→ 需要交租
              ✗ 每个 epoch 扣租金
              ✗ 余额归零时被清理
              ⚠️ 实际上现在 Solana 强制要求免租

重要：
从 2022 年开始，Solana 要求所有新账户必须达到免租金额度。
无法创建"交租"状态的账户了。
```

### 免租金额度计算公式

```
免租金额度 = (账户数据大小 + 128) × 每字节2年租金

其中：
- 128 字节是账户元数据开销
- 每字节2年租金 ≈ 0.00000348 SOL

示例：
100 字节数据
= (100 + 128) × 0.00000348
= 228 × 0.00000348
= 0.00079344 SOL
≈ 0.00089 SOL（实际会略高）
```

## 新手最常踩的 3 个坑

### 坑 1：创建账户时余额不足

**问题**：创建账户失败，报错 "Insufficient lamports"

**原因**：传入的 lamports 少于免租金额度

**解决**：
```javascript
// 错误：硬编码可能不够
const lamports = 1000000; // 0.001 SOL，可能不够！

// 正确：动态计算
const lamports = await connection.getMinimumBalanceForRentExemption(dataSize);
```

### 坑 2：忘记考虑 Anchor discriminator

**问题**：计算空间时只算了数据字段，结果不够

**原因**：Anchor 账户有 8 字节的 discriminator

**解决**：
```rust
// Anchor 账户空间计算
#[account(init, payer = user, space = 8 + 32 + 8)]
//                                    ↑
//                            discriminator（必须加！）

// 8 + 32 (Pubkey) + 8 (u64) = 48 字节
```

### 坑 3：没有关闭废弃账户

**问题**：创建了很多临时账户，SOL 都锁在里面

**解决**：
```rust
// 提供关闭账户的指令
#[derive(Accounts)]
pub struct CloseMyAccount<'info> {
    #[account(mut, close = authority)]  // 关键：close 约束
    pub my_account: Account<'info, MyData>,

    #[account(mut)]
    pub authority: Signer<'info>,
}
```

## 流程图定位

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       Rent 在账户生命周期中的位置                             │
└──────────────────────────────────────────────────────────────────────────────┘

创建账户                    使用账户                    关闭账户
    │                          │                          │
    ▼                          ▼                          ▼
┌──────────┐            ┌──────────┐            ┌──────────┐
│  计算    │            │  正常    │            │  回收    │
│ 免租金额 │──存入──→   │  使用    │──关闭──→   │  SOL    │
│          │   SOL      │          │            │          │
└──────────┘            └──────────┘            └──────────┘
    │                          │                          │
    ▼                          ▼                          ▼
必须存够                  数据安全存储                 释放空间
免租金额度                不会被清理                   归还 SOL
```

## 租金优化技巧

### 1. 最小化账户大小

```rust
// 不好：使用过大的类型
#[account]
pub struct Wasteful {
    pub small_number: u64,     // 只需要存 0-255，却用了 8 字节
    pub long_string: String,   // 预留了过多空间
}

// 好：使用合适的类型
#[account]
pub struct Efficient {
    pub small_number: u8,      // 1 字节够用
    pub short_string: [u8; 32], // 固定大小，节省空间
}
```

### 2. 使用 PDA 而非随机密钥对

```rust
// PDA 不需要额外存储密钥对，且更安全
#[account(
    seeds = [b"user-stats", user.key().as_ref()],
    bump
)]
pub user_stats: Account<'info, UserStats>,
```

### 3. 及时关闭不用的账户

```rust
// 临时账户用完就关
#[account(mut, close = user)]
pub temp_account: Account<'info, TempData>,
```

## 自测题

1. **基础题**：一个账户存储 200 字节数据，免租金额度大约是多少？
   <details>
   <summary>答案</summary>
   约 0.00114 SOL。
   计算：(200 + 128) × 0.00000348 ≈ 0.00114
   实际可通过 `solana rent 200` 查看准确值。
   </details>

2. **理解题**：为什么 Solana 现在强制要求所有账户都是 rent-exempt？
   <details>
   <summary>答案</summary>
   1. 简化开发体验（不用担心账户被意外清理）
   2. 避免"租金攻击"（恶意耗尽他人账户余额）
   3. 保证数据持久性（用户资产不会因忘记续费而丢失）
   4. 减少网络维护成本（不用频繁清理低余额账户）
   </details>

3. **实践题**：如何估算一个 DApp 的存储成本？
   <details>
   <summary>答案</summary>
   1. 列出所有账户类型和大小
   2. 估算每类账户的数量
   3. 计算总存储空间
   4. 乘以免租费率

   示例：
   - 10000 用户，每用户 1 个 Profile 账户 (200 字节)
   - 总空间 = 10000 × 200 = 2,000,000 字节
   - 免租总额 ≈ 10000 × 0.00114 = 11.4 SOL

   注意：这些 SOL 是锁定的，关闭账户可以回收。
   </details>
