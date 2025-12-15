# 创建并转账 SPL Token - 单点穿透演练

## 案例背景

**目标**：创建一个属于自己的代币（SPL Token），铸造 1000 个，然后转账 100 个给另一个地址。

**为什么选这个案例**：
1. 覆盖 Solana 核心概念：Account、Program、Transaction、Wallet
2. 实际操作链上状态变化
3. 理解代码和数据分离的设计
4. 为后续 DApp 开发打下基础

**最终产出**：
- 一个 Mint Account（代币定义）
- 两个 Token Account（你和接收方的代币余额）
- 完整的交易记录

---

## 准备工作

### 1. 安装环境

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 安装 Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# 验证安装
solana --version
# 输出: solana-cli 1.18.x

# 安装 SPL Token CLI
cargo install spl-token-cli
```

### 2. 配置网络和钱包

```bash
# 切换到 Devnet（测试网）
solana config set --url devnet

# 创建钱包
solana-keygen new --outfile ~/my-wallet.json

# 设为默认钱包
solana config set --keypair ~/my-wallet.json

# 查看地址
solana address
# 输出: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

# 获取测试币
solana airdrop 2
# 输出: Requesting airdrop of 2 SOL...
# Signature: xxx
# 2 SOL

# 确认余额
solana balance
# 输出: 2 SOL
```

---

## 流程演练

### 节点 1：创建代币（Mint）

**输入**：
- 你的钱包（付费者 + Mint Authority）
- 代币参数（小数位数，默认 9）

**加工**：
- 调用 Token Program
- 创建 Mint Account
- 设置你为 Mint Authority

**输出**：
- Mint Account 地址
- 交易签名

```bash
# 创建代币
spl-token create-token

# 输出:
# Creating token 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
# Signature: 5VERv8NMvLYX...
#
# Address: 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
# Decimals: 9
```

**验证**：
```bash
# 查看 Mint 信息
spl-token display 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# 输出:
# SPL Token Mint
#   Address: 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
#   Mint Authority: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU  ← 是你的地址
#   Supply: 0                                                      ← 还没铸造
#   Decimals: 9
#   Freeze Authority: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
```

**链上发生了什么**：
```
┌─────────────────────────────────────────────────────────────┐
│                创建 Mint 的过程                              │
└─────────────────────────────────────────────────────────────┘

1. 你的交易调用 Token Program

2. Token Program 创建新的 Mint Account:
   ┌────────────────────────────────────────┐
   │ Mint Account                          │
   │ Address: 4zMMC9...                    │
   │                                        │
   │ Data:                                 │
   │   - supply: 0                         │
   │   - decimals: 9                       │
   │   - mint_authority: 你的地址          │
   │   - freeze_authority: 你的地址        │
   │                                        │
   │ Owner: Token Program                  │
   │ Lamports: 0.00144 SOL (免租金额度)     │
   └────────────────────────────────────────┘

3. 从你的钱包扣除:
   - 创建账户费: 0.00144 SOL
   - 交易费: 0.000005 SOL
```

**常见失败原因**：
1. 钱包余额不足（需要约 0.002 SOL）
2. 网络问题（RPC 节点无响应）
3. Airdrop 限制（Devnet 每次最多 2 SOL）

---

### 节点 2：创建 Token Account

**输入**：
- Mint 地址
- 所有者地址（你的钱包）

**加工**：
- 调用 Associated Token Program
- 计算 ATA 地址
- 创建 Token Account

**输出**：
- Token Account 地址
- 交易签名

```bash
# 创建你的 Token Account（用于存储代币余额）
spl-token create-account 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# 输出:
# Creating account 8YjNuD7yrV52mFPNnhxPBG7Q3VxqVnv5NyC6DnLQmvnz
# Signature: 4VERv8NMvLYX...
```

**验证**：
```bash
# 查看 Token Account
spl-token accounts 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# 输出:
# Account                                      Token                                         Balance
# -------------------------------------------- --------------------------------------------- --------
# 8YjNuD7yrV52mFPNnhxPBG7Q3VxqVnv5NyC6DnLQmvnz 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU       0
```

**链上发生了什么**：
```
┌─────────────────────────────────────────────────────────────┐
│                创建 Token Account 的过程                     │
└─────────────────────────────────────────────────────────────┘

1. 计算 ATA 地址:
   ATA = PDA(你的钱包, Token Program, Mint地址)
       = 8YjNuD7yrV52mFPNnhxPBG7Q3VxqVnv5NyC6DnLQmvnz

2. 创建 Token Account:
   ┌────────────────────────────────────────┐
   │ Token Account (ATA)                   │
   │ Address: 8YjNuD7...                   │
   │                                        │
   │ Data:                                 │
   │   - mint: 4zMMC9...                   │
   │   - owner: 你的钱包地址                │
   │   - amount: 0                         │
   │   - delegate: None                    │
   │   - state: Initialized                │
   │                                        │
   │ Owner: Token Program                  │
   │ Lamports: 0.00203 SOL (免租金额度)     │
   └────────────────────────────────────────┘

3. 从你的钱包扣除:
   - 创建账户费: 0.00203 SOL
   - 交易费: 0.000005 SOL
```

**常见失败原因**：
1. Mint 地址错误（复制粘贴问题）
2. Token Account 已存在（重复创建）
3. 余额不足

---

### 节点 3：铸造代币

**输入**：
- Mint 地址
- 目标 Token Account
- 铸造数量
- Mint Authority 签名

**加工**：
- 验证 Mint Authority
- 增加 Supply
- 增加 Token Account 余额

**输出**：
- 更新后的余额
- 交易签名

```bash
# 铸造 1000 个代币
spl-token mint 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU 1000

# 输出:
# Minting 1000 tokens
#   Token: 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
#   Recipient: 8YjNuD7yrV52mFPNnhxPBG7Q3VxqVnv5NyC6DnLQmvnz
# Signature: 3VERv8NMvLYX...
```

**验证**：
```bash
# 查看余额
spl-token balance 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# 输出: 1000

# 查看 Mint 供应量变化
spl-token supply 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU

# 输出: 1000
```

**链上发生了什么**：
```
┌─────────────────────────────────────────────────────────────┐
│                    铸造代币的过程                            │
└─────────────────────────────────────────────────────────────┘

交易内容:
┌──────────────────────────────────────────────────────────┐
│ Transaction                                              │
│ ├── Instruction: MintTo                                  │
│ │   ├── program: Token Program                          │
│ │   ├── accounts:                                        │
│ │   │   ├── mint: 4zMMC9... (writable)                  │
│ │   │   ├── destination: 8YjNuD7... (writable)          │
│ │   │   └── authority: 你的钱包 (signer)                │
│ │   └── data: amount = 1000 * 10^9                      │
│ └── Signature: 你的私钥签名                              │
└──────────────────────────────────────────────────────────┘

执行后状态变化:

Mint Account:
  supply: 0 → 1000000000000 (1000 * 10^9)

Token Account:
  amount: 0 → 1000000000000
```

**常见失败原因**：
1. 不是 Mint Authority（无权铸造）
2. Token Account 不存在
3. 数值溢出（超过 u64 最大值）

---

### 节点 4：转账代币

**输入**：
- 发送方 Token Account
- 接收方地址
- 转账数量
- 发送方签名

**加工**：
- 验证发送方权限
- 检查/创建接收方 Token Account
- 转移余额

**输出**：
- 双方余额更新
- 交易签名

```bash
# 创建接收方地址（模拟另一个用户）
solana-keygen new --no-bip39-passphrase --outfile ~/receiver-wallet.json
RECEIVER=$(solana address -k ~/receiver-wallet.json)
echo "接收方地址: $RECEIVER"

# 转账 100 个代币
# --fund-recipient: 自动为接收方创建 Token Account 并支付费用
spl-token transfer 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU 100 $RECEIVER --fund-recipient

# 输出:
# Transfer 100 tokens
#   Sender: 8YjNuD7yrV52mFPNnhxPBG7Q3VxqVnv5NyC6DnLQmvnz
#   Recipient: CfMF3Xvt...  (接收方的 ATA，自动创建)
# Signature: 2VERv8NMvLYX...
```

**验证**：
```bash
# 查看你的余额
spl-token balance 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
# 输出: 900

# 查看接收方余额
spl-token balance --owner $RECEIVER 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
# 输出: 100
```

**链上发生了什么**：
```
┌─────────────────────────────────────────────────────────────┐
│               转账代币的过程（带自动创建 ATA）               │
└─────────────────────────────────────────────────────────────┘

Transaction 包含两条指令:

指令 1: CreateAssociatedTokenAccount
┌──────────────────────────────────────────────────────────┐
│ 为接收方创建 Token Account                               │
│ ├── 计算接收方的 ATA 地址                                │
│ ├── 创建账户                                             │
│ └── 从发送方扣除 0.00203 SOL                             │
└──────────────────────────────────────────────────────────┘

指令 2: Transfer
┌──────────────────────────────────────────────────────────┐
│ 转移代币                                                 │
│ ├── 从发送方 Token Account 扣除 100                      │
│ └── 给接收方 Token Account 增加 100                      │
└──────────────────────────────────────────────────────────┘

状态变化:

你的 Token Account:
  amount: 1000000000000 → 900000000000

接收方 Token Account (新创建):
  amount: 0 → 100000000000

你的钱包:
  lamports: 减少 (创建 ATA 费 + 交易费)
```

**常见失败原因**：
1. 余额不足（代币或 SOL）
2. 接收方地址错误
3. 未使用 `--fund-recipient` 且接收方没有 Token Account

---

## 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SPL Token 创建和转账完整流程                            │
└─────────────────────────────────────────────────────────────────────────────┘

你的钱包 (2 SOL)
    │
    │ create-token
    ▼
┌──────────────────────┐
│ Mint Account 创建    │ ─────────────────────────────────────┐
│ 4zMMC9...           │                                       │
│ supply: 0           │                                       │
│ authority: 你       │                                       │
└──────────────────────┘                                       │
    │                                                          │
    │ create-account                                           │
    ▼                                                          │
┌──────────────────────┐                                       │
│ 你的 Token Account  │                                       │
│ 8YjNuD7...          │ ◄────────────────────────────────────┤
│ balance: 0          │                                       │
└──────────────────────┘                                       │
    │                                                          │
    │ mint 1000                                                │
    ▼                                                          │
┌──────────────────────┐                                       │
│ 你的 Token Account  │                                       │
│ 8YjNuD7...          │      Mint: supply 0 → 1000            │
│ balance: 1000       │ ◄─────────────────────────────────────┘
└──────────────────────┘
    │
    │ transfer 100
    ▼
┌──────────────────────┐     ┌──────────────────────┐
│ 你的 Token Account  │     │ 接收方 Token Account │
│ 8YjNuD7...          │     │ CfMF3X... (自动创建)  │
│ balance: 900        │     │ balance: 100         │
└──────────────────────┘     └──────────────────────┘
```

---

## 常见坑点提醒

### 坑点 1：小数位数混淆

```
代币有 9 位小数（默认）

显示 "1000" 代币
实际存储 1000 * 10^9 = 1,000,000,000,000

如果你想要 1000.5 个代币:
spl-token mint <mint> 1000.5
# 实际存储: 1000500000000
```

### 坑点 2：忘记 --fund-recipient

```bash
# 错误：接收方没有 Token Account
spl-token transfer <mint> 100 <receiver>
# Error: Recipient's associated token account does not exist

# 正确：使用 --fund-recipient 自动创建
spl-token transfer <mint> 100 <receiver> --fund-recipient
```

### 坑点 3：在错误的网络上操作

```bash
# 检查当前网络
solana config get

# 确保在 Devnet
solana config set --url devnet

# 不要在 Mainnet 上做测试！
```

---

## 使用 JavaScript 实现

```javascript
// complete-flow.js
import {
  Connection,
  Keypair,
  LAMPORTS_PER_SOL,
  clusterApiUrl,
} from '@solana/web3.js';
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
  transfer,
} from '@solana/spl-token';

async function main() {
  // 1. 连接 Devnet
  const connection = new Connection(clusterApiUrl('devnet'), 'confirmed');

  // 2. 创建钱包（实际使用时从文件加载）
  const payer = Keypair.generate();
  const receiver = Keypair.generate();

  // 3. 获取空投
  console.log('获取空投...');
  const airdropSig = await connection.requestAirdrop(
    payer.publicKey,
    2 * LAMPORTS_PER_SOL
  );
  await connection.confirmTransaction(airdropSig);
  console.log('余额:', (await connection.getBalance(payer.publicKey)) / LAMPORTS_PER_SOL, 'SOL');

  // 4. 创建代币
  console.log('创建代币...');
  const mint = await createMint(
    connection,
    payer,           // 付费者
    payer.publicKey, // Mint Authority
    null,            // Freeze Authority (无)
    9                // Decimals
  );
  console.log('Mint 地址:', mint.toBase58());

  // 5. 创建你的 Token Account
  console.log('创建 Token Account...');
  const payerTokenAccount = await getOrCreateAssociatedTokenAccount(
    connection,
    payer,
    mint,
    payer.publicKey
  );
  console.log('你的 Token Account:', payerTokenAccount.address.toBase58());

  // 6. 铸造代币
  console.log('铸造 1000 代币...');
  await mintTo(
    connection,
    payer,
    mint,
    payerTokenAccount.address,
    payer,
    1000 * 10 ** 9  // 1000 个代币
  );
  console.log('铸造完成');

  // 7. 创建接收方 Token Account
  console.log('创建接收方 Token Account...');
  const receiverTokenAccount = await getOrCreateAssociatedTokenAccount(
    connection,
    payer,            // 付费者（由发送方付费）
    mint,
    receiver.publicKey
  );
  console.log('接收方 Token Account:', receiverTokenAccount.address.toBase58());

  // 8. 转账
  console.log('转账 100 代币...');
  await transfer(
    connection,
    payer,
    payerTokenAccount.address,
    receiverTokenAccount.address,
    payer,
    100 * 10 ** 9  // 100 个代币
  );
  console.log('转账完成');

  // 9. 查看最终状态
  const payerBalance = await connection.getTokenAccountBalance(payerTokenAccount.address);
  const receiverBalance = await connection.getTokenAccountBalance(receiverTokenAccount.address);

  console.log('\n=== 最终状态 ===');
  console.log('你的余额:', payerBalance.value.uiAmount, '代币');
  console.log('接收方余额:', receiverBalance.value.uiAmount, '代币');
}

main().catch(console.error);
```

运行：
```bash
npm init -y
npm install @solana/web3.js @solana/spl-token
node complete-flow.js
```

---

## 复盘

### 我学到的 3 件事

1. **代码和数据分离**
   - Token Program 是共用的代码
   - 每个 Mint、每个 Token Account 是独立的数据账户
   - 这就是 Solana 高效的原因

2. **Account 是核心**
   - 创建代币 = 创建 Mint Account
   - 接收代币 = 先有 Token Account
   - 所有状态都在 Account 里

3. **交易是原子的**
   - `--fund-recipient` 包含两条指令
   - 创建 ATA + 转账 要么全成功，要么全失败

### 仍不确定的 3 件事

1. 多签名钱包如何操作 Token？
2. Token-2022（新标准）和 SPL Token 有什么区别？
3. 如何在生产环境安全管理 Mint Authority？

### 下一步要查的 3 个点

1. **PDA 的使用**：如何用 Program 签名代替个人签名
2. **CPI（跨程序调用）**：Program 如何调用 Token Program
3. **Metaplex**：如何给代币添加元数据（名称、图标、符号）

---

## 费用总结

| 操作 | 费用 | 说明 |
|------|------|------|
| 创建 Mint | ~0.00144 SOL | Mint Account 免租金额 |
| 创建 Token Account | ~0.00203 SOL | Token Account 免租金额 |
| 铸造 | ~0.000005 SOL | 只有交易费 |
| 转账 | ~0.000005 SOL | 只有交易费 |
| 自动创建 ATA | ~0.00203 SOL | 使用 --fund-recipient 时 |

**总计**：完成本案例约需 0.005 SOL，Devnet 空投足够用。
