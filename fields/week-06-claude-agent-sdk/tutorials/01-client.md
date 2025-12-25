# Anthropic Client：连接 Claude 的"遥控器"

## 一句话定义

**Anthropic Client 就是你和 Claude API 之间的"遥控器"**——你按按钮（调用方法），它帮你和 Claude 通信。

---

## 生活类比

想象你要点外卖：
- **你**：想吃披萨的用户
- **外卖 App**：Anthropic Client
- **餐厅**：Claude API

你不需要亲自跑到餐厅，只需要在 App 里下单。Client 就是那个帮你传递信息的"中间人"。

---

## 为什么需要它？

Claude 是运行在 Anthropic 服务器上的 AI。你的代码想和它对话，需要：
1. 证明你有权限使用（API Key）
2. 按照规定的格式发送请求
3. 解析返回的数据

Client 把这些复杂的事情都封装好了，你只需要几行代码就能搞定。

---

## 代码示例

### 最简单的初始化

```python
from anthropic import Anthropic

# 方式1：自动从环境变量读取 ANTHROPIC_API_KEY
client = Anthropic()

# 方式2：显式传入 API Key
client = Anthropic(api_key="sk-ant-xxx...")
```

### 异步版本（适合高并发场景）

```python
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()
```

---

## 关键配置项

| 参数 | 作用 | 默认值 |
|------|------|--------|
| `api_key` | 你的 API 密钥 | 读取 `ANTHROPIC_API_KEY` 环境变量 |
| `timeout` | 请求超时时间 | 10 分钟 |
| `max_retries` | 失败自动重试次数 | 2 次 |
| `base_url` | API 地址（用于私有部署） | Anthropic 官方地址 |

### 自定义配置示例

```python
client = Anthropic(
    api_key="sk-ant-xxx",
    timeout=60.0,        # 60秒超时
    max_retries=3,       # 失败重试3次
)
```

---

## 常见坑点

### 1. API Key 泄露
**错误做法**：
```python
client = Anthropic(api_key="sk-ant-abc123...")  # 千万别提交到 Git！
```

**正确做法**：
```python
import os
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

或者使用 `.env` 文件配合 `python-dotenv`：

```bash
# 1. 安装 python-dotenv
pip install python-dotenv

# 2. 创建 .env 文件（在项目根目录）
echo 'ANTHROPIC_API_KEY=sk-ant-xxx...' > .env

# 3. 把 .env 添加到 .gitignore，防止提交到 Git
echo '.env' >> .gitignore
```

```python
# 4. 在代码中加载 .env
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的变量

from anthropic import Anthropic
client = Anthropic()  # 会自动读取 ANTHROPIC_API_KEY
```

### 2. 忘记处理网络错误
```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.APIConnectionError:
    print("网络连接失败")
except anthropic.RateLimitError:
    print("请求太频繁，稍后重试")
except anthropic.APIStatusError as e:
    print(f"API 错误: {e.status_code}")
```

### 3. 同步/异步混用
```python
# 错误：在同步代码中使用 AsyncAnthropic
client = AsyncAnthropic()
response = client.messages.create(...)  # 这会返回协程，不是结果！

# 正确：同步场景用 Anthropic
client = Anthropic()
response = client.messages.create(...)
```

> **什么是异步/协程？** 这是 Python 的进阶概念，用于同时处理多个任务（如同时给100个用户回复）。初学者只需使用同步版本 `Anthropic()` 即可，等熟悉后再学习异步。

---

## 自检清单

- [ ] **费曼检验**：我能向别人讲清楚 Client 是做什么的吗？
- [ ] **迁移检验**：如果换成 OpenAI 的 SDK，我能找到类似的 Client 概念吗？
- [ ] **深度检验**：我能说出为什么需要 Client 而不是直接发 HTTP 请求吗？

---

## 常见问题

### Q1: Client 和 API 有什么区别？
**A**: API 是 Anthropic 提供的"服务"，Client 是你用来"调用这个服务"的工具。就像餐厅（API）和外卖 App（Client）的关系。

### Q2: 同步和异步 Client 选哪个？
**A**: 
- 写脚本、做测试 → 同步 `Anthropic`
- Web 服务、需要同时处理多个请求 → 异步 `AsyncAnthropic`

### Q3: API Key 从哪里获取？
**A**: 登录 [console.anthropic.com](https://console.anthropic.com)，在 API Keys 页面创建。

### Q4: 请求超时了怎么办？
**A**: 
1. 检查网络连接
2. 增加 `timeout` 参数
3. 对于长任务，使用流式响应（streaming）

### Q5: 可以同时创建多个 Client 吗？
**A**: 可以。比如一个连生产环境，一个连测试环境。每个 Client 独立工作。
