---
description: 创建新的学习主题目录并开始学习
allowed-tools: Bash, Read, Write, Skill, Glob, Git
---

用户想要学习的主题是: $ARGUMENTS

**重要：检查用户输入**

首先检查 `$ARGUMENTS` 是否为空：
- 如果 `$ARGUMENTS` 为空或只包含空白字符，你必须**停止执行**，并询问用户："请告诉我你想学习的主题是什么？"。然后等待用户回复后再继续。
- 如果 `$ARGUMENTS` 有内容，则继续执行下面的步骤。

---

请按照以下步骤执行：

## 步骤 1: 翻译主题
将用户输入的主题翻译成英文（如果已经是英文则保持不变）。翻译结果应该：
- 使用小写字母
- 用连字符 `-` 连接多个单词
- 简洁明了，适合作为目录名

## 步骤 2: 确定新的 week 编号
查看 @fields/ 目录下所有以 `week-` 开头的目录，找出最大的数字编号，然后加 1 作为新的编号。

例如：如果现有目录是 `week-01-crypto` 和 `week-02-learning-methodology`，那么新编号应该是 `03`。

## 步骤 3: 创建新目录
在 `fields/` 目录下创建新目录，命名格式为：`week-{编号}-{英文主题}`

编号需要补零到两位数（如 01, 02, 03...）。

## 步骤 4: 开始学习
使用 `learn-new-domain` skill 在新创建的目录中开始学习这个主题。

在调用 skill 之前，先告诉用户你创建的目录名称。

## 步骤 5: 多 AI 专家 Review 与优化

教程生成完成后，使用 `scripts/ai_review.py` 脚本进行多 AI 并行 review 和优化。

### 5.1 运行 AI Review 脚本

执行以下命令（将变量替换为实际值）：

```bash
python scripts/ai_review.py \
    --topic "{中文主题名}" \
    --content-path "$(pwd)/fields/{week-XX-主题名}" \
    --output-path "$(pwd)/fields/{week-XX-主题名}/reviews"
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

### 5.2 检查结果

脚本执行完成后，检查 `reviews/` 目录下的文件：
- 确认 review 文件已生成
- 查看 `summary.md` 了解主要问题
- 查看 `optimization-report.md` 了解优化内容

### 5.3 告知用户

告诉用户：
- Review 和优化的执行结果
- 如果有失败的 AI 工具，说明原因
- 优化后的教程结构变化

## 步骤 6: 更新项目 README
更新项目根目录的 `README.md` 文件：
- 在文件中添加新创建的学习主题
- 包含主题名称和目录链接
- 保持与现有格式一致

## 步骤 7: 提交代码
执行以下 Git 操作：
1. `git add -A` - 添加所有新文件和优化后的内容
2. `git commit -m "feat: 添加 {主题名称} 学习内容（含多 AI Review 优化）"` - 提交代码

## 步骤 8: 推送代码
执行 `git push` 将代码推送到远程仓库。

如果 push 失败（如没有设置远程仓库），告知用户失败原因，但不影响整体流程的完成。
