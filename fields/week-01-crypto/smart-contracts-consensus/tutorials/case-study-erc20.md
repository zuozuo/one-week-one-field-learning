# ERC-20 代币实战 - 单点穿透演练

## 案例背景

**目标**：从零开始，完整走一遍创建、部署、交互 ERC-20 代币的全流程。

**什么是 ERC-20？**
- ERC = Ethereum Request for Comments（以太坊改进提案）
- 20 = 提案编号
- 定义了代币的标准接口，让所有代币都能用同样的方式交互

**为什么选这个案例？**
- ERC-20 是最常用的代币标准
- 涉及智能合约的核心概念
- 从这个点可以打通整个合约开发流程

---

## 流程演练

### 节点 1：理解 ERC-20 标准

**输入**：ERC-20 提案文档

**加工**：提取必须实现的接口

**输出**：接口规范

```solidity
// ERC-20 标准必须实现的接口
interface IERC20 {
    // ========== 查询函数 ==========

    // 代币总供应量
    function totalSupply() external view returns (uint256);

    // 查询某地址的余额
    function balanceOf(address account) external view returns (uint256);

    // 查询授权额度：owner 授权给 spender 的额度
    function allowance(address owner, address spender) external view returns (uint256);


    // ========== 操作函数 ==========

    // 转账：从自己账户转给别人
    function transfer(address to, uint256 amount) external returns (bool);

    // 授权：允许 spender 从我账户最多转走 amount
    function approve(address spender, uint256 amount) external returns (bool);

    // 代转账：从 from 转给 to（需要 from 事先授权）
    function transferFrom(address from, address to, uint256 amount) external returns (bool);


    // ========== 事件 ==========

    // 转账事件
    event Transfer(address indexed from, address indexed to, uint256 value);

    // 授权事件
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

**检查点**：
- ✅ 我知道 ERC-20 有 6 个必须实现的函数
- ✅ 我理解 `approve` + `transferFrom` 的组合用法
- ✅ 我知道事件是用来记录日志的

**常见失败原因**：
1. 忘记实现某个必须的函数
2. 函数签名写错（参数顺序、返回值类型）
3. 忘记触发事件

---

### 节点 2：编写合约代码

**输入**：ERC-20 接口规范

**加工**：实现完整的代币合约

**输出**：可编译的 .sol 文件

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MyToken - 一个简单的 ERC-20 代币实现
 * @dev 包含完整的 ERC-20 标准实现 + 常用扩展
 */
contract MyToken {
    // ==================== 状态变量 ====================

    string public name;           // 代币名称，如 "My Token"
    string public symbol;         // 代币符号，如 "MTK"
    uint8 public decimals;        // 小数位数，通常是 18
    uint256 public totalSupply;   // 总供应量

    // 余额映射：地址 => 余额
    mapping(address => uint256) public balanceOf;

    // 授权映射：授权人 => (被授权人 => 额度)
    mapping(address => mapping(address => uint256)) public allowance;


    // ==================== 事件 ====================

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);


    // ==================== 构造函数 ====================

    /**
     * @dev 部署时初始化代币
     * @param _name 代币名称
     * @param _symbol 代币符号
     * @param _initialSupply 初始供应量（会乘以 10^18）
     */
    constructor(string memory _name, string memory _symbol, uint256 _initialSupply) {
        name = _name;
        symbol = _symbol;
        decimals = 18;  // 标准小数位数

        // 计算实际供应量（带 18 位小数）
        uint256 supply = _initialSupply * 10 ** uint256(decimals);
        totalSupply = supply;

        // 全部代币分配给部署者
        balanceOf[msg.sender] = supply;

        // 触发转账事件（从零地址转入表示铸造）
        emit Transfer(address(0), msg.sender, supply);
    }


    // ==================== 核心函数 ====================

    /**
     * @dev 转账函数
     * @param to 接收地址
     * @param amount 转账金额
     */
    function transfer(address to, uint256 amount) public returns (bool) {
        require(to != address(0), "Transfer to zero address");
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");

        // 更新余额
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;

        // 触发事件
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    /**
     * @dev 授权函数
     * @param spender 被授权地址
     * @param amount 授权额度
     */
    function approve(address spender, uint256 amount) public returns (bool) {
        require(spender != address(0), "Approve to zero address");

        // 设置授权额度
        allowance[msg.sender][spender] = amount;

        // 触发事件
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    /**
     * @dev 代转账函数（需要事先授权）
     * @param from 转出地址
     * @param to 接收地址
     * @param amount 转账金额
     */
    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        require(from != address(0), "Transfer from zero address");
        require(to != address(0), "Transfer to zero address");
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");

        // 更新余额
        balanceOf[from] -= amount;
        balanceOf[to] += amount;

        // 更新授权额度
        allowance[from][msg.sender] -= amount;

        // 触发事件
        emit Transfer(from, to, amount);
        return true;
    }
}
```

**检查点**：
- ✅ 我的合约实现了所有 6 个标准函数
- ✅ 我在每个操作后都触发了正确的事件
- ✅ 我添加了必要的检查（余额、授权、零地址）

**常见失败原因**：
1. 溢出问题（使用 0.8.0+ 版本可避免）
2. 没有检查零地址
3. 授权额度没有更新
4. 事件参数顺序错误

---

### 节点 3：本地编译

**输入**：.sol 源代码

**加工**：使用 Solidity 编译器

**输出**：字节码 + ABI

**方法 A：使用 Remix IDE（推荐新手）**

```
1. 打开 https://remix.ethereum.org
2. 创建新文件 MyToken.sol
3. 粘贴合约代码
4. 左侧选择 Solidity Compiler
5. 选择编译器版本 0.8.20
6. 点击 Compile MyToken.sol
```

**方法 B：使用 Hardhat（推荐正式项目）**

```bash
# 1. 初始化项目
mkdir my-token && cd my-token
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# 2. 初始化 Hardhat
npx hardhat init
# 选择 "Create a JavaScript project"

# 3. 把合约代码放到 contracts/MyToken.sol

# 4. 编译
npx hardhat compile
```

**编译输出示例**：
```
Compiled 1 Solidity file successfully

artifacts/
├── contracts/
│   └── MyToken.sol/
│       ├── MyToken.json     # 包含 ABI + 字节码
│       └── MyToken.dbg.json
```

**检查点**：
- ✅ 编译无错误
- ✅ 生成了 ABI 和字节码
- ✅ 我知道 ABI 是什么（合约的"使用说明书"）

**常见失败原因**：
1. 编译器版本不匹配
2. pragma 语句写错
3. 语法错误（缺少分号、括号不匹配）

---

### 节点 4：部署到测试网

**输入**：字节码 + ABI + 构造函数参数

**加工**：发送部署交易

**输出**：合约地址

**准备工作**：

```
1. 安装 MetaMask 浏览器插件
2. 切换到 Sepolia 测试网
3. 从水龙头获取测试 ETH
   - https://sepoliafaucet.com/
   - https://faucets.chain.link/sepolia
```

**使用 Remix 部署**：

```
1. 在 Remix 左侧选择 "Deploy & Run Transactions"
2. Environment 选择 "Injected Provider - MetaMask"
3. MetaMask 弹窗确认连接
4. 填写构造函数参数：
   - _name: "My First Token"
   - _symbol: "MFT"
   - _initialSupply: 1000000
5. 点击 "Deploy"
6. MetaMask 确认交易（需要支付 Gas）
7. 等待交易确认
```

**使用 Hardhat 部署**：

```javascript
// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const token = await MyToken.deploy("My First Token", "MFT", 1000000);
  await token.waitForDeployment();

  console.log("MyToken deployed to:", await token.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

```bash
# 部署
npx hardhat run scripts/deploy.js --network sepolia
```

**检查点**：
- ✅ 交易发送成功
- ✅ 获得合约地址
- ✅ 可以在 Sepolia Etherscan 上看到合约

**常见失败原因**：
1. 测试 ETH 不足
2. Gas 估算失败（代码有问题）
3. 网络连接问题

---

### 节点 5：验证合约代码

**输入**：合约地址 + 源代码

**加工**：上传到 Etherscan 验证

**输出**：可公开查看的源代码

```
为什么要验证？
1. 让用户信任合约（可以看到源码）
2. 可以直接在 Etherscan 上交互
3. 体现项目的透明度
```

**Remix 验证**（自动）：
- 如果使用 Remix + MetaMask 部署，通常自动验证

**Hardhat 验证**：
```bash
# 安装验证插件
npm install --save-dev @nomiclabs/hardhat-etherscan

# 在 hardhat.config.js 中配置 Etherscan API Key

# 验证命令
npx hardhat verify --network sepolia \
  <合约地址> \
  "My First Token" "MFT" 1000000
```

**检查点**：
- ✅ Etherscan 显示绿色勾（已验证）
- ✅ 可以看到 "Read Contract" 和 "Write Contract" 标签
- ✅ 源代码与部署代码匹配

---

### 节点 6：与合约交互

**输入**：合约地址 + ABI

**加工**：调用合约函数

**输出**：交易结果 / 查询结果

**在 Etherscan 上交互**：

```
Read Contract（免费，不需要交易）：
- name() → "My First Token"
- symbol() → "MFT"
- decimals() → 18
- totalSupply() → 1000000000000000000000000
- balanceOf(你的地址) → 1000000000000000000000000

Write Contract（需要签名交易）：
1. 点击 "Connect to Web3"
2. 连接 MetaMask
3. 调用 transfer(接收地址, 数量)
4. 确认交易
```

**使用 ethers.js 交互**：

```javascript
const { ethers } = require("ethers");

// 连接网络
const provider = new ethers.JsonRpcProvider("https://sepolia.infura.io/v3/YOUR_KEY");
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY", provider);

// 合约实例
const tokenAddress = "0x..."; // 你的合约地址
const tokenABI = [...]; // 从编译结果获取

const token = new ethers.Contract(tokenAddress, tokenABI, wallet);

// 查询余额
const balance = await token.balanceOf(wallet.address);
console.log("余额:", ethers.formatUnits(balance, 18));

// 转账
const tx = await token.transfer("0x接收地址...", ethers.parseUnits("100", 18));
await tx.wait();
console.log("转账成功:", tx.hash);
```

**检查点**：
- ✅ 读取函数正常返回
- ✅ 写入函数交易成功
- ✅ 状态变更符合预期

---

## 常见坑点提醒

### 坑 1：小数位数搞错

```javascript
// ❌ 错误：想转 100 个代币
token.transfer(to, 100);
// 实际只转了 0.0000000000000001 个！

// ✅ 正确：考虑 18 位小数
token.transfer(to, ethers.parseUnits("100", 18));
// 或者
token.transfer(to, 100n * 10n ** 18n);
```

### 坑 2：授权后忘记调用 transferFrom

```javascript
// 场景：用户授权 DEX 花费代币

// 第一步：用户授权
await token.approve(dexAddress, amount);

// 第二步：DEX 代转账（很多人忘了这步！）
await token.connect(dex).transferFrom(user, dex, amount);

// 只做 approve 是不会转移代币的！
```

### 坑 3：重入攻击（本例不涉及，但要注意）

```solidity
// ERC-20 本身一般不受重入攻击影响
// 但如果你的代币有回调机制（如 ERC-777），要小心

// 安全的做法：先更新状态，再调用外部合约
balanceOf[msg.sender] -= amount;  // 先更新
balanceOf[to] += amount;          // 先更新
// 然后再做其他事情
```

---

## 复盘

### 我学到的 3 件事

1. **ERC-20 是接口标准，不是代码实现**
   - 只要实现指定的函数签名，用什么方式实现都可以
   - 这就是为什么所有钱包都能识别任何 ERC-20 代币

2. **approve + transferFrom 是为第三方设计的**
   - 用户不需要直接转账给合约
   - 而是授权合约"代为操作"自己的资产
   - 这是 DeFi 的基础机制

3. **Gas 成本和安全性需要平衡**
   - 每次转账都要更新 3 个存储槽（两个余额 + 授权额度）
   - 简单的实现可能不是最优的

### 仍不确定的 3 件事

1. **代币升级怎么做？**
   - 如果发现 bug 怎么办？
   - 提示：研究代理模式（Proxy Pattern）

2. **如何防止无限授权风险？**
   - 很多 DApp 要求 MAX_UINT256 授权
   - 提示：研究 Permit2

3. **为什么不用 ERC-777？**
   - 它有回调功能，更强大
   - 提示：研究 ERC-777 的安全问题

### 下一步要查的 3 个点

1. **OpenZeppelin 的 ERC-20 实现**
   - 生产环境应该用经过审计的库
   - https://docs.openzeppelin.com/contracts/

2. **ERC-20 的扩展标准**
   - ERC-20Permit（签名授权）
   - ERC-20Burnable（可销毁）
   - ERC-20Pausable（可暂停）

3. **如何做代币经济模型**
   - 代币发行量怎么定？
   - 如何防止通胀/通缩？

---

## 完整代码下载

创建这些文件来复现整个流程：

```
my-token/
├── contracts/
│   └── MyToken.sol
├── scripts/
│   └── deploy.js
├── test/
│   └── MyToken.test.js
├── hardhat.config.js
└── package.json
```

**测试代码示例**：

```javascript
// test/MyToken.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MyToken", function () {
  let token;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    const MyToken = await ethers.getContractFactory("MyToken");
    token = await MyToken.deploy("Test Token", "TEST", 1000);
    await token.waitForDeployment();
  });

  it("Should have correct name and symbol", async function () {
    expect(await token.name()).to.equal("Test Token");
    expect(await token.symbol()).to.equal("TEST");
  });

  it("Should assign total supply to owner", async function () {
    const ownerBalance = await token.balanceOf(owner.address);
    expect(await token.totalSupply()).to.equal(ownerBalance);
  });

  it("Should transfer tokens", async function () {
    const amount = ethers.parseUnits("100", 18);
    await token.transfer(addr1.address, amount);
    expect(await token.balanceOf(addr1.address)).to.equal(amount);
  });
});
```

运行测试：
```bash
npx hardhat test
```

---

## 延伸阅读

- [智能合约基础](01-smart-contract.md)
- [Solidity 基础](02-solidity-basics.md)
- [Gas 和费用](03-gas-and-fees.md)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
