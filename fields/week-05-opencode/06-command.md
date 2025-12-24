# Command（命令）详解

## 什么是 Command？

**一句话定义**：Command 就是给常用操作设置的"快捷键"，输入 `/命令名` 就能执行一段预定义的 prompt。

### 生活类比

| 没有 Command | 有 Command |
|-------------|-----------|
| 每次都要说："帮我运行测试，看看有没有失败的，如果有就分析一下原因" | 直接打 `/test` |
| 每次都要说："帮我审查这段代码，关注安全性、性能、可维护性..." | 直接打 `/review` |

就像手机上的快捷指令，一键完成复杂操作。

---

## 内置命令

OpenCode 自带这些命令：

| 命令 | 功能 |
|------|------|
| `/init` | 初始化项目，生成 AGENTS.md |
| `/undo` | 撤销上一步操作 |
| `/redo` | 重做撤销的操作 |
| `/share` | 分享当前对话 |
| `/help` | 显示帮助信息 |
| `/connect` | 配置 API Key |
| `/models` | 选择模型 |
| `/clear` | 清空对话 |

---

## 创建自定义命令

### 方法 1：Markdown 文件（推荐）

在 `.opencode/command/` 目录下创建 `.md` 文件：

```markdown
<!-- .opencode/command/test.md -->
---
description: 运行测试并分析结果
---

运行项目的完整测试套件。
如果有失败的测试，分析原因并给出修复建议。
```

使用：
```
/test
```

### 方法 2：JSON 配置

在 `opencode.json` 中配置：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "description": "运行测试并分析结果",
      "template": "运行项目的完整测试套件。\n如果有失败的测试，分析原因并给出修复建议。"
    }
  }
}
```

---

## 命令配置目录

| 位置 | 作用域 |
|------|--------|
| `~/.config/opencode/command/` | 全局，所有项目可用 |
| `.opencode/command/` | 项目级，仅当前项目可用 |

---

## 配置选项详解

### 完整示例

```markdown
---
description: 创建新的 React 组件
agent: build
model: anthropic/claude-sonnet-4
subtask: false
---

创建一个名为 $ARGUMENTS 的 React 组件。

要求：
- 使用 TypeScript
- 包含基本的 props 类型定义
- 添加适当的注释
- 遵循项目现有的代码风格
```

### 选项说明

| 选项 | 说明 | 示例 |
|------|------|------|
| `description` | 命令描述，在 TUI 中显示 | `"运行测试"` |
| `template` | prompt 模板（JSON 用） | `"运行测试..."` |
| `agent` | 指定使用哪个 Agent | `"build"` / `"plan"` |
| `model` | 指定使用哪个模型 | `"anthropic/claude-sonnet-4"` |
| `subtask` | 是否作为子任务运行 | `true` / `false` |

---

## 模板变量

### $ARGUMENTS - 获取所有参数

```markdown
---
description: 创建新组件
---

创建一个名为 $ARGUMENTS 的 React 组件。
```

使用：
```
/component Button
```

`$ARGUMENTS` 会被替换为 `Button`。

### $1, $2, $3... - 按位置获取参数

```markdown
---
description: 在指定目录创建文件
---

在 $2 目录下创建一个名为 $1 的文件，
内容为：$3
```

使用：
```
/create-file config.json src '{"key": "value"}'
```

- `$1` → `config.json`
- `$2` → `src`
- `$3` → `{"key": "value"}`

---

## 高级特性

### 执行 Shell 命令

用 ` !`command` ` 语法在 prompt 中嵌入命令输出：

```markdown
---
description: 分析最近的提交
---

这是最近的 10 个 git 提交：
!`git log --oneline -10`

分析这些提交，总结最近的开发工作。
```

### 引用文件

用 `@` 语法引用文件内容：

```markdown
---
description: 审查组件代码
---

审查 @src/components/Button.tsx 的代码。

检查：
- 代码质量
- 性能问题
- 可访问性
```

---

## 实用命令示例

### 1. 运行测试

```markdown
<!-- .opencode/command/test.md -->
---
description: 运行测试并分析结果
---

运行测试命令：
!`npm test`

如果有失败的测试：
1. 分析失败原因
2. 给出修复建议
3. 如果是简单问题，直接修复
```

### 2. 代码审查

```markdown
<!-- .opencode/command/review.md -->
---
description: 审查代码变更
agent: plan
---

查看当前的代码变更：
!`git diff`

对这些变更进行代码审查：
- 检查安全问题
- 检查性能问题
- 检查代码风格
- 检查边界情况

给出改进建议。
```

### 3. 快速提交

```markdown
<!-- .opencode/command/commit.md -->
---
description: 智能 git commit
---

查看当前状态：
!`git status`

查看变更内容：
!`git diff --staged`

根据变更生成一个简洁的 commit message，然后执行 git commit。
```

### 4. 创建组件

```markdown
<!-- .opencode/command/component.md -->
---
description: 创建 React 组件
---

创建一个名为 $ARGUMENTS 的 React 组件。

参考现有组件的风格：
@src/components/Button.tsx

要求：
- TypeScript
- 函数式组件
- 包含 Props 接口
- 添加基本样式
```

### 5. 修复 Bug

```markdown
<!-- .opencode/command/fix.md -->
---
description: 分析并修复 Bug
---

问题描述：$ARGUMENTS

步骤：
1. 搜索相关代码
2. 分析问题原因
3. 提出修复方案
4. 实施修复
5. 验证修复是否有效
```

### 6. 文档生成

```markdown
<!-- .opencode/command/doc.md -->
---
description: 为文件生成文档
agent: build
---

为 $ARGUMENTS 生成文档。

包含：
- 函数/类的用途说明
- 参数和返回值文档
- 使用示例
- 注意事项

文档风格：JSDoc 格式
```

---

## 命令组织建议

```
.opencode/
└── command/
    ├── git/
    │   ├── commit.md      # /git/commit
    │   └── pr.md          # /git/pr
    ├── test/
    │   ├── run.md         # /test/run
    │   └── watch.md       # /test/watch
    ├── create/
    │   ├── component.md   # /create/component
    │   └── page.md        # /create/page
    └── review.md          # /review
```

子目录中的命令用 `/目录/文件名` 调用。

---

## 覆盖内置命令

你可以创建与内置命令同名的文件来覆盖它：

```markdown
<!-- .opencode/command/help.md -->
---
description: 自定义帮助信息
---

显示项目特定的帮助信息：

1. 本项目使用 React + TypeScript
2. 运行 /test 执行测试
3. 运行 /review 审查代码
...
```

---

## 调试技巧

### 1. 查看命令是否加载

在 TUI 中输入 `/`，会显示所有可用命令。

### 2. 检查参数替换

```markdown
---
description: 调试参数
---

收到的参数：
- $ARGUMENTS = "$ARGUMENTS"
- $1 = "$1"
- $2 = "$2"
```

### 3. 检查 Shell 输出

```markdown
---
description: 调试 Shell
---

命令输出：
!`echo "Hello World"`
```

---

## 常见问题

### Q: 命令没有生效怎么办？
**A:** 检查：
1. 文件位置是否正确（`.opencode/command/`）
2. 文件扩展名是否是 `.md`
3. 重启 OpenCode 试试

### Q: 如何传递带空格的参数？
**A:** 用引号包裹：
```
/create-file "my file.txt" "Hello World"
```

### Q: 可以在命令中调用其他命令吗？
**A:** 目前不支持直接嵌套调用。但你可以在 prompt 中让 AI 执行多个步骤。

### Q: 命令可以访问环境变量吗？
**A:** Shell 命令（!`...`）可以访问。prompt 模板本身不能直接访问。

---

## 下一步

- 了解 [Config（配置）](./07-config.md) 完整配置
- 学习 [Permission（权限）](./08-permission.md) 控制
- 查看 [实战案例](./case-add-feature.md)
