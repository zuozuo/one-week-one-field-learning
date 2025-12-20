#!/usr/bin/env python3
"""
AI Review 脚本

并行调用 Claude Code / Codex / Gemini CLI 对内容进行 review，
然后汇总意见并优化内容。

用法:
    python ai_review.py --topic "量子物理" --content-path /path/to/content --output-path /path/to/reviews

参数:
    --topic: 主题名称，用于构建 review prompt
    --content-path: 要 review 的内容的完整绝对路径
    --output-path: review 结果的输出路径
    --skip-optimize: 跳过优化步骤，只生成 review
"""

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# 代理配置
PROXY_CONFIG = {
    "https_proxy": "http://127.0.0.1:10080",
    "http_proxy": "http://127.0.0.1:10080",
    "all_proxy": "socks5://127.0.0.1:10081",
}

# AI CLI 工具配置
AI_TOOLS = {
    "claude": {
        "cmd": "claude",
        "args": ["-p", "{prompt}", "--allowedTools", "Read,Write,Bash"],
        "output_file": "review-claude.md",
    },
    "codex": {
        "cmd": "codex",
        "args": ["-p", "{prompt}"],
        "output_file": "review-codex.md",
    },
    "gemini": {
        "cmd": "gemini",
        "args": ["-p", "{prompt}"],
        "output_file": "review-gemini.md",
    },
}

# 超时配置（秒）
REVIEW_TIMEOUT = 600  # 10 分钟
OPTIMIZE_TIMEOUT = 900  # 15 分钟


def build_review_prompt(topic: str, content_path: str, output_path: str, tool_name: str) -> str:
    """构建 review prompt"""
    output_file = AI_TOOLS[tool_name]["output_file"]
    
    return f"""你是 {topic} 领域的顶级专家。

{content_path} 里面是我们写的让小白用户学习 {topic} 的教程。

请用你专业的眼光 review 这个教程，重点关注：
1. 知识体系的完整性 - 是否覆盖了该领域的核心概念？有没有遗漏重要内容？
2. 小白用户的学习上手容易程度 - 解释是否通俗易懂？例子是否贴切？学习曲线是否合理？
3. 内容的准确性 - 有没有错误或不准确的地方？

请把你发现的问题和改进建议总结成一份 review 报告。

**重要**：将你的 review 报告写入文件 {output_path}/{output_file}"""


def build_optimize_prompt(topic: str, content_path: str, reviews_path: str) -> str:
    """构建优化 prompt"""
    return f"""你是 {topic} 领域的顶级专家，同时也是优秀的技术写作者。

## 任务

请根据多位 AI 专家的 review 意见，优化 {content_path} 中的教程内容。

## Review 文件位置

请读取 {reviews_path} 目录下的所有 review 文件：
- review-claude.md
- review-codex.md  
- review-gemini.md

## 执行步骤

### 步骤 1: 汇总 Review 意见

读取所有 review 文件，将意见汇总整理：
- 找出多个 AI 都提到的问题（高优先级）
- 整理具体的改进建议
- 将汇总结果写入 {reviews_path}/summary.md

汇总格式：
```markdown
# Review 意见汇总

## 高优先级问题（多个 AI 都提到）
- ...

## Claude 专家意见
- ...

## Codex 专家意见
- ...

## Gemini 专家意见
- ...

## 待改进项清单
- [ ] ...
```

### 步骤 2: 优化教程内容

根据汇总的意见，逐一优化 {content_path} 中的教程：

1. **知识完整性问题**：补充遗漏的核心概念
2. **易懂性问题**：优化解释方式，增加更贴切的类比和例子
3. **准确性问题**：修正错误或不准确的内容
4. **更新 README.md**：如果添加了新内容，同步更新

### 步骤 3: 输出优化报告

完成后，在 {reviews_path}/optimization-report.md 中记录：
- 汇总了哪些主要问题
- 做了哪些优化改进
- 优化后的教程结构变化"""


def setup_environment() -> dict:
    """设置环境变量（包含代理）"""
    env = os.environ.copy()
    env.update(PROXY_CONFIG)
    return env


def run_ai_review(tool_name: str, prompt: str, env: dict, timeout: int = REVIEW_TIMEOUT) -> dict:
    """运行单个 AI CLI 工具进行 review"""
    tool_config = AI_TOOLS[tool_name]
    cmd = [tool_config["cmd"]]
    
    # 构建命令参数
    for arg in tool_config["args"]:
        if arg == "{prompt}":
            cmd.append(prompt)
        else:
            cmd.append(arg)
    
    print(f"🚀 启动 {tool_name} review...")
    
    result = {
        "tool": tool_name,
        "success": False,
        "output": "",
        "error": "",
    }
    
    try:
        process = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["success"] = process.returncode == 0
        
        if result["success"]:
            print(f"✅ {tool_name} review 完成")
        else:
            print(f"❌ {tool_name} review 失败: {process.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        result["error"] = f"超时 ({timeout}秒)"
        print(f"⏰ {tool_name} review 超时")
    except FileNotFoundError:
        result["error"] = f"未找到命令: {tool_config['cmd']}"
        print(f"❌ {tool_name} 未安装或不在 PATH 中")
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ {tool_name} review 异常: {e}")
    
    return result


def run_parallel_reviews(topic: str, content_path: str, output_path: str) -> list:
    """并行运行所有 AI review"""
    env = setup_environment()
    results = []
    
    print("\n" + "=" * 60)
    print("📝 开始并行 AI Review")
    print("=" * 60)
    print(f"主题: {topic}")
    print(f"内容路径: {content_path}")
    print(f"输出路径: {output_path}")
    print("=" * 60 + "\n")
    
    # 使用线程池并行执行
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        
        for tool_name in AI_TOOLS:
            prompt = build_review_prompt(topic, content_path, output_path, tool_name)
            future = executor.submit(run_ai_review, tool_name, prompt, env)
            futures[future] = tool_name
        
        # 收集结果
        for future in as_completed(futures):
            tool_name = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ {tool_name} 执行异常: {e}")
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e),
                })
    
    return results


def check_review_files(output_path: str) -> dict:
    """检查 review 文件是否生成"""
    status = {}
    for tool_name, config in AI_TOOLS.items():
        file_path = os.path.join(output_path, config["output_file"])
        exists = os.path.exists(file_path)
        status[tool_name] = {
            "file": config["output_file"],
            "exists": exists,
            "path": file_path,
        }
    return status


def run_optimization(topic: str, content_path: str, reviews_path: str) -> bool:
    """运行优化流程"""
    print("\n" + "=" * 60)
    print("🔧 开始汇总 Review 并优化教程")
    print("=" * 60 + "\n")
    
    env = setup_environment()
    prompt = build_optimize_prompt(topic, content_path, reviews_path)
    
    cmd = ["claude", "-p", prompt, "--allowedTools", "Read,Write,Bash"]
    
    try:
        process = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=OPTIMIZE_TIMEOUT,
        )
        
        if process.returncode == 0:
            print("✅ 优化完成")
            return True
        else:
            print(f"❌ 优化失败: {process.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 优化超时 ({OPTIMIZE_TIMEOUT}秒)")
        return False
    except FileNotFoundError:
        print("❌ Claude CLI 未安装或不在 PATH 中")
        return False
    except Exception as e:
        print(f"❌ 优化异常: {e}")
        return False


def print_summary(review_results: list, file_status: dict, optimize_success: bool = None):
    """打印执行摘要"""
    print("\n" + "=" * 60)
    print("📊 执行摘要")
    print("=" * 60)
    
    print("\n📝 Review 结果:")
    for result in review_results:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['tool']}")
        if result.get("error"):
            print(f"      错误: {result['error'][:100]}")
    
    print("\n📁 Review 文件:")
    for tool_name, status in file_status.items():
        icon = "✅" if status["exists"] else "❌"
        print(f"  {icon} {status['file']}")
    
    if optimize_success is not None:
        print(f"\n🔧 优化: {'✅ 成功' if optimize_success else '❌ 失败'}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="AI Review 脚本 - 并行调用多个 AI 进行 review 并优化内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python ai_review.py --topic "量子物理" \\
        --content-path /path/to/week-03-quantum-physics \\
        --output-path /path/to/week-03-quantum-physics/reviews
        
    # 只执行 review，跳过优化
    python ai_review.py --topic "量子物理" \\
        --content-path /path/to/content \\
        --output-path /path/to/reviews \\
        --skip-optimize
        """,
    )
    
    parser.add_argument(
        "--topic",
        required=True,
        help="主题名称，用于构建 review prompt",
    )
    parser.add_argument(
        "--content-path",
        required=True,
        help="要 review 的内容的完整绝对路径",
    )
    parser.add_argument(
        "--output-path",
        required=True,
        help="review 结果的输出路径",
    )
    parser.add_argument(
        "--skip-optimize",
        action="store_true",
        help="跳过优化步骤，只生成 review",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=REVIEW_TIMEOUT,
        help=f"单个 review 的超时时间（秒），默认 {REVIEW_TIMEOUT}",
    )
    
    args = parser.parse_args()
    
    # 验证路径
    if not os.path.exists(args.content_path):
        print(f"❌ 内容路径不存在: {args.content_path}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(args.output_path, exist_ok=True)
    
    # 步骤 1: 并行执行 AI Review
    review_results = run_parallel_reviews(
        topic=args.topic,
        content_path=args.content_path,
        output_path=args.output_path,
    )
    
    # 等待一下让文件写入完成
    time.sleep(2)
    
    # 步骤 2: 检查 review 文件
    file_status = check_review_files(args.output_path)
    
    # 步骤 3: 汇总并优化（如果不跳过）
    optimize_success = None
    if not args.skip_optimize:
        # 检查是否有足够的 review 文件
        existing_files = sum(1 for s in file_status.values() if s["exists"])
        if existing_files >= 1:
            optimize_success = run_optimization(
                topic=args.topic,
                content_path=args.content_path,
                reviews_path=args.output_path,
            )
        else:
            print("⚠️ 没有生成任何 review 文件，跳过优化步骤")
    
    # 打印摘要
    print_summary(review_results, file_status, optimize_success)
    
    # 返回退出码
    success_count = sum(1 for r in review_results if r["success"])
    if success_count == 0:
        sys.exit(1)
    elif success_count < len(AI_TOOLS):
        sys.exit(2)  # 部分成功
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

