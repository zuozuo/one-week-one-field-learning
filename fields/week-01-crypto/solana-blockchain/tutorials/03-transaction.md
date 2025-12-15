# Transaction（交易）

## 一句话大白话

**Transaction 是一个打包好的"操作请求"，里面包含一条或多条指令，要么全部成功，要么全部失败——这就是原子性。**

你可以把它想象成：一个快递包裹，里面可以装多个物品（指令），快递员（验证节点）要么全部签收，要么全部拒收，不存在签一半的情况。

## 它解决什么问题

区块链上的操作需要：
1. **原子性**：复杂操作要么全成功，要么全失败（防止中间状态）
2. **可验证**：所有人都能验证操作是否合法
3. **防重放**：同一笔交易不能被重复执行
4. **授权**：只有授权的人才能发起操作

Transaction 通过签名机制和原子执行保证了这些需求。

## 什么时候用 / 什么时候别用

### 什么时候需要构造 Transaction
- 任何链上操作都需要：转账、调用合约、创建账户...
- 需要组合多个操作为原子操作

### 什么时候不需要
- 只读操作（查询余额、获取账户信息）不需要交易

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| Transaction = 转账 | 转账只是 Transaction 的一种用途 |
| 一个 Transaction 只能做一件事 | 一个 Transaction 可以包含多条指令 |
| Transaction 失败不扣费 | 即使失败也要扣 gas 费 |

## 最小例子

### Transaction 的结构

```
┌─────────────────────────────────────────────────────────────┐
│                      Transaction                            │
├─────────────────────────────────────────────────────────────┤
│  Message (消息体)                                           │
│  ├── Header (头部)                                          │
│  │   ├── num_required_signatures: 1                        │
│  │   ├── num_readonly_signed_accounts: 0                   │
│  │   └── num_readonly_unsigned_accounts: 1                 │
│  │                                                          │
│  ├── Account Keys (账户列表)                                │
│  │   ├── [0] 发送方 (signer, writable)                     │
│  │   ├── [1] 接收方 (writable)                             │
│  │   └── [2] System Program (readonly)                     │
│  │                                                          │
│  ├── Recent Blockhash (最近区块哈希 - 防重放)               │
│  │   └── "5GU4...xyz"                                       │
│  │                                                          │
│  └── Instructions (指令列表)                                │
│      └── Instruction 0                                      │
│          ├── program_id_index: 2 (指向 System Program)      │
│          ├── accounts: [0, 1] (涉及的账户索引)              │
│          └── data: [2, 0, 0, 0, ...] (指令数据)            │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Signatures (签名列表)                                       │
│  └── [0] 发送方的签名 (64 字节)                             │
└─────────────────────────────────────────────────────────────┘
```

### 用 JavaScript 构造并发送 Transaction

```javascript
import {
  Connection,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
  PublicKey,
  Keypair,
  LAMPORTS_PER_SOL,
} from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');

// 1. 创建指令
const transferInstruction = SystemProgram.transfer({
  fromPubkey: sender.publicKey,
  toPubkey: new PublicKey('接收方地址'),
  lamports: 0.1 * LAMPORTS_PER_SOL, // 0.1 SOL
});

// 2. 创建交易并添加指令
const transaction = new Transaction().add(transferInstruction);

// 3. 获取最新区块哈希（用于防重放）
const { blockhash } = await connection.getLatestBlockhash();
transaction.recentBlockhash = blockhash;
transaction.feePayer = sender.publicKey;

// 4. 签名
transaction.sign(sender);

// 5. 发送并确认
const signature = await sendAndConfirmTransaction(connection, transaction, [sender]);

console.log('交易成功！签名:', signature);
console.log('查看交易: https://explorer.solana.com/tx/' + signature + '?cluster=devnet');
```

### 多指令 Transaction（原子操作）

```javascript
// 场景：创建代币账户 + 转账，必须同时成功
const transaction = new Transaction();

// 指令 1：创建 Token Account
transaction.add(
  createAssociatedTokenAccountInstruction(
    payer.publicKey,
    associatedTokenAddress,
    owner.publicKey,
    mintAddress
  )
);

// 指令 2：转账代币
transaction.add(
  createTransferInstruction(
    sourceTokenAccount,
    associatedTokenAddress,
    owner.publicKey,
    amount
  )
);

// 两个指令会原子执行
// 如果创建失败，转账也不会执行
// 如果转账失败，已创建的账户也会回滚
const signature = await sendAndConfirmTransaction(connection, transaction, [payer, owner]);
```

### 查看交易详情

```bash
# 使用 CLI 查看交易
solana confirm -v <交易签名>

# 输出示例
Transaction confirmed
Block Time: 2024-01-15T10:30:00Z
Slot: 123456789
Status: Success
Fee: 0.000005 SOL
Accounts:
  [0] 7xKXt... (signer, writable, fee payer)
  [1] 8yLYu... (writable)
  [2] 11111... (readonly, System Program)
Instructions:
  [0] System Program: Transfer
      From: 7xKXt...
      To: 8yLYu...
      Amount: 100000000 lamports (0.1 SOL)
```

## 新手最常踩的 3 个坑

### 坑 1：Blockhash 过期

**问题**：交易报错 "Blockhash not found" 或 "Transaction expired"

**原因**：Solana 的 blockhash 只在约 60-90 秒内有效（150 个区块）。如果构造交易后等太久才发送，blockhash 会过期。

**解决**：
```javascript
// 方法 1：发送前重新获取 blockhash
const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();
transaction.recentBlockhash = blockhash;

// 方法 2：使用 durable nonce（持久化 nonce）
// 适用于需要离线签名的场景
```

### 坑 2：签名者顺序错误

**问题**：交易报错 "Signature verification failed"

**原因**：签名者数组的顺序必须和 Transaction 中账户的顺序一致。

**错误示例**：
```javascript
// Transaction 里 payer 是第一个签名者，owner 是第二个
// 但签名时顺序反了
await sendAndConfirmTransaction(connection, transaction, [owner, payer]); // 错！
```

**正确示例**：
```javascript
// 顺序要和 Transaction 中的声明一致
await sendAndConfirmTransaction(connection, transaction, [payer, owner]); // 对！
```

### 坑 3：交易太大

**问题**：交易报错 "Transaction too large"

**原因**：Solana 单个交易最大 1232 字节。包含太多指令或账户会超限。

**解决**：
```javascript
// 检查交易大小
const serialized = transaction.serialize({ requireAllSignatures: false });
console.log('交易大小:', serialized.length, '字节');

// 如果太大，拆分成多个交易
// 但注意：拆分后就不是原子操作了
```

**大小限制明细**：
- 签名：每个 64 字节
- 账户地址：每个 32 字节
- 指令数据：取决于具体操作
- 总计：不超过 1232 字节

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │    │  钱包    │    │  RPC     │    │ 验证节点  │    │  账本    │
│  发起    │───▶│  签名    │───▶│  广播    │───▶│  执行    │───▶│  确认    │
│  交易    │    │  交易    │    │  交易    │    │  交易    │    │  上链    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
【Transaction】 【Transaction】  【Transaction】 【Transaction】 【Transaction】
 构造消息体      添加签名       序列化发送      验证+执行      永久记录
 指定账户+指令   防止篡改       进入内存池      原子性保证      可查询
```

## Transaction 生命周期详解

```
1. 构造阶段
   ┌─────────────────────────────────┐
   │ 用户/DApp                       │
   │ - 确定要调用的 Program          │
   │ - 准备需要的 Account 列表       │
   │ - 组装指令数据                  │
   │ - 获取最新 blockhash            │
   └─────────────────────────────────┘
                 │
                 ▼
2. 签名阶段
   ┌─────────────────────────────────┐
   │ 钱包                            │
   │ - 显示交易详情给用户确认        │
   │ - 用私钥签名                    │
   │ - 可能需要多个签名者            │
   └─────────────────────────────────┘
                 │
                 ▼
3. 广播阶段
   ┌─────────────────────────────────┐
   │ RPC 节点                        │
   │ - 接收序列化的交易              │
   │ - 基础验证（签名、blockhash）   │
   │ - 转发给 Leader 节点            │
   └─────────────────────────────────┘
                 │
                 ▼
4. 执行阶段
   ┌─────────────────────────────────┐
   │ Leader 验证节点                 │
   │ - 加载涉及的所有 Account        │
   │ - 执行每条指令                  │
   │ - 任何失败则全部回滚            │
   │ - 成功则更新 Account 状态       │
   └─────────────────────────────────┘
                 │
                 ▼
5. 确认阶段
   ┌─────────────────────────────────┐
   │ 共识                            │
   │ - 其他节点验证并投票            │
   │ - 达到确认阈值后最终确认        │
   │ - 写入不可变账本                │
   └─────────────────────────────────┘
```

## 自测题

1. **基础题**：一个 Transaction 里有 3 条指令，第 2 条失败了，会发生什么？
   <details>
   <summary>答案</summary>
   整个 Transaction 失败回滚，3 条指令都不会生效。Transaction 是原子的，要么全成功，要么全失败。但仍会扣除 gas 费。
   </details>

2. **理解题**：为什么 Transaction 需要包含 recent blockhash？
   <details>
   <summary>答案</summary>
   防止重放攻击。如果没有 blockhash，别人可以复制你签过的交易反复提交。blockhash 有时效性（约 60-90 秒），过期后交易无效，保证同一笔交易只能执行一次。
   </details>

3. **实践题**：如何提高交易成功率？
   <details>
   <summary>答案</summary>
   1. 发送前重新获取最新 blockhash
   2. 设置合适的 priority fee（优先费）
   3. 使用 preflight 检查（模拟执行）
   4. 实现重试机制
   5. 确保账户有足够余额
   </details>
