# Anchor 框架

## 一句话大白话

**Anchor 是 Solana 智能合约开发的"瑞士军刀"，把原本繁琐的 Rust 底层开发变成了简洁的声明式开发——就像 Ruby on Rails 之于 Web 开发。**

你可以把它想象成：如果原生 Solana 开发是手搓面条，Anchor 就是面条机——输入面粉和水（你的逻辑），自动产出整齐的面条（可靠的合约）。

## 它解决什么问题

原生 Solana Program 开发的痛点：
1. **样板代码太多**：账户验证、序列化/反序列化要写很多重复代码
2. **容易出错**：忘记验证账户权限会导致安全漏洞
3. **测试困难**：需要手动构造交易和账户

Anchor 的解决方案：
- **声明式账户验证**：用宏自动生成验证代码
- **自动序列化**：定义结构体，自动处理序列化
- **集成测试框架**：TypeScript 测试开箱即用
- **IDL 生成**：自动生成前端调用所需的接口描述

## 什么时候用 / 什么时候别用

### 什么时候用 Anchor
- 刚开始学 Solana 开发（入门更简单）
- 中小型项目（快速迭代）
- 需要和前端协作（IDL 很方便）

### 什么时候可能不用
- 极致性能优化（原生可省 CU）
- 超底层操作
- 团队精通原生 Solana 开发

> 实际上，90%+ 的 Solana 项目都用 Anchor。

## 它不是什么

### 常见混淆点

| 你可能以为 | 实际上是 |
|-----------|---------|
| Anchor 是一种语言 | Anchor 是 Rust 框架，底层还是 Rust |
| 用 Anchor 性能差 | 差距很小，大多数场景可忽略 |
| Anchor 只能用于简单项目 | Jupiter、Marinade 等大项目都用 Anchor |

## 最小例子

### 1. 环境安装

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# 安装 Anchor
cargo install --git https://github.com/coral-xyz/anchor avm --locked
avm install latest
avm use latest

# 验证安装
anchor --version
```

### 2. 创建项目

```bash
# 创建新项目
anchor init my_project
cd my_project

# 项目结构
my_project/
├── Anchor.toml          # 项目配置
├── Cargo.toml           # Rust 依赖
├── programs/            # 智能合约代码
│   └── my_project/
│       └── src/
│           └── lib.rs   # 主合约文件
├── tests/               # 测试代码
│   └── my_project.ts    # TypeScript 测试
└── target/              # 编译产物
```

### 3. 编写第一个 Program

```rust
// programs/my_project/src/lib.rs
use anchor_lang::prelude::*;

// 程序 ID（部署后会更新）
declare_id!("你的Program地址");

#[program]
pub mod my_project {
    use super::*;

    // 初始化：创建一个存储计数器的账户
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let counter = &mut ctx.accounts.counter;
        counter.count = 0;
        msg!("Counter initialized!");
        Ok(())
    }

    // 增加计数
    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        let counter = &mut ctx.accounts.counter;
        counter.count += 1;
        msg!("Counter incremented to {}", counter.count);
        Ok(())
    }
}

// 定义 Counter 账户的数据结构
#[account]
pub struct Counter {
    pub count: u64,
}

// Initialize 指令需要的账户
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,                          // 创建新账户
        payer = user,                  // 谁支付租金
        space = 8 + 8                  // 空间：8(discriminator) + 8(u64)
    )]
    pub counter: Account<'info, Counter>,

    #[account(mut)]
    pub user: Signer<'info>,           // 必须签名

    pub system_program: Program<'info, System>,
}

// Increment 指令需要的账户
#[derive(Accounts)]
pub struct Increment<'info> {
    #[account(mut)]                    // 只需要可写，不需要 init
    pub counter: Account<'info, Counter>,
}
```

### 4. 编译和部署

```bash
# 编译
anchor build

# 获取 Program ID
solana address -k target/deploy/my_project-keypair.json

# 更新 declare_id! 和 Anchor.toml 中的 ID

# 配置网络（使用 devnet）
solana config set --url devnet

# 获取测试币
solana airdrop 2

# 部署
anchor deploy

# 或者一键构建+部署
anchor build && anchor deploy
```

### 5. 编写测试

```typescript
// tests/my_project.ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyProject } from "../target/types/my_project";
import { expect } from "chai";

describe("my_project", () => {
  // 配置客户端
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.MyProject as Program<MyProject>;

  // 生成 counter 账户的密钥对
  const counter = anchor.web3.Keypair.generate();

  it("Initializes the counter", async () => {
    await program.methods
      .initialize()
      .accounts({
        counter: counter.publicKey,
        user: program.provider.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([counter])
      .rpc();

    // 获取账户数据
    const account = await program.account.counter.fetch(counter.publicKey);
    expect(account.count.toNumber()).to.equal(0);
  });

  it("Increments the counter", async () => {
    await program.methods
      .increment()
      .accounts({
        counter: counter.publicKey,
      })
      .rpc();

    const account = await program.account.counter.fetch(counter.publicKey);
    expect(account.count.toNumber()).to.equal(1);
  });
});
```

```bash
# 运行测试
anchor test
```

## Anchor 核心概念

### 账户约束 (Constraints)

```rust
#[derive(Accounts)]
pub struct MyInstruction<'info> {
    // init: 创建新账户
    #[account(init, payer = user, space = 8 + 32)]
    pub new_account: Account<'info, MyData>,

    // mut: 账户数据可修改
    #[account(mut)]
    pub mutable_account: Account<'info, MyData>,

    // has_one: 验证字段匹配
    #[account(has_one = authority)]
    pub data_account: Account<'info, MyData>,

    // seeds + bump: PDA 账户
    #[account(
        seeds = [b"my-seed", user.key().as_ref()],
        bump
    )]
    pub pda_account: Account<'info, MyData>,

    // constraint: 自定义验证
    #[account(constraint = amount > 0 @ MyError::InvalidAmount)]
    pub amount: u64,

    // Signer: 必须签名
    pub user: Signer<'info>,

    // Program: 系统程序
    pub system_program: Program<'info, System>,
}
```

### 错误处理

```rust
// 定义错误
#[error_code]
pub enum MyError {
    #[msg("Amount must be greater than zero")]
    InvalidAmount,
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Overflow occurred")]
    Overflow,
}

// 使用错误
pub fn my_instruction(ctx: Context<MyInstruction>, amount: u64) -> Result<()> {
    require!(amount > 0, MyError::InvalidAmount);
    require!(
        ctx.accounts.authority.key() == ctx.accounts.data.authority,
        MyError::Unauthorized
    );
    Ok(())
}
```

### PDA（Program Derived Address）

```rust
// 定义 PDA 账户
#[derive(Accounts)]
#[instruction(seed_value: String)]
pub struct CreatePDA<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + 32 + 4 + seed_value.len(),
        seeds = [b"my-pda", user.key().as_ref(), seed_value.as_bytes()],
        bump
    )]
    pub pda_account: Account<'info, MyPDA>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub system_program: Program<'info, System>,
}

// 在指令中使用 bump
pub fn create_pda(ctx: Context<CreatePDA>, seed_value: String) -> Result<()> {
    let pda = &mut ctx.accounts.pda_account;
    pda.bump = ctx.bumps.pda_account;  // 保存 bump 供后续使用
    pda.seed = seed_value;
    Ok(())
}
```

## 新手最常踩的 3 个坑

### 坑 1：忘记更新 Program ID

**问题**：部署后调用失败，报错 "Program ID mismatch"

**原因**：`declare_id!` 中的地址和实际部署地址不一致

**解决**：
```bash
# 1. 编译获取密钥
anchor build

# 2. 查看生成的 Program ID
solana address -k target/deploy/my_project-keypair.json

# 3. 更新 lib.rs 中的 declare_id!
# 4. 更新 Anchor.toml 中的 [programs.devnet]
# 5. 重新编译部署
anchor build && anchor deploy
```

### 坑 2：Space 计算错误

**问题**：初始化账户失败，报错 "Account data too small"

**原因**：`space` 参数没有正确计算账户大小

**计算公式**：
```rust
// space = 8 (discriminator) + 实际数据大小

#[account]
pub struct MyAccount {
    pub authority: Pubkey,      // 32 bytes
    pub count: u64,             // 8 bytes
    pub name: String,           // 4 + 字符串长度 bytes
    pub items: Vec<u64>,        // 4 + (8 * 元素数量) bytes
}

// 总共: 8 + 32 + 8 + (4 + 32) + (4 + 8*10) = 168 bytes
```

### 坑 3：测试时签名者遗漏

**问题**：测试报错 "Missing signature"

**原因**：init 创建的账户需要作为签名者

```typescript
// 错误
await program.methods
  .initialize()
  .accounts({
    counter: counter.publicKey,
    user: program.provider.publicKey,
    systemProgram: SystemProgram.programId,
  })
  .rpc();  // 缺少 signers!

// 正确
await program.methods
  .initialize()
  .accounts({
    counter: counter.publicKey,
    user: program.provider.publicKey,
    systemProgram: SystemProgram.programId,
  })
  .signers([counter])  // 添加 counter 作为签名者
  .rpc();
```

## 流程图定位

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Anchor 开发流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  编写    │    │ anchor   │    │ anchor   │    │ anchor   │    │  前端    │
│ Rust代码 │───▶│  build   │───▶│  test    │───▶│  deploy  │───▶│  集成    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
 使用 Anchor    编译生成:        TypeScript      部署到链上      使用生成的
 宏简化开发     - .so 文件       本地测试        Devnet/Mainnet  IDL 调用
               - IDL 文件
               - TypeScript类型
```

## Anchor vs 原生对比

```rust
// 原生 Solana Program（繁琐）
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // 手动解析 instruction_data
    let instruction = MyInstruction::try_from_slice(instruction_data)?;

    // 手动获取账户
    let accounts_iter = &mut accounts.iter();
    let account1 = next_account_info(accounts_iter)?;
    let account2 = next_account_info(accounts_iter)?;

    // 手动验证账户
    if !account1.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }
    if account1.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }

    // 手动反序列化
    let mut data = MyData::try_from_slice(&account2.data.borrow())?;

    // 业务逻辑
    data.value += 1;

    // 手动序列化
    data.serialize(&mut *account2.data.borrow_mut())?;

    Ok(())
}

// Anchor（简洁）
#[program]
pub mod my_program {
    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        ctx.accounts.data.value += 1;  // 直接操作
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Increment<'info> {
    #[account(mut)]
    pub data: Account<'info, MyData>,
    pub signer: Signer<'info>,  // 自动验证签名
}
```

## 自测题

1. **基础题**：Anchor 的 `space = 8 + 8` 中，第一个 8 是什么？
   <details>
   <summary>答案</summary>
   是 discriminator（鉴别器），8 字节，Anchor 自动在每个账户数据前面加上这个标识，用于区分不同类型的账户。
   </details>

2. **理解题**：`#[account(init)]` 和 `#[account(mut)]` 有什么区别？
   <details>
   <summary>答案</summary>
   - `init`: 创建新账户，需要 payer 和 space，需要账户作为签名者
   - `mut`: 标记现有账户为可写，不创建新账户

   如果账户已存在但用了 init，会报错；如果账户不存在但用了 mut，也会报错。
   </details>

3. **实践题**：如何让一个 Program 调用另一个 Program（CPI）？
   <details>
   <summary>答案</summary>

   ```rust
   use anchor_spl::token::{self, Token, Transfer};

   pub fn transfer_tokens(ctx: Context<TransferTokens>, amount: u64) -> Result<()> {
       let cpi_accounts = Transfer {
           from: ctx.accounts.from.to_account_info(),
           to: ctx.accounts.to.to_account_info(),
           authority: ctx.accounts.authority.to_account_info(),
       };
       let cpi_program = ctx.accounts.token_program.to_account_info();
       let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
       token::transfer(cpi_ctx, amount)
   }
   ```
   </details>
