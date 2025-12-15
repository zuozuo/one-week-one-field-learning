# 非对称加密（Asymmetric Encryption）

## 一句话大白话

**有两把不同的钥匙：公钥像邮箱口（谁都能往里塞信），私钥像邮箱钥匙（只有你能取信）。**

```
公钥加密 → 私钥解密（加密用途）
私钥签名 → 公钥验证（签名用途）

关键：公钥可以公开，私钥必须保密！
```

## 它解决什么问题

非对称加密解决的是**密钥分发**问题：两个从未见面的人，如何在不安全的网络上协商出一个安全的密钥？

**对称加密的困境：**
```
Alice想和Bob安全通信
        ↓
需要先共享一个密钥
        ↓
但传递密钥的过程不安全
        ↓
鸡生蛋还是蛋生鸡？🐔🥚
```

**非对称加密的解决方案：**
```
Bob公开自己的公钥（全世界都能看到）
        ↓
Alice用Bob的公钥加密消息
        ↓
只有Bob的私钥能解密
        ↓
即使中间人截获，也看不懂！✅
```

**使用场景：**
- HTTPS握手时交换密钥
- 电子邮件加密（PGP/GPG）
- 数字签名（证明身份）
- SSH免密登录
- 区块链钱包

## 什么时候用 / 什么时候别用

### ✅ 适合用的场景

| 场景 | 说明 |
|------|------|
| 首次通信 | 双方不需要预先共享密钥 |
| 数字签名 | 证明消息确实是某人发送的 |
| 密钥交换 | 安全地协商对称加密的密钥 |
| 身份认证 | 证明"我是我" |

### ❌ 不适合用的场景

| 场景 | 原因 |
|------|------|
| 加密大量数据 | 太慢了！比对称加密慢1000倍 |
| 实时通信加密 | 性能不够 |
| 加密存储 | 没必要，对称加密更合适 |

**实际做法：用非对称加密交换密钥，用对称加密传输数据。**

## 它不是什么（常见混淆）

| 误解 | 真相 |
|------|------|
| "公钥加密，公钥解密" | ❌ 公钥加密必须私钥解密 |
| "非对称加密比对称加密更安全" | ❌ 安全性取决于密钥长度和使用方式，不能简单比较 |
| "RSA和ECC是一回事" | ❌ 数学原理完全不同，ECC用更短的密钥达到同等安全性 |
| "私钥可以推算出公钥" | ✅ 这是对的！但公钥推不出私钥 |

## 数学原理（简化版）

### RSA的核心思想

RSA基于一个数学事实：**大数分解非常困难**。

```
选两个大质数 p 和 q
计算 n = p × q  （这个n有几百位数字）

给你 n，让你算出 p 和 q → 目前没有高效算法！

公钥 = (n, e)  可以公开
私钥 = (n, d)  必须保密

加密：密文 = 明文^e mod n
解密：明文 = 密文^d mod n
```

**类比：**
想象一个特殊的保险箱：
- 任何人都能把东西放进去（用公钥）
- 只有你能打开取出来（用私钥）
- 保险箱的设计是公开的，但没人能仿造你的私钥

### ECC的核心思想

ECC基于**椭圆曲线离散对数问题**：

```
在椭圆曲线上：
已知点G和点Q=kG，求k → 非常困难！

用256位ECC ≈ 3072位RSA 的安全性
```

**优势：密钥更短，计算更快，特别适合移动设备和嵌入式系统。**

## 主要算法对比

| 算法 | 基于问题 | 密钥长度 | 状态 | 典型用途 |
|------|----------|----------|------|----------|
| RSA-2048 | 大数分解 | 2048位 | ✅ 可用 | 传统场景，兼容性好 |
| RSA-4096 | 大数分解 | 4096位 | ✅ 推荐 | 长期安全需求 |
| ECDSA | 椭圆曲线 | 256位 | ✅ 推荐 | 数字签名（比特币用这个） |
| ECDH | 椭圆曲线 | 256位 | ✅ 推荐 | 密钥交换 |
| Ed25519 | 椭圆曲线 | 256位 | ✅ 强烈推荐 | 签名，速度快，安全性高 |

**选择建议：**
- 新项目优先用 ECC（Ed25519/X25519）
- 需要兼容老系统用 RSA-2048+
- 不要用 RSA-1024（已不安全）

## 最小例子

### Python 示例：RSA加密解密

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# 1. 生成密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# 2. 用公钥加密
message = b"Hello, RSA!"
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print(f"密文长度: {len(ciphertext)} 字节")  # 256字节（2048位）

# 3. 用私钥解密
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
print(f"解密结果: {plaintext}")
```

### Python 示例：数字签名

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

# 1. 生成ECC密钥对
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# 2. 用私钥签名
message = b"This message is from Alice"
signature = private_key.sign(
    message,
    ec.ECDSA(hashes.SHA256())
)
print(f"签名: {signature.hex()[:64]}...")

# 3. 用公钥验证
try:
    public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    print("签名验证成功！✅")
except:
    print("签名验证失败！❌")

# 4. 篡改消息试试
try:
    public_key.verify(signature, b"Tampered message", ec.ECDSA(hashes.SHA256()))
except:
    print("篡改后验证失败！这是预期的 ✅")
```

### 命令行示例（OpenSSL）

```bash
# 生成RSA私钥
openssl genrsa -out private.pem 2048

# 从私钥导出公钥
openssl rsa -in private.pem -pubout -out public.pem

# 用公钥加密
echo "Hello World" | openssl rsautl -encrypt -pubin -inkey public.pem -out encrypted.bin

# 用私钥解密
openssl rsautl -decrypt -inkey private.pem -in encrypted.bin
```

## 新手最常踩的 3 个坑

### 坑1：用RSA加密大数据

```
❌ 错误示范
# RSA-2048 最多加密 245 字节
huge_data = b"x" * 1000
ciphertext = public_key.encrypt(huge_data, padding)  # 报错！

✅ 正确做法
# 用RSA加密一个随机的AES密钥
# 用AES加密实际数据
aes_key = os.urandom(32)
encrypted_key = rsa_encrypt(aes_key)
encrypted_data = aes_encrypt(huge_data, aes_key)
```

**为什么是坑：** RSA加密的数据长度不能超过密钥长度减去填充。2048位RSA最多加密245字节（使用OAEP填充时）。

### 坑2：不用填充（Padding）

```
❌ 错误示范（教科书式RSA）
ciphertext = pow(message, e, n)  # 裸RSA，严重不安全！

✅ 正确做法
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(...)  # 必须使用标准填充
)
```

**为什么是坑：**
- 不用填充的RSA有很多已知攻击
- 相同明文会产生相同密文
- 存在数学结构可被利用

### 坑3：混淆加密和签名

```
❌ 概念混淆
"用公钥签名" 或 "用私钥加密消息内容"

✅ 正确理解
加密：公钥加密 → 私钥解密（保密）
签名：私钥签名 → 公钥验证（认证）
```

| 操作 | 用什么密钥 | 目的 |
|------|-----------|------|
| 加密 | 公钥 | 只有私钥持有者能解密 |
| 解密 | 私钥 | 获取原始内容 |
| 签名 | 私钥 | 证明是我发的 |
| 验签 | 公钥 | 确认确实是他发的 |

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────┐
│                     安全通信流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ████████████        ████████████                               │
│  │ 身份验证 │   →   │ 密钥交换 │   →   对称加密通信             │
│  ████████████        ████████████                               │
│       ↑                   ↑                                     │
│       │                   │                                     │
│  数字签名              非对称加密                                │
│  (私钥签名)           (公钥加密密钥种子)                         │
│                                                                 │
│  ← 你在这里！非对称加密用于握手阶段                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**上游依赖：** 无（起点）
**下游消费：** 对称加密（提供会话密钥）、数字签名（提供密钥对）

## 公钥与私钥的关系图解

```
                    数学关系
    ┌─────────────────────────────────────┐
    │                                     │
    │   私钥 ──────────→ 公钥             │
    │         (可以推导)                  │
    │                                     │
    │   公钥 ──────╳───→ 私钥             │
    │         (不可逆！)                  │
    │                                     │
    └─────────────────────────────────────┘

                    使用方式
    ┌─────────────────────────────────────┐
    │                                     │
    │  加密场景：                          │
    │  发送方 ─[公钥加密]─→ 密文           │
    │  接收方 ─[私钥解密]─→ 明文           │
    │                                     │
    │  签名场景：                          │
    │  签名方 ─[私钥签名]─→ 签名值         │
    │  验证方 ─[公钥验证]─→ 真/假          │
    │                                     │
    └─────────────────────────────────────┘
```

## 自测题

### 题目1：为什么不能只用非对称加密进行所有通信？

<details>
<summary>点击查看答案</summary>

因为非对称加密太慢了：
- RSA加密比AES慢约1000倍
- 加密大文件会非常耗时
- 移动设备上更明显

实际做法是"混合加密"：
1. 用非对称加密交换一个随机密钥（几百字节）
2. 用对称加密传输实际数据（可以是GB级别）

</details>

### 题目2：Alice想给Bob发送加密消息，她应该用谁的什么密钥？

<details>
<summary>点击查看答案</summary>

Alice应该用 **Bob的公钥** 加密。

逻辑链：
1. Alice想让只有Bob能看到消息
2. 所以需要用只有Bob能解开的方式加密
3. 只有Bob有他的私钥
4. 所以用Bob的公钥加密

如果Alice用自己的私钥"加密"，那叫签名，任何人用Alice的公钥都能"解密"（验证），就不保密了。

</details>

### 题目3：RSA-1024和ECC-256哪个更安全？

<details>
<summary>点击查看答案</summary>

**ECC-256更安全！**

安全性等级对比：
- RSA-1024 ≈ 80位安全性（已不安全，可被破解）
- ECC-256 ≈ 128位安全性（目前安全）
- RSA-2048 ≈ 112位安全性
- RSA-3072 ≈ 128位安全性

这就是为什么现代系统越来越多使用ECC：更短的密钥，同等或更好的安全性，更快的速度。

</details>

---

## 总结

| 要点 | 内容 |
|------|------|
| 核心概念 | 公钥加密私钥解；私钥签名公钥验 |
| 解决问题 | 密钥分发问题 |
| 推荐算法 | ECC (Ed25519/X25519) 或 RSA-2048+ |
| 关键原则 | 私钥绝不能泄露；加密用公钥，签名用私钥 |
| 最大局限 | 速度慢，不适合加密大量数据 |

**下一步：** 学习[哈希函数](03-hash-function.md)，理解数字签名的基础！
