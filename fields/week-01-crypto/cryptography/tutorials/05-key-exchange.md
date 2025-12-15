# 密钥交换（Key Exchange）

## 一句话大白话

**两个陌生人当着所有人的面商量一个暗号，即使有人全程偷听，也猜不出这个暗号是什么。**

```
Alice 和 Bob 从未见过面
     │
     ▼
在公开信道上交换一些信息
     │
     ▼
双方都计算出相同的密钥
     │
     ▼
中间人虽然看到了交换的所有信息
却算不出这个密钥！🔐
```

## 它解决什么问题

密钥交换解决的是**密钥分发**问题：

```
困境：
- 对称加密需要共享密钥
- 但传递密钥的过程本身就不安全
- 鸡生蛋还是蛋生鸡？🐔

解决方案：
- 密钥交换协议让双方能在不安全的信道上
- 协商出一个只有他们知道的共享密钥
- 中间人即使截获所有通信也算不出密钥
```

**使用场景：**
- HTTPS/TLS握手
- VPN连接建立
- 即时通讯端对端加密
- SSH连接
- IPsec

## Diffie-Hellman 密钥交换（DH）

### 原理：颜色混合类比

想象一个魔法世界，混合颜料后无法分离：

```
┌─────────────────────────────────────────────────────────────────┐
│              Diffie-Hellman 颜色类比                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  公开信息：黄色（公共颜色）                                      │
│                                                                 │
│      Alice                           Bob                        │
│        │                              │                         │
│  私有：红色                      私有：蓝色                      │
│        │                              │                         │
│        ▼                              ▼                         │
│  黄+红=橙色 ─────── 交换 ──────→ 黄+蓝=绿色                    │
│  （公开传输）     （公开传输）                                  │
│        │                              │                         │
│  收到绿色                        收到橙色                        │
│        │                              │                         │
│        ▼                              ▼                         │
│  绿+红=棕色                      橙+蓝=棕色                      │
│        │                              │                         │
│        └──────────────────────────────┘                         │
│                      │                                          │
│                      ▼                                          │
│              双方得到相同的棕色！                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  中间人看到：黄色、橙色、绿色                                    │
│  但算不出棕色！因为不知道红色和蓝色                              │
└─────────────────────────────────────────────────────────────────┘
```

### 数学原理（简化版）

```
公开参数：
- 大质数 p（比如2048位）
- 生成元 g（比如2或5）

Alice:                          Bob:
1. 选私钥 a（随机）             1. 选私钥 b（随机）
2. 算公钥 A = g^a mod p         2. 算公钥 B = g^b mod p
3. 发送 A ────────────────→     3. 发送 B
   ←──────────────────────
4. 收到 B                       4. 收到 A
5. 算密钥 K = B^a mod p         5. 算密钥 K = A^b mod p

数学上：
K = B^a mod p = (g^b)^a mod p = g^(ab) mod p
K = A^b mod p = (g^a)^b mod p = g^(ab) mod p

两边结果相同！

攻击者知道：g, p, A, B
但要算出 K 需要知道 a 或 b
从 A = g^a mod p 求 a 就是"离散对数问题"——目前没有高效算法！
```

## ECDH：椭圆曲线版本

```
┌─────────────────────────────────────────────────────────────────┐
│                    DH vs ECDH 对比                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  经典 DH（基于大数乘法）                                         │
│  - 需要2048位以上的参数才安全                                    │
│  - 计算较慢                                                     │
│  - 密钥较大                                                     │
│                                                                 │
│  ECDH（基于椭圆曲线）                                            │
│  - 256位就能达到同等安全性                                       │
│  - 计算更快                                                     │
│  - 密钥更短                                                     │
│  - 现代协议首选！                                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  安全性等价：                                                    │
│  - ECDH 256位 ≈ DH 3072位 ≈ RSA 3072位                         │
│  - ECDH 384位 ≈ DH 7680位 ≈ RSA 7680位                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 什么时候用 / 什么时候别用

### ✅ 适合用的场景

| 场景 | 说明 |
|------|------|
| 首次安全通信 | 双方从未通信过 |
| 需要前向保密 | 即使长期密钥泄露，历史会话仍安全 |
| TLS/HTTPS | 每次连接协商新密钥 |
| 端到端加密 | 用户之间直接协商密钥 |

### ❌ 不适合用的场景

| 场景 | 原因 |
|------|------|
| 本地加密 | 不需要密钥交换，自己有密钥 |
| 已有共享密钥 | 没必要再交换 |
| 单向通信 | 需要双向交互 |

## 前向保密（Forward Secrecy）

```
┌─────────────────────────────────────────────────────────────────┐
│                    前向保密的重要性                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  【没有前向保密】                                                │
│                                                                 │
│  1. 攻击者记录所有加密流量（多年）                               │
│  2. 某天服务器私钥泄露                                          │
│  3. 攻击者用私钥解密所有历史流量！                               │
│                                                                 │
│  风险：今天的通信，十年后可能被解密                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  【有前向保密】(使用临时DH密钥)                                   │
│                                                                 │
│  1. 每次连接生成临时密钥对                                       │
│  2. 会话结束后销毁临时私钥                                       │
│  3. 即使长期私钥泄露                                            │
│  4. 历史会话密钥无法恢复，流量安全！                             │
│                                                                 │
│  TLS 1.3 强制使用前向保密 ✅                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 它不是什么（常见混淆）

| 误解 | 真相 |
|------|------|
| "DH能认证身份" | ❌ 基本DH不能！需要配合签名或证书 |
| "DH直接用来加密" | ❌ DH只是协商密钥，加密要用对称算法 |
| "密钥交换很慢" | ⚠️ ECDH其实很快，现代设备毫无压力 |

## 中间人攻击（MITM）

**裸DH的致命弱点：不能防止中间人攻击！**

```
┌─────────────────────────────────────────────────────────────────┐
│                    中间人攻击原理                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  正常情况：                                                      │
│  Alice ←────────────────────────────────→ Bob                  │
│         （直接交换DH参数）                                       │
│                                                                 │
│  中间人攻击：                                                    │
│  Alice ←──────→ Mallory ←──────→ Bob                          │
│                  （中间人）                                      │
│                                                                 │
│  1. Alice发送A给Bob                                             │
│  2. Mallory截获A，生成自己的M1发给Bob                           │
│  3. Bob发送B给Alice                                             │
│  4. Mallory截获B，生成自己的M2发给Alice                         │
│                                                                 │
│  结果：                                                          │
│  - Alice以为和Bob协商密钥K1，实际是和Mallory                     │
│  - Bob以为和Alice协商密钥K2，实际是和Mallory                     │
│  - Mallory可以解密、查看、修改、再加密转发！                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  解决方案：数字证书！                                            │
│  - 证书证明公钥属于谁                                            │
│  - DH参数需要签名验证                                            │
│  - 这就是HTTPS为什么需要证书的原因                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 最小例子

### Python 示例：ECDH密钥交换

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Alice 生成密钥对
alice_private = ec.generate_private_key(ec.SECP256R1())
alice_public = alice_private.public_key()

# Bob 生成密钥对
bob_private = ec.generate_private_key(ec.SECP256R1())
bob_public = bob_private.public_key()

# 交换公钥后，各自计算共享密钥
# Alice 用自己的私钥和Bob的公钥
alice_shared = alice_private.exchange(ec.ECDH(), bob_public)

# Bob 用自己的私钥和Alice的公钥
bob_shared = bob_private.exchange(ec.ECDH(), alice_public)

# 验证两边计算结果相同
print(f"Alice计算的共享密钥: {alice_shared.hex()[:32]}...")
print(f"Bob计算的共享密钥:   {bob_shared.hex()[:32]}...")
print(f"两边相同: {alice_shared == bob_shared}")

# 派生实际的加密密钥（使用KDF）
def derive_key(shared_key):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)

alice_key = derive_key(alice_shared)
bob_key = derive_key(bob_shared)
print(f"派生的AES密钥相同: {alice_key == bob_key}")
```

### 输出示例

```
Alice计算的共享密钥: 7a8f2b3c...
Bob计算的共享密钥:   7a8f2b3c...
两边相同: True
派生的AES密钥相同: True
```

### 使用X25519（更现代的曲线）

```python
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

# 更简洁的API，专门为密钥交换设计
alice_private = X25519PrivateKey.generate()
alice_public = alice_private.public_key()

bob_private = X25519PrivateKey.generate()
bob_public = bob_private.public_key()

# 交换
alice_shared = alice_private.exchange(bob_public)
bob_shared = bob_private.exchange(alice_public)

print(f"X25519密钥交换成功: {alice_shared == bob_shared}")
```

## 新手最常踩的 3 个坑

### 坑1：直接使用DH输出作为密钥

```
❌ 错误示范
shared_secret = dh_exchange()
aes_key = shared_secret[:32]  # 直接截取

✅ 正确做法
shared_secret = dh_exchange()
aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=random_salt,
    info=b'encryption key',
).derive(shared_secret)
```

**为什么是坑：** DH输出的原始共享密钥在数学上有一些结构，可能不够均匀分布。使用KDF（密钥派生函数）可以产生更安全的密钥。

### 坑2：忽略中间人攻击

```
❌ 错误示范
# 直接交换公钥，不验证身份
alice_pub = receive_from_network()  # 可能是攻击者的！
shared = my_private.exchange(alice_pub)

✅ 正确做法
# 公钥需要通过签名验证
alice_pub = receive_from_network()
signature = receive_signature()
if not verify(alice_pub, signature, trusted_ca_key):
    raise SecurityError("Public key not authenticated!")
shared = my_private.exchange(alice_pub)
```

**为什么是坑：** 没有认证的DH完全不能防中间人。必须配合证书或预共享的公钥。

### 坑3：重复使用临时密钥

```
❌ 错误示范
# 用同一个密钥处理所有会话
private_key = load_from_file()  # 长期使用
for session in sessions:
    shared = private_key.exchange(session.peer_public)

✅ 正确做法
# 每个会话生成新密钥（前向保密）
for session in sessions:
    ephemeral_private = ec.generate_private_key(ec.SECP256R1())
    shared = ephemeral_private.exchange(session.peer_public)
    # 会话结束后 ephemeral_private 被丢弃
```

**为什么是坑：** 使用长期密钥意味着如果私钥泄露，所有历史会话都能被解密。临时密钥提供前向保密。

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────┐
│                     安全通信流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  身份验证 → ████████████ → 对称加密通信                         │
│            │ 密钥交换 │  ← 你在这里！                           │
│            ████████████                                        │
│                 │                                               │
│                 ├── ECDH/DH 协商共享秘密                        │
│                 │                                               │
│                 ├── KDF 派生会话密钥                            │
│                 │                                               │
│                 └── 会话密钥用于对称加密                        │
│                                                                 │
│  在HTTPS中的角色：                                               │
│  1. 服务器发送证书（包含公钥）                                   │
│  2. 客户端验证证书                                              │
│  3. ECDH交换生成共享秘密  ← 密钥交换                            │
│  4. 派生对称密钥开始加密通信                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**上游依赖：** 数字证书（认证公钥归属）、非对称加密（数学基础）
**下游消费：** 对称加密（使用协商的密钥）

## 现代TLS密钥交换方式

```
TLS 1.2:
- RSA密钥交换（不推荐，无前向保密）
- DHE（前向保密）
- ECDHE（前向保密，推荐）

TLS 1.3:
- 只支持 ECDHE（强制前向保密）
- 支持的曲线：X25519, P-256, P-384

推荐：TLS 1.3 + X25519
```

## 自测题

### 题目1：Alice和Bob完成DH密钥交换后，Eve记录了所有公开传输的信息。Eve能算出共享密钥吗？

<details>
<summary>点击查看答案</summary>

不能！

Eve知道的信息：g, p, A(=g^a), B(=g^b)

要算出密钥K(=g^ab)，Eve需要知道a或b。
从A=g^a求a就是"离散对数问题"，目前没有高效算法。

这就是DH的安全性基础。

但注意：如果Eve能主动拦截和修改通信（中间人攻击），情况就不同了。所以DH必须配合证书使用。

</details>

### 题目2：为什么TLS 1.3放弃了RSA密钥交换，只用ECDHE？

<details>
<summary>点击查看答案</summary>

因为RSA密钥交换没有前向保密！

RSA密钥交换流程：
1. 客户端用服务器公钥加密"预主密钥"
2. 服务器用私钥解密

问题：
- 如果服务器私钥泄露
- 攻击者可以解密所有历史会话
- 十年前记录的流量都暴露了

ECDHE（临时DH）：
- 每次会话用新的临时密钥
- 会话结束后临时密钥销毁
- 即使服务器私钥泄露，历史会话仍安全

TLS 1.3强制前向保密，更安全。

</details>

### 题目3：如果DH参数(g,p)选得不好会怎样？

<details>
<summary>点击查看答案</summary>

会导致安全性大打折扣！

已知问题：
1. **Logjam攻击**（2015）：许多服务器使用相同的1024位DH参数，攻击者预计算后可以快速破解。

2. **小子群攻击**：如果p-1有小因子，攻击者可能推断出密钥信息。

安全要求：
- p至少2048位
- p应该是"安全素数"（p=2q+1，q也是素数）
- 使用标准参数（如RFC 7919定义的）

更好的选择：
- 使用ECDH，参数更简单
- 使用标准曲线（P-256, X25519）

</details>

---

## 总结

| 要点 | 内容 |
|------|------|
| 核心概念 | 公开交换信息，各自计算出相同的共享秘密 |
| 推荐算法 | ECDH (X25519 或 P-256) |
| 关键特性 | 前向保密、不传输密钥本身 |
| 最大局限 | 不能防中间人攻击，必须配合证书 |

**下一步：** 学习[数字证书与PKI](06-certificate-pki.md)，了解如何解决身份认证问题！
