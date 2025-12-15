# 从零部署你的第一个代币 - 单点穿透演练

## 案例背景

**目标**：创建并部署一个 ERC-20 代币，完整体验以太坊开发的全流程。

这个案例将带你走完从「一个想法」到「链上运行的代币」的完整路径，每一步都会对应到前面学习的概念。

**我们要做的**：
1. 创建一个叫 `MyToken (MTK)` 的代币
2. 总量 100 万个
3. 在测试网部署
4. 验证合约代码
5. 和代币交互（转账）

---

## 准备工作

### 需要的工具

```bash
# 1. Node.js (v18+)
node --version

# 2. 包管理器（npm 或 yarn）
npm --version

# 3. 创建项目目录
mkdir my-token && cd my-token
npm init -y

# 4. 安装开发工具
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# 5. 初始化 Hardhat 项目
npx hardhat init
# 选择 "Create a JavaScript project"
```

### 获取测试网 ETH

```
1. 安装 MetaMask 浏览器扩展
2. 切换到 Sepolia 测试网
3. 访问水龙头获取测试 ETH：
   - https://sepoliafaucet.com/
   - https://www.alchemy.com/faucets/ethereum-sepolia
4. 等待 ETH 到账（通常几分钟）
```

---

## 流程演练

```
┌─────────────────────────────────────────────────────────────────────┐
│                    代币部署完整流程                                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 编写合约 │ → │ 编译合约 │ → │ 部署合约 │ → │ 验证合约 │ → │ 交互测试 │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │              │
     v              v              v              v              v
  Solidity       字节码         上链交易        源码公开       转账代币
   代码          + ABI          消耗Gas         Etherscan
```

---

### 节点 1：编写智能合约

**输入**：业务需求（代币名称、符号、总量）

**加工**：编写 Solidity 代码

创建 `contracts/MyToken.sol`：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// 导入 OpenZeppelin 的 ERC-20 实现
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title MyToken
 * @dev 一个简单的 ERC-20 代币
 *
 * 对应学习内容：
 * - 智能合约章节：合约结构、继承、构造函数
 * - 流程图位置：合约代码 → 编译
 */
contract MyToken is ERC20 {
    /**
     * @dev 构造函数，部署时执行一次
     * @param initialSupply 初始供应量（单位：代币的最小单位）
     *
     * ERC-20 默认 18 位小数，所以：
     * - 1 MTK = 1 * 10^18 个最小单位
     * - 1,000,000 MTK = 1,000,000 * 10^18
     */
    constructor(uint256 initialSupply) ERC20("MyToken", "MTK") {
        // _mint 是 ERC20 的内部函数，用于创建代币
        // msg.sender 是部署合约的地址
        // 所有代币都会发到部署者地址
        _mint(msg.sender, initialSupply);
    }
}
```

**输出**：`.sol` 源代码文件

**常见失败原因**：

1. **编译器版本不匹配**
   ```solidity
   // 错误：OpenZeppelin 需要 ^0.8.20，但你用的是 0.8.0
   pragma solidity ^0.8.0;  // 改成 ^0.8.20
   ```

2. **忘记安装 OpenZeppelin**
   ```bash
   npm install @openzeppelin/contracts
   ```

3. **语法错误**
   - 缺少分号
   - 括号不匹配
   - 关键字拼写错误

---

### 节点 2：编译合约

**输入**：Solidity 源代码

**加工**：Solidity 编译器将代码编译成 EVM 字节码

```bash
npx hardhat compile
```

**输出**：
- `artifacts/contracts/MyToken.sol/MyToken.json`（包含 ABI 和字节码）

**查看编译输出**：

```javascript
// 读取编译结果
const fs = require('fs');
const artifact = JSON.parse(
    fs.readFileSync('artifacts/contracts/MyToken.sol/MyToken.json')
);

console.log('合约 ABI:', artifact.abi);
console.log('字节码长度:', artifact.bytecode.length, '字符');
```

**检查点**：
- [ ] 编译成功无错误
- [ ] 生成了 `artifacts` 目录
- [ ] 可以找到 `MyToken.json` 文件

**常见失败原因**：

1. **依赖未安装**
   ```bash
   npm install @openzeppelin/contracts
   ```

2. **Hardhat 配置错误**
   ```javascript
   // hardhat.config.js
   require("@nomicfoundation/hardhat-toolbox");
   module.exports = {
     solidity: "0.8.20",  // 确保版本匹配
   };
   ```

3. **路径错误**
   - 确保合约在 `contracts/` 目录下
   - 文件名和合约名最好一致

---

### 节点 3：部署合约

**输入**：编译后的字节码 + 部署参数

**加工**：构造部署交易，签名并广播

**配置网络和私钥**：

```javascript
// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: "https://sepolia.infura.io/v3/YOUR_INFURA_KEY",
      // 或者使用 Alchemy: "https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
      accounts: ["YOUR_PRIVATE_KEY"]  // 不要提交到 Git！
    }
  },
  etherscan: {
    apiKey: "YOUR_ETHERSCAN_API_KEY"  // 用于验证合约
  }
};
```

**创建部署脚本** `scripts/deploy.js`：

```javascript
const hre = require("hardhat");

async function main() {
    // 获取部署者信息
    const [deployer] = await hre.ethers.getSigners();
    console.log("部署者地址:", deployer.address);

    // 检查余额
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("账户余额:", hre.ethers.formatEther(balance), "ETH");

    // 部署参数：100万代币，每个代币有18位小数
    const initialSupply = hre.ethers.parseEther("1000000");  // 1,000,000 * 10^18

    // 获取合约工厂
    const MyToken = await hre.ethers.getContractFactory("MyToken");

    // 部署合约
    console.log("正在部署合约...");
    const token = await MyToken.deploy(initialSupply);

    // 等待部署完成
    await token.waitForDeployment();

    const address = await token.getAddress();
    console.log("合约部署成功！");
    console.log("合约地址:", address);
    console.log("区块浏览器:", `https://sepolia.etherscan.io/address/${address}`);

    // 验证部署结果
    const name = await token.name();
    const symbol = await token.symbol();
    const totalSupply = await token.totalSupply();

    console.log("\n代币信息:");
    console.log("名称:", name);
    console.log("符号:", symbol);
    console.log("总量:", hre.ethers.formatEther(totalSupply), symbol);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("部署失败:", error);
        process.exit(1);
    });
```

**执行部署**：

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

**输出**：
- 合约地址
- 交易哈希
- 区块浏览器链接

**检查点**：
- [ ] 交易已确认
- [ ] 合约地址已生成
- [ ] 可以在 Etherscan 上看到合约

**常见失败原因**：

1. **余额不足**
   ```
   Error: insufficient funds for gas * price + value
   解决：去水龙头获取更多测试 ETH
   ```

2. **Gas 估算失败**
   ```
   Error: cannot estimate gas
   可能原因：构造函数参数错误、合约代码有问题
   ```

3. **Nonce 问题**
   ```
   Error: nonce too low
   解决：等待之前的交易确认，或手动指定 nonce
   ```

---

### 节点 4：验证合约

**输入**：合约地址 + 源代码 + 构造函数参数

**加工**：Etherscan 编译源代码，对比链上字节码

**为什么要验证**：
- 让任何人都可以看到合约代码
- 建立信任
- 可以直接在 Etherscan 上交互

**使用 Hardhat 验证**：

```bash
npx hardhat verify --network sepolia CONTRACT_ADDRESS "1000000000000000000000000"
# 参数是 initialSupply，用 Wei 表示
```

**或手动在 Etherscan 验证**：

1. 打开合约页面：`https://sepolia.etherscan.io/address/YOUR_CONTRACT`
2. 点击 "Contract" → "Verify and Publish"
3. 选择编译器版本：0.8.20
4. 选择许可证：MIT
5. 粘贴合约代码（包括 import 的内容）
6. 输入构造函数参数（ABI 编码）

**输出**：合约页面显示绿色对勾 ✓

**常见失败原因**：

1. **编译器版本不匹配**
   - 确保 Etherscan 选择的版本和 hardhat.config.js 一致

2. **构造函数参数错误**
   ```javascript
   // 获取 ABI 编码的构造函数参数
   const abiCoder = new ethers.AbiCoder();
   const encoded = abiCoder.encode(
       ["uint256"],
       [ethers.parseEther("1000000")]
   );
   console.log(encoded);
   ```

3. **代码不匹配**
   - 确保提交的代码和部署时用的完全一致
   - 包括空格、注释

---

### 节点 5：交互测试

**输入**：合约地址 + ABI + 钱包

**加工**：发送交易调用合约函数

**创建交互脚本** `scripts/interact.js`：

```javascript
const hre = require("hardhat");

// 替换为你部署的合约地址
const CONTRACT_ADDRESS = "YOUR_CONTRACT_ADDRESS";

async function main() {
    const [owner, recipient] = await hre.ethers.getSigners();

    // 连接到已部署的合约
    const MyToken = await hre.ethers.getContractFactory("MyToken");
    const token = MyToken.attach(CONTRACT_ADDRESS);

    console.log("=== 查询操作（免费，不需要 Gas）===\n");

    // 查询代币信息
    const name = await token.name();
    const symbol = await token.symbol();
    const decimals = await token.decimals();
    const totalSupply = await token.totalSupply();

    console.log(`代币名称: ${name}`);
    console.log(`代币符号: ${symbol}`);
    console.log(`小数位数: ${decimals}`);
    console.log(`总供应量: ${hre.ethers.formatEther(totalSupply)} ${symbol}`);

    // 查询余额
    const ownerBalance = await token.balanceOf(owner.address);
    console.log(`\n你的余额: ${hre.ethers.formatEther(ownerBalance)} ${symbol}`);

    console.log("\n=== 转账操作（需要 Gas）===\n");

    // 转账
    const transferAmount = hre.ethers.parseEther("1000");  // 转 1000 MTK
    const recipientAddress = recipient?.address || "0x0000000000000000000000000000000000000001";

    console.log(`转账 1000 ${symbol} 到 ${recipientAddress}...`);

    const tx = await token.transfer(recipientAddress, transferAmount);
    console.log(`交易哈希: ${tx.hash}`);
    console.log("等待确认...");

    const receipt = await tx.wait();
    console.log(`交易确认！区块号: ${receipt.blockNumber}`);
    console.log(`Gas 消耗: ${receipt.gasUsed.toString()}`);

    // 查询转账后的余额
    const newBalance = await token.balanceOf(owner.address);
    console.log(`\n转账后余额: ${hre.ethers.formatEther(newBalance)} ${symbol}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
```

**执行交互**：

```bash
npx hardhat run scripts/interact.js --network sepolia
```

**输出**：
- 代币信息
- 余额查询结果
- 转账交易哈希
- 转账后的余额

**检查点**：
- [ ] 可以查询代币信息
- [ ] 可以查询余额
- [ ] 转账交易成功
- [ ] 余额变化正确

**常见失败原因**：

1. **余额不足**
   ```
   ERC20: transfer amount exceeds balance
   ```

2. **合约地址错误**
   ```
   检查 CONTRACT_ADDRESS 是否正确
   ```

3. **网络不对**
   ```
   确保 --network 参数正确
   ```

---

## 完整流程回顾

```
┌─────────────────────────────────────────────────────────────────────┐
│                    你刚才完成了什么                                  │
└─────────────────────────────────────────────────────────────────────┘

1. 编写合约（智能合约章节）
   └─ 使用 Solidity 编写 ERC-20 代币

2. 编译合约（EVM 章节）
   └─ Solidity → 字节码 + ABI

3. 部署合约（交易与签名章节）
   └─ 构造交易 → 签名 → 广播 → 确认
   └─ 消耗了 Gas（Gas 机制章节）

4. 验证合约
   └─ 让代码公开可审计

5. 交互测试
   └─ 读取操作：view 函数，免费
   └─ 写入操作：需要签名和 Gas

恭喜！你已经：
✓ 创建了自己的加密代币
✓ 理解了从代码到链上的完整流程
✓ 实践了钱包、交易、Gas 等概念
✓ 学会了使用开发工具链
```

---

## 常见坑点提醒

### 1. 私钥安全

```
❌ 绝对不要做：
- 把私钥写在代码里提交到 Git
- 使用主网私钥做测试
- 把私钥发给任何人

✅ 正确做法：
- 使用环境变量
- 测试网用专门的测试钱包
- 使用 .env 文件 + .gitignore
```

```javascript
// 安全的配置方式
require('dotenv').config();

module.exports = {
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_URL,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

### 2. Gas 费用

```
测试网 Gas 免费，但主网很贵！

部署一个简单 ERC-20 合约：
- 测试网：免费（测试 ETH）
- 主网：约 $50-200（取决于网络拥堵）

建议：
- 先在测试网充分测试
- 选择 Gas 低的时候部署
- 使用 L2（如 Arbitrum、Optimism）省钱
```

### 3. 合约不可变

```
合约部署后代码无法修改！

发现 bug 怎么办：
1. 如果是关键漏洞：紧急暂停（如果有暂停功能）
2. 部署新合约，迁移资产
3. 如果有升级机制：通过代理合约升级

所以：
- 充分测试
- 做代码审计
- 考虑是否需要升级机制
```

---

## 复盘

### 我学到的 3 件事

1. **智能合约是真实的代码在真实的网络上运行**
   - 每一行代码都要经过编译、部署、执行
   - 错误会造成真实的损失
   - 要像写金融系统一样谨慎

2. **Gas 是所有操作的成本**
   - 部署合约需要 Gas
   - 写操作需要 Gas
   - 读操作免费（只是查询）

3. **工具链帮你处理复杂细节**
   - Hardhat 封装了编译、部署、验证
   - ethers.js 封装了签名、广播
   - 但要理解底层在做什么

### 仍不确定的 3 件事

1. **如何优化 Gas 消耗？**
   - 学习 EVM 操作码的成本
   - 学习 Solidity 优化技巧

2. **如何做合约升级？**
   - 代理模式（Proxy Pattern）
   - OpenZeppelin Upgrades 插件

3. **如何处理安全问题？**
   - 常见漏洞类型
   - 代码审计流程
   - 安全最佳实践

### 下一步要查的 3 个点

1. **ERC-20 标准的完整规范**
   - approve/transferFrom 机制
   - 事件和日志
   - 扩展功能（铸造、销毁、暂停）

2. **更多代币标准**
   - ERC-721（NFT）
   - ERC-1155（多代币）
   - ERC-4626（金库）

3. **DeFi 集成**
   - 把代币添加到 Uniswap
   - 在借贷协议中使用
   - 创建流动性池

---

## 进阶挑战

完成基础部署后，尝试：

1. **添加更多功能**
   ```solidity
   // 可铸造的代币
   function mint(address to, uint256 amount) public onlyOwner {
       _mint(to, amount);
   }

   // 可销毁的代币
   function burn(uint256 amount) public {
       _burn(msg.sender, amount);
   }
   ```

2. **部署到主网**
   - 使用真实的 ETH
   - 做好充分测试

3. **创建一个简单的 DApp**
   - 前端界面
   - 连接 MetaMask
   - 显示余额、支持转账

4. **学习更复杂的合约**
   - 多签钱包
   - DAO 治理
   - DeFi 协议
