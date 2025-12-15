# DeFi 基础

## 一句话大白话

**DeFi（去中心化金融）就是用代码重建银行、交易所、借贷公司——没有CEO、没有营业时间、没有KYC，7×24小时自动运行。**

传统金融需要你信任银行不会倒闭、不会冻结你的账户。DeFi 让代码成为「银行」，规则公开透明，任何人都可以审计。

---

## 它解决什么问题

### 核心问题：如何在没有中间人的情况下实现金融服务？

传统金融的问题：
- **准入门槛**：很多人无法获得银行服务
- **效率低下**：跨境转账需要数天，手续费高
- **不透明**：你不知道银行怎么用你的钱
- **审查风险**：账户可能被冻结
- **营业时间**：银行周末不上班

**DeFi 的解决方案**：
- 任何人都可以使用（只需一个钱包）
- 24/7 运行
- 规则完全透明（智能合约公开）
- 无法单方面冻结资产
- 即时结算

### DeFi 的核心组件

```
传统金融                    DeFi 对应
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
银行（存款/借贷）     →     借贷协议（Aave, Compound）
交易所               →     DEX（Uniswap, Curve）
期货/期权            →     衍生品协议（dYdX, GMX）
保险公司             →     保险协议（Nexus Mutual）
资产管理             →     收益聚合器（Yearn）
稳定币               →     算法稳定币（DAI）
```

---

## 什么时候用 / 什么时候别用

### DeFi 的优势场景

| 场景 | 为什么 DeFi 更好 |
|------|------------------|
| 跨境转账 | 几分钟完成，手续费低 |
| 24/7 交易 | 随时可用，不受营业时间限制 |
| 无需许可 | 不需要 KYC，不会被拒绝服务 |
| 透明度 | 可以审计所有资金流向 |
| 可组合性 | 不同协议可以像乐高一样组合 |

### DeFi 的局限

| 局限 | 说明 |
|------|------|
| 智能合约风险 | 代码可能有漏洞 |
| Gas 费用 | 网络拥堵时成本高 |
| 用户体验 | 比传统应用复杂 |
| 监管不确定 | 法律地位不明确 |
| 链下资产 | 只能处理链上原生资产 |

---

## 它不是什么

### 常见误解

| 误解 | 真相 |
|------|------|
| 「DeFi 是无风险的」 | 智能合约漏洞、清算风险、预言机攻击都是真实威胁 |
| 「DeFi 年化收益 100%+」 | 高收益 = 高风险，可能是庞氏或即将归零 |
| 「DeFi 完全匿名」 | 链上交易完全公开，可以被追踪 |
| 「DeFi 不需要信任」 | 仍需信任代码正确、预言机诚实、治理不作恶 |
| 「DeFi 可以替代所有金融」 | 链下资产、法币、监管合规等问题仍需传统金融 |

---

## 最小例子

### DeFi 核心场景详解

```
┌─────────────────────────────────────────────────────────────────────┐
│  场景 1: DEX（去中心化交易所）                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  传统交易所（订单簿模式）：                                          │
│  ├─ 买家出价 $1999，卖家要价 $2000                                   │
│  ├─ 需要撮合引擎                                                    │
│  └─ 需要做市商提供流动性                                            │
│                                                                     │
│  DEX（AMM 模式，如 Uniswap）：                                       │
│  ├─ 使用数学公式：x × y = k                                         │
│  ├─ 流动性由用户提供（LP）                                           │
│  └─ 价格由供需自动调整                                               │
│                                                                     │
│  示例：ETH/USDC 交易对                                               │
│  ┌─────────────────────────────────────────┐                        │
│  │  池子状态：                              │                        │
│  │  ETH: 100 个                            │                        │
│  │  USDC: 200,000 个                       │                        │
│  │  k = 100 × 200,000 = 20,000,000        │                        │
│  │  价格 = 200,000 / 100 = 2000 USDC/ETH  │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
│  用户用 2000 USDC 买 ETH：                                          │
│  新 USDC = 202,000                                                  │
│  新 ETH = 20,000,000 / 202,000 ≈ 99.01                             │
│  用户获得 ≈ 0.99 ETH（有滑点）                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│  场景 2: 借贷协议（如 Aave）                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  存款人                        借款人                               │
│  ┌──────────┐                ┌──────────┐                          │
│  │ 存入 ETH │                │ 存入抵押品│                          │
│  │ 获得利息 │                │ 借出资产  │                          │
│  └──────────┘                └──────────┘                          │
│       │                           │                                 │
│       v                           v                                 │
│  ┌─────────────────────────────────────────┐                        │
│  │           借贷池（智能合约）              │                        │
│  │  ├─ 管理存款和借款                       │                        │
│  │  ├─ 根据供需计算利率                     │                        │
│  │  └─ 自动清算低于阈值的抵押品              │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
│  超额抵押示例：                                                       │
│  ┌─────────────────────────────────────────┐                        │
│  │  抵押: 2 ETH（价值 $4000）               │                        │
│  │  借出: 2000 USDC                        │                        │
│  │  抵押率: 200%                           │                        │
│  │  清算线: 150%                           │                        │
│  │                                         │                        │
│  │  如果 ETH 跌到 $1500:                   │                        │
│  │  抵押价值 = $3000                       │                        │
│  │  抵押率 = 150% ← 触发清算！             │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│  场景 3: 稳定币（如 DAI）                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  问题：加密货币波动太大，需要稳定的价值存储                           │
│                                                                     │
│  解决方案：                                                          │
│  ┌────────────────────┬─────────────────────────────────────────┐   │
│  │ 类型               │ 例子           │ 锚定方式               │   │
│  ├────────────────────┼────────────────┼────────────────────────┤   │
│  │ 法币抵押           │ USDC, USDT     │ 1:1 美元储备           │   │
│  │ 加密抵押           │ DAI            │ 超额加密资产抵押        │   │
│  │ 算法稳定           │ (多数已失败)    │ 供需算法调节           │   │
│  └────────────────────┴────────────────┴────────────────────────┘   │
│                                                                     │
│  DAI 的工作原理：                                                    │
│  ┌─────────────────────────────────────────┐                        │
│  │  1. 用户存入 ETH 作为抵押                │                        │
│  │  2. 系统铸造 DAI（不超过抵押价值的 ~67%） │                        │
│  │  3. 用户还清 DAI + 利息                  │                        │
│  │  4. 取回抵押品                           │                        │
│  │                                         │                        │
│  │  如果抵押品价值下跌 → 自动清算           │                        │
│  │  价格稳定机制：套利者维持价格锚定         │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### JavaScript 示例：与 Uniswap 交互

```javascript
const { ethers } = require('ethers');

// Uniswap V2 Router 地址（以太坊主网）
const UNISWAP_ROUTER = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D';

// 简化的 Router ABI
const routerAbi = [
    'function getAmountsOut(uint amountIn, address[] path) view returns (uint[] amounts)',
    'function swapExactETHForTokens(uint amountOutMin, address[] path, address to, uint deadline) payable returns (uint[] amounts)',
];

const WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2';
const USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48';

async function checkSwapPrice(provider) {
    const router = new ethers.Contract(UNISWAP_ROUTER, routerAbi, provider);

    // 查询用 1 ETH 能换多少 USDC
    const amountIn = ethers.parseEther('1');
    const path = [WETH, USDC];

    const amounts = await router.getAmountsOut(amountIn, path);
    const usdcAmount = ethers.formatUnits(amounts[1], 6); // USDC 6位小数

    console.log(`1 ETH ≈ ${usdcAmount} USDC`);
}

async function swapETHForUSDC(wallet, ethAmount, minUsdcOut) {
    const router = new ethers.Contract(UNISWAP_ROUTER, routerAbi, wallet);

    const path = [WETH, USDC];
    const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20分钟后过期

    const tx = await router.swapExactETHForTokens(
        minUsdcOut,   // 最少获得的 USDC（滑点保护）
        path,
        wallet.address,
        deadline,
        { value: ethAmount }
    );

    console.log('交易哈希:', tx.hash);
    await tx.wait();
    console.log('交换完成！');
}
```

### JavaScript 示例：与 Aave 交互

```javascript
const { ethers } = require('ethers');

// Aave V3 Pool 地址（以太坊主网）
const AAVE_POOL = '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2';

const poolAbi = [
    'function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)',
    'function withdraw(address asset, uint256 amount, address to) returns (uint256)',
    'function borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)',
    'function repay(address asset, uint256 amount, uint256 interestRateMode, address onBehalfOf) returns (uint256)',
    'function getUserAccountData(address user) view returns (uint256 totalCollateralBase, uint256 totalDebtBase, uint256 availableBorrowsBase, uint256 currentLiquidationThreshold, uint256 ltv, uint256 healthFactor)',
];

async function checkAccountHealth(provider, userAddress) {
    const pool = new ethers.Contract(AAVE_POOL, poolAbi, provider);

    const data = await pool.getUserAccountData(userAddress);

    console.log('账户健康数据:');
    console.log('总抵押品 (USD):', ethers.formatUnits(data.totalCollateralBase, 8));
    console.log('总债务 (USD):', ethers.formatUnits(data.totalDebtBase, 8));
    console.log('可借额度 (USD):', ethers.formatUnits(data.availableBorrowsBase, 8));
    console.log('健康因子:', ethers.formatUnits(data.healthFactor, 18));

    // 健康因子 < 1 会被清算！
    if (data.healthFactor < ethers.parseEther('1')) {
        console.log('警告：账户即将被清算！');
    }
}

async function supplyToAave(wallet, tokenAddress, amount) {
    // 先 approve
    const token = new ethers.Contract(tokenAddress, [
        'function approve(address spender, uint256 amount) returns (bool)'
    ], wallet);
    await token.approve(AAVE_POOL, amount);

    // 再 supply
    const pool = new ethers.Contract(AAVE_POOL, poolAbi, wallet);
    const tx = await pool.supply(
        tokenAddress,
        amount,
        wallet.address,
        0  // referralCode
    );

    await tx.wait();
    console.log('存款成功！');
}
```

---

## 新手最常踩的 3 个坑

### 坑 1：不理解无常损失（Impermanent Loss）

**什么是无常损失**：
```
你提供流动性：存入 1 ETH + 2000 USDC
（假设当时 1 ETH = 2000 USDC）

如果 ETH 涨到 4000 USDC：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
如果只是持有：
  1 ETH = $4000
  2000 USDC = $2000
  总计 = $6000

作为 LP：
  由于 AMM 的 x*y=k，你的份额变成：
  约 0.707 ETH + 2828 USDC
  总计 ≈ $5656

无常损失 = $6000 - $5656 = $344 (约 5.7%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

价格变化越大，无常损失越大：
价格变化 2x → 无常损失 5.7%
价格变化 3x → 无常损失 13.4%
价格变化 5x → 无常损失 25.5%
```

**建议**：
- 选择低波动性的交易对（如稳定币对）
- 确保手续费收入 > 无常损失
- 了解风险再参与

### 坑 2：被清算（Liquidation）

**清算是怎么发生的**：
```
初始状态：
┌─────────────────────────────────────────┐
│  抵押: 10 ETH @ $2000 = $20,000         │
│  借出: $10,000 USDC                     │
│  抵押率: 200%                           │
│  清算线: 150%                           │
└─────────────────────────────────────────┘

ETH 价格下跌：
┌─────────────────────────────────────────┐
│  ETH 跌到 $1500                         │
│  抵押价值: 10 × $1500 = $15,000         │
│  抵押率: 150% ← 触发清算线！            │
│                                         │
│  清算过程:                              │
│  1. 清算人替你还一部分债务              │
│  2. 清算人获得你的抵押品（打折）         │
│  3. 你损失部分抵押品 + 清算罚金         │
└─────────────────────────────────────────┘

损失：
- 清算罚金: 通常 5-15%
- 在最坏时机被迫卖出
```

**如何避免**：
- 保持较高的抵押率（如 300%）
- 设置价格警报
- 使用自动去杠杆工具（如 DeFi Saver）
- 不要借满额度

### 坑 3：授权（Approve）风险

**问题**：
```
使用 DeFi 时经常需要授权代币：
"Allow Uniswap to spend your USDC"

风险：
1. 授权了恶意合约 → 代币被盗
2. 授权了无限额度 → 即使不用了也有风险
3. 授权钓鱼 → 签名看似无害但实际授权了转账
```

**安全实践**：
```javascript
// 坏：授权无限额度
await token.approve(spender, ethers.MaxUint256);

// 好：只授权需要的额度
await token.approve(spender, exactAmount);

// 更好：用完后撤销授权
await token.approve(spender, 0);
```

**定期检查授权**：
- 使用 Revoke.cash 检查和撤销授权
- 使用单独的钱包进行 DeFi 操作
- 对不熟悉的协议谨慎授权

---

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DeFi 生态系统                                    │
└─────────────────────────────────────────────────────────────────────┘

底层基础设施
┌─────────────────────────────────────────────────────────────────────┐
│  以太坊区块链                                                        │
│  ├─ 账户系统（之前学的）                                            │
│  ├─ 智能合约（之前学的）                                            │
│  └─ 交易和签名（之前学的）                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              v
核心 DeFi 协议（你在这里学习）
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│  │ 稳定币  │  │  DEX    │  │  借贷   │  │  衍生品 │               │
│  │(DAI...)│  │(Uniswap)│  │ (Aave) │  │ (dYdX) │               │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘               │
│       │            │            │            │                     │
│       └────────────┴────────────┴────────────┘                     │
│                         │                                          │
│                         v                                          │
│               可组合性（Money Lego）                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              v
聚合层和应用层
┌─────────────────────────────────────────────────────────────────────┐
│  收益聚合器（Yearn）、交易聚合器（1inch）、                          │
│  杠杆协议、保险协议、DAO 财库...                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 自测题

### 基础理解

1. **什么是 AMM（自动做市商）？和传统订单簿有什么区别？**

<details>
<summary>参考答案</summary>

AMM = Automated Market Maker（自动做市商）

传统订单簿：
- 买家挂买单，卖家挂卖单
- 价格匹配时成交
- 需要足够的买卖双方

AMM（如 Uniswap）：
- 使用数学公式定价：x × y = k
- 流动性由 LP（流动性提供者）提供
- 任何时候都可以交易（只要池子有流动性）
- 价格随供需自动调整

优缺点：
| 特性 | AMM | 订单簿 |
|------|-----|-------|
| 流动性 | LP 提供 | 做市商提供 |
| 定价 | 数学公式 | 市场供需 |
| 滑点 | 大额交易滑点大 | 取决于深度 |
| 去中心化 | 完全去中心化 | 可能中心化 |
</details>

2. **为什么 DeFi 借贷需要「超额抵押」？不能像银行一样信用贷款吗？**

<details>
<summary>参考答案</summary>

需要超额抵押的原因：

1. **无法验证身份**
   - 区块链是假名的
   - 无法知道借款人的信用历史
   - 无法追讨违约

2. **无法强制执行**
   - 没有法院、没有执行机制
   - 借款人可以直接消失
   - 唯一的保障是抵押品

3. **波动性**
   - 加密资产价格波动大
   - 需要缓冲空间应对价格下跌
   - 所以要求 150%-200% 抵押率

为什么不能信用贷款：
- 传统信用贷款依赖：
  - 身份验证
  - 信用评分
  - 法律强制执行
  - 社会信任
- 这些在去中心化环境中都不存在

未来可能的方向：
- 链上信用积累（多次还款记录）
- 社交图谱信用
- 与链下身份关联
</details>

3. **什么是「可组合性」？为什么说 DeFi 是 Money Lego？**

<details>
<summary>参考答案</summary>

可组合性 = DeFi 协议可以像乐高积木一样自由组合

例子：
```
单独使用：
- Aave：存款赚利息
- Uniswap：交换代币
- Yearn：收益优化

组合使用：
1. 在 Aave 存入 ETH
2. 借出 DAI
3. 用 DAI 在 Uniswap 提供流动性
4. LP 代币存入 Yearn 自动复利
5. 用 Yearn 代币再抵押借款...
```

这种组合创造了：
- 杠杆
- 收益策略
- 新的金融产品

为什么可能：
- 统一的代币标准（ERC-20）
- 合约可以调用合约
- 无需许可（不用申请接入）

风险：
- 组合越复杂，风险越高
- 一个环节出问题，整个策略可能崩溃
- 「DeFi 套娃」可能放大风险
</details>

### 进阶思考

4. **如果你要评估一个新的 DeFi 协议是否安全，你会关注哪些方面？**

<details>
<summary>参考答案</summary>

安全评估清单：

1. **智能合约审计**
   - 是否有知名审计公司审计？
   - 审计报告是否公开？
   - 发现的问题是否已修复？

2. **代码开源**
   - 是否完全开源？
   - 是否可以验证部署的代码和开源代码一致？

3. **团队背景**
   - 团队是否公开？
   - 是否有不良历史？
   - 是否有逃跑风险？

4. **TVL 和运行时间**
   - TVL（总锁仓量）是否稳定增长？
   - 运行了多长时间？（林迪效应）

5. **治理和权限**
   - 是否有管理员后门？
   - 多签还是单签？
   - 治理代币分布是否去中心化？

6. **经济模型**
   - 收益来源是什么？（真实收益 vs 代币通胀）
   - 是否可持续？
   - 是否有庞氏特征？

7. **依赖风险**
   - 依赖哪些预言机？
   - 依赖哪些其他协议？
   - 单点故障风险？

红旗警告：
- 无审计
- 团队匿名且无历史
- 年化收益超高且来源不明
- 合约有无限铸币权
- 代码不开源
</details>
