# 实战案例：用 OpenCode 添加新功能

本案例将带你完整体验如何使用 OpenCode 给项目添加一个"用户登录"功能。

---

## 场景描述

假设你有一个简单的 Express.js 后端项目，现在需要添加用户登录功能。

---

## 准备工作

### 1. 安装 OpenCode

```bash
# 选择一种安装方式
curl -fsSL https://opencode.ai/install | bash

# 或者用 npm
npm install -g opencode-ai
```

### 2. 配置 API Key

```bash
# 进入项目目录
cd my-express-app

# 启动 OpenCode
opencode

# 配置 API（选择你的 Provider）
/connect
```

### 3. 初始化项目

```bash
# 让 OpenCode 分析项目结构
/init
```

这会生成一个 `AGENTS.md` 文件，帮助 AI 理解你的项目。

---

## 第一步：规划方案（Plan 模式）

### 切换到 Plan 模式

按 `Tab` 键，看到右下角显示 `[Plan]`

### 描述需求

输入：
```
I need to add user authentication to this Express app.
It should include:
1. User registration with email and password
2. User login with JWT tokens
3. Password hashing
4. Protected route middleware

Please analyze the current codebase and propose an implementation plan.
```

### AI 分析项目

AI 会：
1. 读取现有代码结构
2. 查看已有的依赖
3. 理解项目的代码风格

### AI 给出方案

```
Plan 模式下，AI 会输出类似这样的方案：

## 实现方案

### 1. 新增依赖
- bcryptjs: 密码哈希
- jsonwebtoken: JWT 处理
- express-validator: 输入验证

### 2. 新增文件
- src/middleware/auth.js - 认证中间件
- src/routes/auth.js - 认证路由
- src/models/User.js - 用户模型

### 3. 修改文件
- src/app.js - 注册新路由
- package.json - 添加依赖

### 4. 实现细节
...
```

### 审查并调整方案

你可以提出修改意见：

```
I'd prefer using Argon2 instead of bcrypt for password hashing.
Also, please add refresh token functionality.
```

AI 会更新方案。

---

## 第二步：实施代码（Build 模式）

### 切换到 Build 模式

按 `Tab` 键，看到右下角显示 `[Build]`

### 开始实施

输入：
```
Great plan! Let's implement it step by step.
Start with installing the dependencies and creating the User model.
```

### AI 开始工作

```
AI 会执行一系列操作：

1. 执行命令：
   > npm install argon2 jsonwebtoken express-validator

2. 创建文件 src/models/User.js：
   （显示文件内容预览）

3. 创建文件 src/middleware/auth.js：
   （显示文件内容预览）

...
```

### 监督过程

如果你的权限设置是 `ask`，每个操作都会询问你：

```
┌────────────────────────────────────────────┐
│ OpenCode 请求执行：                         │
│                                            │
│ bash: npm install argon2 jsonwebtoken      │
│                                            │
│ [允许] [拒绝]                              │
└────────────────────────────────────────────┘
```

---

## 第三步：测试功能

### 让 AI 写测试

```
Now write some unit tests for the authentication endpoints.
```

AI 会：
1. 创建测试文件
2. 写测试用例
3. 可能会运行测试

### 运行测试

```
Run the tests and fix any failures.
```

AI 会执行 `npm test` 并分析结果。

---

## 第四步：处理问题

### 如果有错误

AI 发现测试失败：
```
Test failed: User registration - password too short
Expected: validation error
Received: 500 internal error
```

AI 会自动分析并修复：
```
I found the issue. The validation middleware is not properly
connected. Let me fix that...

修改 src/routes/auth.js...
```

### 如果不满意结果

使用 `/undo` 撤销：
```
/undo
```

然后重新描述你的需求：
```
Let's try a different approach. Instead of middleware validation,
use Joi schema validation.
```

---

## 第五步：优化和完善

### 添加文档

```
Add JSDoc comments to all the new functions and update the README
with API documentation for the auth endpoints.
```

### 代码审查

```
@explore check all the new files for potential security issues
```

或切换到 Plan 模式：
```
<Tab>
Review the authentication implementation for security best practices.
Check for:
- SQL injection
- Password handling
- Token security
- Rate limiting
```

---

## 完整对话示例

```
┌─────────────────────────────────────────────────────────────────┐
│ 你的对话过程可能是这样的：                                        │
└─────────────────────────────────────────────────────────────────┘

你 [Plan]: I need to add user auth with JWT...
AI: 好的，让我分析一下项目...
    [读取文件 src/app.js]
    [读取文件 package.json]
    这是我的实现方案：...

你 [Plan]: 用 Argon2 替代 bcrypt
AI: 明白，更新后的方案：...

你 [Build]: 开始实施
AI: 好的，首先安装依赖...
    [执行 npm install argon2 jsonwebtoken]
    [创建 src/models/User.js]
    [创建 src/middleware/auth.js]
    [创建 src/routes/auth.js]
    [修改 src/app.js]

你 [Build]: 写测试
AI: [创建 tests/auth.test.js]
    [执行 npm test]
    有 2 个测试失败，让我修复...
    [修改 src/routes/auth.js]
    [执行 npm test]
    全部通过！

你 [Build]: /undo (不满意某个改动)
AI: 已撤销上一步操作。

你 [Build]: 用这种方式代替...
AI: 明白，重新实现...
```

---

## 实用技巧总结

### 1. 先 Plan 后 Build

复杂功能一定要先规划：
```
Plan 模式 → 讨论方案 → Build 模式 → 实施
```

### 2. 分步骤实施

不要一次性让 AI 做太多：
```
# 好的做法
先安装依赖，创建 User 模型

# 不好的做法
实现完整的用户认证系统（太笼统）
```

### 3. 善用 @文件引用

```
参考 @src/routes/users.js 的风格实现新的路由
```

### 4. 善用 /undo

不满意就撤销，重新来：
```
/undo
Let's try a different approach...
```

### 5. 善用子代理

```
@explore 找找项目里有没有类似的认证代码
@general 搜索所有使用了 deprecated API 的地方
```

### 6. 创建常用命令

```markdown
<!-- .opencode/command/test.md -->
---
description: 运行测试
---
运行 npm test，分析结果，修复失败的测试。
```

然后直接用 `/test`。

---

## 常见问题

### Q: AI 改错了代码怎么办？
**A:** 用 `/undo` 撤销，然后更清楚地描述你的需求。

### Q: AI 理解错了需求怎么办？
**A:** 给更多上下文，用 `@文件` 引用相关代码，或者给出具体例子。

### Q: 怎么让 AI 遵循项目规范？
**A:**
1. 运行 `/init` 生成 AGENTS.md
2. 在 AGENTS.md 中添加代码规范
3. 用 `instructions` 配置引用规范文件

### Q: AI 一直在循环执行怎么办？
**A:** 按 `Ctrl+C` 中断，然后给出更清晰的指令。

---

## 下一步

恭喜你完成了这个实战案例！现在你可以：

1. 在自己的项目中尝试使用 OpenCode
2. 创建自己的常用命令（`/test`、`/review` 等）
3. 定制适合你的 Agent
4. 探索 MCP Server 扩展能力

祝你编码愉快！
