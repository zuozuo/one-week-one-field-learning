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

## 步骤 5: 多 AI 专家 Review

教程生成完成后，启动多个 AI 工具并行 review 教程质量。

### 5.1 创建 reviews 目录
```bash
mkdir -p fields/{week-XX-主题名}/reviews
```

### 5.2 构建 Review Prompt
构建以下 prompt（将 `{Topic}` 和 `{目录路径}` 替换为实际值）：

```
你是 {Topic} 领域的顶级专家。

{目录路径} 里面是我们写的让小白用户学习 {Topic} 的教程。

请用你专业的眼光 review 这个教程，重点关注：
1. 知识体系的完整性 - 是否覆盖了该领域的核心概念？有没有遗漏重要内容？
2. 小白用户的学习上手容易程度 - 解释是否通俗易懂？例子是否贴切？学习曲线是否合理？
3. 内容的准确性 - 有没有错误或不准确的地方？

请把你发现的问题和改进建议总结成一份 review 报告，写到 {目录路径}/reviews/ 目录下。
```

### 5.3 并行启动 AI Review（后台运行）

**重要：在一个命令中同时启动三个 AI，确保并行执行：**

```bash
# 设置代理并并行启动三个 AI CLI 工具
export https_proxy=http://127.0.0.1:10080 && \
export http_proxy=http://127.0.0.1:10080 && \
export all_proxy=socks5://127.0.0.1:10081 && \
claude -p "{review_prompt}" --allowedTools "Read,Write,Bash" > /dev/null 2>&1 & \
codex -p "{review_prompt}" --allowedTools "Read,Write,Bash" > /dev/null 2>&1 & \
gemini -p "{review_prompt}" > /dev/null 2>&1 &
```

输出文件：
- Claude Code → `reviews/review-claude.md`
- Codex → `reviews/review-codex.md`
- Gemini CLI → `reviews/review-gemini.md`

### 5.4 告知用户
告诉用户：
- "已启动 Claude Code、Codex、Gemini CLI 并行 review 教程"
- "Review 结果将写入 `{目录路径}/reviews/` 目录"
- "这些 AI 在后台运行，不阻塞后续流程"

## 步骤 6: 更新项目 README
更新项目根目录的 `README.md` 文件：
- 在文件中添加新创建的学习主题
- 包含主题名称和目录链接
- 保持与现有格式一致

## 步骤 7: 提交代码
执行以下 Git 操作：
1. `git add -A` - 添加所有新文件
2. `git commit -m "feat: 添加 {主题名称} 学习内容"` - 提交代码，commit message 中包含主题名称

## 步骤 8: 推送代码
执行 `git push` 将代码推送到远程仓库。

如果 push 失败（如没有设置远程仓库），告知用户失败原因，但不影响整体流程的完成。
