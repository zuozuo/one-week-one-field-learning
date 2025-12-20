---
description: 对已有的学习内容进行多 AI Review 并优化
allowed-tools: Bash, Read, Write, Glob, Git
---

用户指定的内容路径是: $ARGUMENTS

**重要：检查用户输入**

首先检查 `$ARGUMENTS` 是否为空：
- 如果 `$ARGUMENTS` 为空或只包含空白字符，你必须**停止执行**，并询问用户："请告诉我要 review 的内容路径，例如：fields/week-03-quantum-physics"。然后等待用户回复后再继续。
- 如果 `$ARGUMENTS` 有内容，则继续执行下面的步骤。

---

请按照以下步骤执行：

## 步骤 1: 验证路径

检查用户提供的路径是否存在：

```bash
ls -la {用户提供的路径}
```

如果路径不存在，告知用户并询问正确的路径。

## 步骤 2: 识别主题

从路径中提取主题信息：
- 读取 `{路径}/README.md` 文件
- 从文件标题或内容中识别主题名称（中文）
- 如果无法识别，询问用户主题名称

## 步骤 3: 多 AI 专家 Review 与优化

使用 `scripts/ai_review.py` 脚本进行多 AI 并行 review 和优化。

### 3.1 运行 AI Review 脚本

执行以下命令（将变量替换为实际值）：

```bash
python scripts/ai_review.py \
    --topic "{识别出的中文主题名}" \
    --content-path "$(pwd)/{用户提供的路径}" \
    --output-path "$(pwd)/{用户提供的路径}/reviews"
```

**脚本功能**：
1. 设置代理环境变量
2. 并行调用 Claude Code / Codex / Gemini CLI 进行 review
3. 等待三个 AI 完成 review
4. 自动调用 Claude Code 汇总 review 意见
5. 根据汇总意见优化教程内容

**输出文件**：
- `reviews/review-claude.md` - Claude 的 review
- `reviews/review-codex.md` - Codex 的 review
- `reviews/review-gemini.md` - Gemini 的 review
- `reviews/summary.md` - 汇总的意见
- `reviews/optimization-report.md` - 优化报告

### 3.2 检查结果

脚本执行完成后，检查 `reviews/` 目录下的文件：
- 确认 review 文件已生成
- 查看 `summary.md` 了解主要问题
- 查看 `optimization-report.md` 了解优化内容

### 3.3 告知用户

告诉用户：
- Review 和优化的执行结果
- 如果有失败的 AI 工具，说明原因
- 优化后的教程结构变化

## 步骤 4: 提交代码

执行以下 Git 操作：
1. `git add -A` - 添加所有新文件和优化后的内容
2. `git commit -m "refactor: 优化 {主题名称} 教程（多 AI Review）"` - 提交代码

## 步骤 5: 推送代码

执行 `git push` 将代码推送到远程仓库。

如果 push 失败（如没有设置远程仓库），告知用户失败原因，但不影响整体流程的完成。

