# Wallet（钱包）

## 一句话大白话

**钱包是管理私钥的工具，私钥就是你在区块链上的"身份证+签名章"。有了私钥，你才能签署交易，证明"这笔操作是我发起的"。**

你可以把它想象成：银行的 U 盾——U 盾本身不存钱，钱在银行（区块链）里，但没有 U 盾你就没法操作账户。

## 它解决什么问题

在区块链上，我们需要：
1. **身份证明**：证明你是账户的主人
2. **授权操作**：允许某笔交易发生
3. **安全存储**：保护私钥不被盗

钱包就是解决这些问题的工具。

## 什么时候用 / 什么时候别用

### 什么时候需要钱包
- 任何链上操作都需要签名（转账、调用合约、创建账户...）
- 开发测试需要钱包
- 用户使用 DApp 需要钱包

### 钱包的类型选择

| 类型 | 适用场景 | 举例 |
|------|----------|------|
| 浏览器钱包 | 日常使用、DApp 交互 | Phantom, Solflare |
| 硬件钱包 | 大额资产存储 | Ledger |
| CLI 钱包 | 开发测试 | solana-keygen |
| 纸钱包 | 冷存储 | 手写助记词 |

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| 钱包存储代币 | 钱包只存私钥，代币数据在链上 |
| 钱包地址 = 私钥 | 地址（公钥）可以公开，私钥必须保密 |
| 换钱包会丢币 | 只要有私钥/助记词，用任何钱包都能恢复 |

### 密钥对的关系

```
┌─────────────────────────────────────────────────────────────┐
│                     密钥对关系图                            │
└─────────────────────────────────────────────────────────────┘

助记词 (12/24 个英文单词)
     │
     │ 通过算法派生
     ▼
私钥 (64 字节，必须保密)
     │
     │ 通过算法计算
     ▼
公钥 / 地址 (32 字节，可以公开)

重要：
- 知道助记词 → 可以推出私钥 → 可以推出公钥
- 知道公钥 → 无法反推私钥 → 无法反推助记词
- 只需要备份助记词，就能恢复一切
```

## 最小例子

### 1. 使用 CLI 创建钱包

```bash
# 安装 Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# 创建新钱包（会生成助记词）
solana-keygen new --outfile ~/my-wallet.json

# 输出示例:
# Generating a new keypair
#
# pubkey: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
#
# Save this seed phrase to recover your new keypair:
# abandon abandon abandon ... (12 个词)

# 查看地址
solana address -k ~/my-wallet.json

# 查看余额
solana balance -k ~/my-wallet.json --url devnet

# 获取测试币
solana airdrop 2 -k ~/my-wallet.json --url devnet
```

### 2. 使用 JavaScript 创建钱包

```javascript
import { Keypair, Connection, LAMPORTS_PER_SOL } from '@solana/web3.js';
import * as bip39 from 'bip39';

// 方法 1: 随机生成密钥对
const keypair = Keypair.generate();
console.log('公钥(地址):', keypair.publicKey.toBase58());
console.log('私钥:', Buffer.from(keypair.secretKey).toString('hex'));

// 方法 2: 从助记词恢复
const mnemonic = 'abandon abandon abandon ...'; // 你的助记词
const seed = bip39.mnemonicToSeedSync(mnemonic).slice(0, 32);
const keypairFromMnemonic = Keypair.fromSeed(seed);

// 方法 3: 从私钥文件恢复
import fs from 'fs';
const secretKey = JSON.parse(fs.readFileSync('/path/to/wallet.json'));
const keypairFromFile = Keypair.fromSecretKey(new Uint8Array(secretKey));
```

### 3. 使用钱包签署交易

```javascript
import {
  Connection,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
} from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');

// 构造交易
const transaction = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: sender.publicKey,
    toPubkey: receiver.publicKey,
    lamports: 0.1 * LAMPORTS_PER_SOL,
  })
);

// 签署并发送
// 钱包在这里完成签名
const signature = await sendAndConfirmTransaction(
  connection,
  transaction,
  [sender]  // sender 是 Keypair，包含私钥用于签名
);
```

### 4. 连接浏览器钱包（前端开发）

```javascript
// 使用 @solana/wallet-adapter-react
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';

function MyComponent() {
  const { publicKey, signTransaction, connected } = useWallet();

  const handleClick = async () => {
    if (!connected) {
      alert('请先连接钱包');
      return;
    }

    // 构造交易
    const transaction = new Transaction().add(...);

    // 请求钱包签名
    const signedTx = await signTransaction(transaction);

    // 发送已签名的交易
    const signature = await connection.sendRawTransaction(signedTx.serialize());
  };

  return (
    <div>
      <WalletMultiButton /> {/* 钱包连接按钮 */}
      {connected && <p>已连接: {publicKey.toBase58()}</p>}
      <button onClick={handleClick}>发送交易</button>
    </div>
  );
}
```

## 新手最常踩的 3 个坑

### 坑 1：助记词/私钥泄露

**问题**：把助记词发到网上、存到云端、截图分享...

**后果**：所有资产被盗，且无法找回

**安全做法**：
- 手写助记词在纸上，存放在安全的地方
- 永远不要在网上输入助记词（除非是官方钱包恢复）
- 永远不要把私钥以明文形式存储在代码库中

```javascript
// 错误！不要这样做
const PRIVATE_KEY = "1234abcd..."; // 明文私钥

// 正确：使用环境变量
const PRIVATE_KEY = process.env.SOLANA_PRIVATE_KEY;
```

### 坑 2：混淆 Devnet 和 Mainnet

**问题**：在测试网 airdrop 的币，想转到主网上用

**事实**：不同网络是隔离的，测试币毫无价值

```bash
# Devnet（测试网）
solana config set --url devnet
solana airdrop 2  # 这是测试币，不值钱

# Mainnet-Beta（主网）
solana config set --url mainnet-beta
# 这里的 SOL 是真金白银！
```

**检查当前网络**：
```bash
solana config get
# 看 RPC URL 是哪个
```

### 坑 3：不理解 Fee Payer

**问题**：交易失败，报错 "insufficient funds for fee"

**原因**：每笔交易需要有人支付 gas 费，默认是第一个签名者

```javascript
// 设置谁付 gas 费
transaction.feePayer = payer.publicKey;

// 确保 payer 有足够的 SOL
const balance = await connection.getBalance(payer.publicKey);
console.log('余额:', balance / LAMPORTS_PER_SOL, 'SOL');
// 一般保留 0.01 SOL 以上
```

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │    │ 【钱包】  │    │  RPC     │
│  发起    │───▶│  签名    │───▶│  广播    │
│  交易    │    │  交易    │    │  交易    │
└──────────┘    └──────────┘    └──────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  钱包的职责：      │
            │  1. 保管私钥      │
            │  2. 展示交易内容  │
            │  3. 用私钥签名    │
            │  4. 防止钓鱼      │
            └──────────────────┘
```

## 常用钱包对比

### 浏览器钱包

| 钱包 | 特点 | 适用 |
|------|------|------|
| Phantom | 最流行，界面友好 | 日常使用 |
| Solflare | 功能丰富，支持 Ledger | 进阶用户 |
| Backpack | xNFT 生态 | Web3 社交 |

### 开发工具

| 工具 | 特点 | 适用 |
|------|------|------|
| solana-keygen | CLI 工具 | 本地开发 |
| @solana/web3.js | JS SDK | 前后端开发 |
| Anchor | 框架内置 | 合约开发 |

## HD 钱包和派生路径

### 什么是 HD 钱包

**HD = Hierarchical Deterministic（分层确定性）**

从一个助记词可以派生出无数个地址：

```
助记词
   │
   ├── 账户 0：7xKXt...
   │      ├── 地址 0
   │      ├── 地址 1
   │      └── ...
   ├── 账户 1：8yLYu...
   └── ...
```

### Solana 的派生路径

```
m/44'/501'/0'/0'

解释：
- 44' : BIP-44 标准
- 501' : Solana 的币种编号
- 0' : 账户索引
- 0' : 地址索引

常见钱包的默认路径：
- Phantom: m/44'/501'/0'/0'
- Solflare: m/44'/501'/0'/0'
- CLI: m/44'/501'/0'/0' (使用 --derivation-path 可自定义)
```

## 自测题

1. **基础题**：助记词和私钥有什么区别？
   <details>
   <summary>答案</summary>
   - 助记词是便于人类记忆的12/24个英文单词
   - 私钥是64字节的数字
   - 助记词可以派生出私钥
   - 备份助记词就等于备份了所有私钥
   </details>

2. **理解题**：为什么"换钱包不会丢币"？
   <details>
   <summary>答案</summary>
   因为代币不在钱包里，在区块链上。钱包只是管理私钥的工具。只要有私钥/助记词，用任何支持 Solana 的钱包都能访问你的资产。
   </details>

3. **安全题**：如何安全地在服务器上使用私钥？
   <details>
   <summary>答案</summary>
   1. 使用环境变量存储，不要硬编码
   2. 使用密钥管理服务（AWS KMS、HashiCorp Vault）
   3. 服务器权限最小化
   4. 不要在日志中打印私钥
   5. 定期轮换密钥
   </details>
