# 元数据 (Metadata)

## 一句话大白话

**元数据就是 NFT 的"说明书"——描述这个 NFT 是什么、长什么样、有什么属性。**

NFT 本身只是链上的一条记录（编号 + 所有者），元数据才是让它"有血有肉"的部分：名字、描述、图片、属性等。

---

## 它解决什么问题

### 核心痛点：链上只存"编号"，如何知道 NFT 是什么？

链上数据极其精简（因为存储贵）：
```javascript
// 链上只存这些
{
  tokenId: 1234,
  owner: "0x1234...5678"
}
```

光看这个，你知道这是什么 NFT 吗？是图片？音乐？长什么样？

### 元数据的作用

元数据补充了所有"描述性信息"：

```javascript
// 元数据（存在链外）
{
  "name": "Bored Ape #1234",
  "description": "无聊猿系列的第 1234 号",
  "image": "ipfs://QmYyy.../ape.png",
  "attributes": [
    { "trait_type": "背景", "value": "蓝色" },
    { "trait_type": "皮肤", "value": "金色" },
    { "trait_type": "眼睛", "value": "激光眼" },
    { "trait_type": "帽子", "value": "王冠" }
  ]
}
```

OpenSea、钱包、浏览器就是读取这个元数据来显示 NFT 的。

---

## 什么时候用 / 什么时候别用

### ✅ 元数据必须包含的场景

- 创建任何类型的 NFT（必须有）
- 想让 NFT 在平台上正确显示
- 需要稀有度/属性系统
- 想让搜索引擎能找到你的 NFT

### ❌ 元数据的局限

- 元数据可以被修改（如果存储方式允许）
- 元数据存储位置可能失效
- 元数据标准不是强制的，可能不兼容

---

## 它不是什么（常见混淆点）

### ❌ 元数据 ≠ 存在链上

大多数 NFT 的元数据存在链外：
- IPFS（去中心化存储）
- Arweave（永久存储）
- 中心化服务器（项目方服务器）

链上只存一个 `tokenURI`，指向元数据的位置。

### ❌ 元数据 ≠ 不可更改

根据存储方式不同：

| 存储方式 | 能否修改 | 风险 |
|---------|---------|------|
| IPFS（内容寻址） | 不能 | 如果没人保存，可能丢失 |
| Arweave | 不能 | 费用较高 |
| 中心化服务器 | 能 | 项目方可以换图、服务器可能关闭 |
| 链上存储 | 不能 | 成本极高，很少使用 |

### ❌ image 字段 ≠ 链上图片

`image` 字段只是一个 URL/链接，指向真正的图片文件。图片本身存在 IPFS 或服务器上。

---

## 最小例子

### 标准元数据格式（OpenSea 兼容）

```json
{
  "name": "我的 NFT #1",
  "description": "这是一个示例 NFT，展示元数据结构",
  "image": "ipfs://QmXxx.../image.png",
  "external_url": "https://myproject.com/nft/1",
  "animation_url": "ipfs://QmZzz.../video.mp4",
  "attributes": [
    {
      "trait_type": "颜色",
      "value": "蓝色"
    },
    {
      "trait_type": "稀有度",
      "value": "传奇"
    },
    {
      "trait_type": "力量",
      "value": 85,
      "max_value": 100,
      "display_type": "number"
    },
    {
      "trait_type": "生日",
      "value": 1704067200,
      "display_type": "date"
    }
  ]
}
```

### 各字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| name | ✅ | NFT 名称，显示在标题位置 |
| description | ✅ | NFT 描述，支持 Markdown |
| image | ✅ | 图片链接（IPFS/HTTP） |
| external_url | ❌ | 点击后跳转的外部链接 |
| animation_url | ❌ | 视频/音频/3D 模型链接 |
| attributes | ❌ | 属性数组，用于筛选和稀有度 |

### 属性类型

```json
// 文字属性
{ "trait_type": "眼睛", "value": "激光" }

// 数字属性（显示进度条）
{ "trait_type": "力量", "value": 85, "max_value": 100 }

// 日期属性
{ "trait_type": "生日", "value": 1704067200, "display_type": "date" }

// 百分比
{ "trait_type": "成功率", "value": 75, "display_type": "boost_percentage" }
```

### tokenURI 的工作方式

```
智能合约
    │
    │ tokenURI(1234) 返回
    ▼
"ipfs://QmXxx.../1234.json"
    │
    │ 解析 IPFS 获取
    ▼
{
  "name": "NFT #1234",
  "image": "ipfs://QmYyy.../1234.png",
  ...
}
    │
    │ 读取 image 字段
    ▼
显示图片
```

---

## 新手最常踩的 3 个坑

### 1. 元数据链接失效

**坑**：买了 NFT，过一阵子图片显示不出来了

**原因**：
- 存在中心化服务器，项目方关服务器了
- 存在 IPFS，但没有节点在保存（pin）这个文件

**如何避免**：
- 购买前检查 tokenURI 的存储方式
- 优先选择 IPFS + 有 pin 服务 的项目
- 高价值 NFT 可以自己 pin 到 IPFS

### 2. 不理解"图片可以改"

**坑**：以为买的 NFT 图片永远不会变

**真相**：如果元数据存在中心化服务器：
- 项目方可以换图片
- 项目方可以改属性
- 你无法阻止

**如何避免**：
- 检查 tokenURI 是 IPFS 还是 HTTP
- IPFS 链接格式：`ipfs://Qm...` 或 `https://ipfs.io/ipfs/Qm...`
- HTTP 链接格式：`https://api.project.com/...`（可能会变）

### 3. 属性理解错误

**坑**：以为属性是"官方认证"的

**真相**：
- 属性由项目方自己定义
- 稀有度是项目方自己算的
- 不同项目的属性不通用

**正确理解**：
- 属性只是元数据的一部分
- 稀有度只在单个项目内有意义
- 属性值可能被滥用（如虚标稀有度）

---

## 流程图定位

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  准备阶段  │───▶│  创作阶段  │───▶│  铸造阶段  │───▶│  交易阶段  │───▶│  持有阶段  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │               │
                     ▼               ▼
                【准备元数据】    【上传元数据】
                - 写描述        - 上传到 IPFS
                - 设置属性      - 获取 CID
                - 准备图片      - 记录到合约
```

元数据在创作和铸造阶段准备：
- **创作阶段**：确定名称、描述、属性
- **铸造阶段**：上传到存储系统，获取链接

---

## 检查 NFT 元数据的方法

### 方法 1：OpenSea 详情页

1. 打开 NFT 详情页
2. 点击"Details"
3. 可以看到 Contract Address 和 Token ID

### 方法 2：直接查询合约

1. 去 Etherscan
2. 输入合约地址
3. 找到 `tokenURI` 函数
4. 输入 Token ID 查询
5. 访问返回的 URI 查看元数据

### 方法 3：IPFS 网关

如果是 IPFS 链接 `ipfs://QmXxx...`：
- 替换成 `https://ipfs.io/ipfs/QmXxx...`
- 或使用其他 IPFS 网关

---

## 自测题

1. **概念理解**：为什么大多数 NFT 的图片不存在区块链上？

2. **风险识别**：以下哪种元数据存储方式风险最高？
   - A. ipfs://QmXxx...
   - B. ar://xxxxx（Arweave）
   - C. https://api.project.com/nft/1
   - D. data:application/json;base64,xxx（链上编码）

3. **实操题**：你在 OpenSea 看到一个 NFT，如何判断它的图片是否可能被项目方更换？

<details>
<summary>参考答案</summary>

1. 因为链上存储极其昂贵。以太坊上存 1KB 数据需要支付很高的 Gas 费，一张普通图片可能有几百 KB 到几 MB，成本太高。所以通常只在链上存一个指向图片的链接（tokenURI），图片本身存在更便宜的地方（IPFS、服务器）。

2. 答案是 C。
   - A（IPFS）：内容寻址，内容变了链接就变，相对安全
   - B（Arweave）：永久存储，最安全
   - C（HTTP）：项目方可以随时更换服务器上的内容，风险最高
   - D（链上）：存在链上，不可更改，最安全但最贵

3. 步骤：
   - 在 OpenSea 详情页找到"Details"
   - 复制 Contract Address
   - 去 Etherscan 查这个合约
   - 调用 tokenURI 函数，输入 Token ID
   - 查看返回的 URI：
     - 如果是 `ipfs://...` 开头 → 相对安全
     - 如果是 `https://...` 开头 → 可能被更换
   - 还可以查看元数据中的 image 字段是什么格式

</details>
