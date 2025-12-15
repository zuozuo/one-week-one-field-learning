# ERC-721 标准

## 一句话大白话

**ERC-721 是 NFT 的"国际标准"——定义了 NFT 必须具备的基本功能，让所有平台都能认识和处理你的 NFT。**

就像 USB 接口标准让所有设备都能连接，ERC-721 让所有平台（钱包、交易所、浏览器）都能识别 NFT。

---

## 它解决什么问题

### 核心痛点：不同项目的 NFT 互不兼容

假设没有标准：
- 项目 A 的 NFT 用 `owner()` 查所有者
- 项目 B 的 NFT 用 `getOwner()` 查所有者
- 项目 C 的 NFT 用 `holderOf()` 查所有者

OpenSea 等平台要对接几千个项目，每个都不一样，怎么可能？

### ERC-721 的解决方案

统一规定：所有 NFT 合约必须实现这些函数

```solidity
// 核心函数（必须实现）
function balanceOf(address owner) → 返回某地址拥有多少 NFT
function ownerOf(uint256 tokenId) → 返回某 NFT 的所有者
function transferFrom(from, to, tokenId) → 转移 NFT
function approve(to, tokenId) → 授权别人操作你的 NFT
function safeTransferFrom(...) → 安全转移（带检查）

// 可选函数
function name() → 返回 NFT 集合名称
function symbol() → 返回代币符号
function tokenURI(tokenId) → 返回元数据链接
```

有了标准，所有平台都知道怎么跟 NFT 合约交互。

---

## 什么时候用 / 什么时候别用

### ✅ 适合用 ERC-721 的场景

- 每个 NFT 都是独一无二的（艺术品、PFP、域名）
- 不需要拆分成更小单位
- 需要兼容主流平台（OpenSea、钱包等）
- 以太坊或 EVM 兼容链上

### ❌ 不适合用 ERC-721 的场景

| 场景 | 更好的选择 |
|------|-----------|
| 游戏道具（需要大量同类物品） | ERC-1155 |
| 可分割的资产（如房产份额） | ERC-1155 或专门的分割协议 |
| 非 EVM 链 | 使用该链的原生标准 |
| 音乐/视频的限量版（1000 份相同的） | ERC-1155 更省 Gas |

---

## 它不是什么（常见混淆点）

### ❌ ERC-721 ≠ 唯一的 NFT 标准

常见 NFT 相关标准：

| 标准 | 特点 | 适用场景 |
|------|------|---------|
| ERC-721 | 每个 TokenID 独一无二 | 艺术品、PFP |
| ERC-1155 | 可以有多个相同 TokenID | 游戏道具、门票 |
| ERC-4907 | 可租借的 NFT | NFT 租赁 |
| ERC-5192 | 灵魂绑定（不可转让） | 身份凭证、成就 |

### ❌ ERC-721 ≠ 代码实现

ERC-721 是接口规范，不是代码实现：
- 规定了"必须能做什么"
- 没规定"怎么实现"
- 不同实现可能有不同的额外功能

### ❌ 符合 ERC-721 ≠ 安全

合约可以符合 ERC-721 标准但仍然有：
- 其他安全漏洞
- 恶意额外功能
- 中心化控制权限

---

## 最小例子

### ERC-721 核心接口

```solidity
interface IERC721 {
    // 事件
    event Transfer(address from, address to, uint256 tokenId);
    event Approval(address owner, address approved, uint256 tokenId);
    event ApprovalForAll(address owner, address operator, bool approved);

    // 查询函数
    function balanceOf(address owner) external view returns (uint256);
    function ownerOf(uint256 tokenId) external view returns (address);

    // 转账函数
    function transferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId) external;

    // 授权函数
    function approve(address to, uint256 tokenId) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function setApprovalForAll(address operator, bool approved) external;
    function isApprovedForAll(address owner, address operator) external view returns (bool);
}
```

### 一个简化的 ERC-721 实现

```solidity
contract SimpleNFT is IERC721 {
    // 存储：TokenID → 所有者
    mapping(uint256 => address) private _owners;
    // 存储：地址 → 拥有数量
    mapping(address => uint256) private _balances;
    // 存储：TokenID → 被授权地址
    mapping(uint256 => address) private _tokenApprovals;

    function balanceOf(address owner) public view returns (uint256) {
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        return _owners[tokenId];
    }

    function transferFrom(address from, address to, uint256 tokenId) public {
        require(ownerOf(tokenId) == from, "不是所有者");
        require(msg.sender == from || getApproved(tokenId) == msg.sender, "无权限");

        _balances[from] -= 1;
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(from, to, tokenId);
    }

    // ... 其他函数
}
```

### ERC-721 vs ERC-1155 对比

```
ERC-721（每个独一无二）：
TokenID 1 → 所有者 A（无聊猿 #1）
TokenID 2 → 所有者 B（无聊猿 #2）
TokenID 3 → 所有者 C（无聊猿 #3）

ERC-1155（可以有多个相同的）：
TokenID 1（剑） → 所有者 A 有 3 把，所有者 B 有 5 把
TokenID 2（盾） → 所有者 A 有 1 个，所有者 C 有 2 个
```

---

## 新手最常踩的 3 个坑

### 1. 不理解 approve 的风险

**坑**：随便授权（approve）给不信任的合约

**风险**：
- approve 后，被授权方可以转走你的 NFT
- 恶意合约可能立即转走
- 即使当时没转，未来也可能转

**正确做法**：
- 只授权给可信的合约（知名交易所等）
- 定期检查和撤销不用的授权
- 使用 Revoke.cash 等工具管理授权

### 2. 混淆 transferFrom 和 safeTransferFrom

**坑**：用 `transferFrom` 发给合约地址，NFT "丢了"

**解释**：
- `transferFrom`：直接转，不检查接收方
- `safeTransferFrom`：转之前检查接收方是否能处理 NFT

如果接收方是个普通合约（没有处理 NFT 的能力），NFT 就被"锁死"在那个合约里了。

**正确做法**：
- 优先使用 `safeTransferFrom`
- 确认接收地址能处理 NFT（是钱包或支持 NFT 的合约）

### 3. 以为所有 NFT 都是 ERC-721

**坑**：按 ERC-721 的方式交互一个 ERC-1155 的 NFT，失败

**如何区分**：
- 查看合约实现了哪些接口
- 看 OpenSea 显示的 Token Standard
- ERC-721: `ownerOf(tokenId)` 返回单个地址
- ERC-1155: `balanceOf(account, tokenId)` 返回数量

---

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  准备阶段  │───▶│  创作阶段  │───▶│  铸造阶段  │───▶│  交易阶段  │───▶│  持有阶段  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                     │               │
                                     ▼               ▼
                              【ERC-721 合约】  【ERC-721 函数】
                              - mint() 铸造    - transferFrom 转账
                              - 分配 tokenId   - approve 授权
                              - 记录 owner     - 平台调用标准接口
```

ERC-721 定义了 NFT 合约的核心行为：
- **铸造阶段**：调用 mint 函数（非标准，各项目自定义）
- **交易阶段**：调用 transferFrom/approve 等标准函数
- **平台交互**：OpenSea 等通过标准接口读取和操作 NFT

---

## 如何验证合约是否符合 ERC-721

### 方法 1：查看 Etherscan

1. 打开合约页面
2. 点击 "Contract" → "Read Contract"
3. 看是否有 `balanceOf`, `ownerOf`, `tokenURI` 等函数

### 方法 2：检查接口支持

```solidity
// ERC-165 接口检测
// ERC-721 的接口 ID 是 0x80ac58cd

function supportsInterface(bytes4 interfaceId) returns (bool);

// 如果返回 true，说明支持 ERC-721
contract.supportsInterface(0x80ac58cd)
```

### 方法 3：查看源码

- 看合约是否继承了 `ERC721` 或 `IERC721`
- 是否实现了所有必须的函数

---

## 自测题

1. **概念理解**：为什么需要 ERC-721 这样的标准？没有标准会怎样？

2. **功能区分**：以下哪个函数是 ERC-721 标准的一部分？
   - A. `mint(address to, uint256 tokenId)`
   - B. `ownerOf(uint256 tokenId)`
   - C. `burn(uint256 tokenId)`
   - D. `setBaseURI(string memory uri)`

3. **安全意识**：你想在 OpenSea 上卖一个 NFT，需要 approve 给 OpenSea 的合约。approve 后会发生什么？有什么风险？

<details>
<summary>参考答案</summary>

1. 标准的作用是让所有 NFT 合约有统一的接口，这样：
   - 钱包知道如何显示 NFT
   - 交易所知道如何交易 NFT
   - 浏览器知道如何查询 NFT

   如果没有标准，每个项目的 NFT 合约都不一样，平台要对接几千个项目会变得不可能，NFT 生态无法形成。

2. 答案是 B。
   - A：mint 不是 ERC-721 标准的一部分，各项目自己定义
   - B：`ownerOf` 是 ERC-721 必须实现的标准函数 ✓
   - C：burn 不是标准的一部分
   - D：setBaseURI 是很多项目添加的扩展功能，不是标准

   ERC-721 核心函数：balanceOf, ownerOf, transferFrom, approve, safeTransferFrom, getApproved, setApprovalForAll, isApprovedForAll

3. approve 后：
   - OpenSea 的合约获得了转移这个 NFT 的权限
   - 当有人购买时，OpenSea 合约代你执行转移

   风险：
   - 如果 approve 给的是假冒的 OpenSea 合约，NFT 可能被立即转走
   - 即使是真的 OpenSea，理论上他们有权限转你的 NFT（虽然正规平台不会滥用）
   - 建议：只在需要时授权，交易完成后考虑撤销授权

</details>
