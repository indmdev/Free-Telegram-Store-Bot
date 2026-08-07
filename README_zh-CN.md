# 免费 Telegram 商店机器人

<!-- hy-mt2-i18n:start -->
[English](./README.md) | **中文** | [日本語](./README_ja.md) | [Español](./README_es.md)
<!-- hy-mt2-i18n:end -->


我让这个机器人完全免费。

如需对机器人进行高级定制，请通过 [@InDMDev](https://t.me/InDMDev) 联系我。
如需更多类似机器人，以及想第一时间获知我发布的新高级机器人信息，请加入我的频道：[@InDMDevBots](https://t.me/InDMDevBots)
用于销售数字产品的 Telegram 机器人：· 在 Telegram 上出售软件许可证密钥 · Telegram 商店/店铺机器人 · 加密货币支付机器人 · CryptoBot 集成功能 · Telegram Payments 卡支付功能 · 自动化数字产品交付 · Python 电商机器人 · python-telegram-bot 商店系统 · SQLAlchemy SQLite 版 Telegram 机器人 · 自主托管的数字商品销售页面。
>
# 数字产品商店 — Telegram 机器人

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-26A5E4?logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-003B57?logo=sqlite&logoColor=white)
![平台](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-555)
[![许可证：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个用于销售数字产品（软件许可证密钥及可下载文件）的 Telegram 机器人。客户可以浏览商品目录，使用加密货币或银行卡为内部钱包充值，然后使用该余额购买产品。许可证密钥会从库存中自动发放；文件类产品则通过下载链接提供。完整的 Telegram 内置管理面板可用于管理产品、分类、库存、订单、纠纷处理、用户信息、广播内容以及店铺设置。

该项目使用 **Python**、**python-telegram-bot v20**（异步版本）以及 **SQLAlchemy**（默认使用 SQLite）构建。

---

<img width="434" height="501" alt="图片" src="https://github.com/user-attachments/assets/45c50008-6b86-4d0c-b0a9-d329b492862b" />

## 目录

1. [功能特性](#features)
2. [技术栈](#tech-stack)
3. [项目结构](#project-structure)
4. [前置条件](#prerequisites)
5. [步骤 1 — 获取 Telegram 凭证](#step-1--get-your-telegram-credentials)
6. [步骤 2 — 克隆仓库](#step-2--clone-the-repository)
7. [步骤 3 — 创建虚拟环境](#step-3--create-a-virtual-environment)
8. [步骤 4 — 安装依赖项](#step-4--install-dependencies)
9. [步骤 5 — 配置环境变量](#step-5--configure-environment-variables)
10. [步骤 6 — 运行机器人](#step-6--run-the-bot)
11. [步骤 7 — 使用机器人（/start 和 /admin）](#step-7--use-the-bot-start-and-admin)
12. [可选功能 — 实时 CryptoBot Webhook](#optional--real-time-cryptobot-webhooks)
13. [可选功能 — 实现机器人 7×24 小时运行](#optional--keep-the-bot-running-247)
14. [数据库相关说明](#database-notes)
15. [故障排除](#troubleshooting)
16. [安全注意事项](#security-notes)

## 功能特性

- 🛒 带有分类和子分类的产品目录
- 🔑 两种产品类型：**许可证密钥**（直接从库存自动发放）以及**可下载文件**（以链接形式提供）
- 💰 内部钱包——用户先充值，再用余额进行购买
- 💳 两种充值方式，均为可选选项，且可通过配置独立开启或关闭：

## 功能特性

- 🛒 带有分类和子分类的产品目录  
- 🔑 两种产品类型：**许可证密钥**（直接从库存自动发放）以及**可下载文件**（以链接形式提供）  
- 💰 内部钱包——用户充值后可用余额进行购买  
- 💳 两种充值方式，均为可选且可通过配置独立开启：  
  - **CryptoBot**——通过[@CryptoBot](https://t.me/CryptoBot)使用任何加密货币支付  
  - **卡片**——通过 Telegram Payments 实现 Telegram 内置的卡片支付  
- 🛠 完整的 Telegram 内置**管理面板**：涵盖产品管理、分类管理、库存/补货、订单处理、纠纷处理、用户管理（封禁/解封）、广播功能以及店铺设置  
- ⏱ 用于支付验证及定期发布可用性信息的后台任务

## 技术栈

| 组件 | 版本 |
|-----------|---------|
| Python | 建议使用 3.10+（支持 3.9+） |
| python-telegram-bot | 20.7 |
| SQLAlchemy | 2.0.23 |
| 数据库 | 默认为 SQLite，也可选用 PostgreSQL |

# 先决条件

# 系统架构说明：`bot.py` 是整个系统的核心协调节点——它首先验证配置文件（位于 `config/` 目录），接着初始化数据库（位于 `database/` 目录），随后注册所有的处理函数。这些处理函数负责与 Telegram 进行交互，并调用 `services/` 目录中的外部 API 以及 `utils/` 目录中的功能模块（如键盘设计及辅助工具）；所有数据访问操作均通过 `database/db.py` 文件中的 `get_db_session()` 函数来完成。

# 先决条件

## 先决条件

在开始之前，请先安装这些工具：

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)  
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)  
  - 在**Windows**系统上，安装程序中请勾选**“Add Python to PATH”**。  
- 一个**Telegram账号**

验证你的工具已安装：

**Windows (PowerShell):**
```powershell
git --version
python --version
```

**Linux / macOS:**
```bash
git --version
python3 --version
```

## 第1步 — 获取你的 Telegram 凭证

你需要一个**机器人令牌**以及你的**管理员 Telegram ID**，这两个支付密钥则是可选的。

### 1a. 机器人令牌（必需）
1. 在 Telegram 中打开 [@BotFather](https://t.me/BotFather)。
2. 发送 `/newbot` 并按照提示操作（选择名称以及以 `bot` 结尾的用户名）。
3. 复制它给出的**API 令牌**（看起来像 `1234567890:ABCdef...`）。

## 第1步 — 获取你的 Telegram 凭证

你需要一个**机器人令牌**以及你的**管理员 Telegram ID**。这两个支付密钥则是可选的。

### 1a. Bot token（必需）
1. 在 Telegram 中打开 [@BotFather](https://t.me/BotFather)。
2. 发送 `/newbot` 并按照提示操作（选择名称以及以 `bot` 结尾的用户名）。
3. 复制它给出的**API token**（格式类似 `1234567890:ABCdef...`）。

### 1b. 您的管理员 Telegram ID（必需）
1. 在 Telegram 中打开 [@userinfobot](https://t.me/userinfobot)。
2. 发送任意消息，它会回复您的数字**ID**（例如 `123456789`）。
3. 只有该账户拥有访问 `/admin` 的权限。

### 1c. CryptoBot API 密钥（可选——支持加密货币充值）
1. 打开 [@CryptoBot](https://t.me/CryptoBot) → 选择 **Crypto Pay** → **My Apps** → 创建一个应用。
2. 复制对应的 **API token**。若留空则可禁用 CryptoBot 功能。

### 1d. Telegram Payments 提供商令牌（可选——用于卡片充值）
1. 打开 [@BotFather](https://t.me/BotFather)，选择你的机器人，然后进入 **Payments** 页面。
2. 连接一个支付提供商并复制 **provider token**。若要禁用卡片充值功能，则将其留空。
   > 卡片支付提供商的服务支持情况因地区而异，请选择你所在国家/地区支持的提供商。在开发阶段可使用该提供商的 **TEST** 令牌。

## 第3步 — 创建虚拟环境

## 第 2 步 — 克隆仓库

**Windows (PowerShell) 和 Linux / macOS**（命令相同）：
```bash
git clone <YOUR_REPOSITORY_URL>
cd FreeTelegramStoreBot
```
> 请将 `<YOUR_REPOSITORY_URL>` 替换为您的仓库克隆地址，如果文件夹名称不同，则将 `FreeTelegramStoreBot` 替换为实际文件夹名。

## 第 2 步 — 克隆仓库

## 第3步 — 创建虚拟环境

虚拟环境能够将此项目的依赖项隔离开来。

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> 如果执行策略阻止了激活操作，需先运行一次：
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned.`
> （或者使用 CMD 激活脚本：`venv\Scripts\activate.bat`）。

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

当虚拟环境处于激活状态时，您的命令行提示符前会显示 `(venv)`。若要退出该状态，请运行 `deactivate` 命令。

## 第 5 步 — 配置环境变量

## 第 4 步 — 安装依赖项

在虚拟环境已激活的状态下：

**Windows (PowerShell):**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

| 变量 | 是否必填 | 描述 |

## 第 5 步 — 配置环境变量

将示例文件复制为真实的 `.env` 文件，然后填入您自己的数值。

**Windows (PowerShell):**
```powershell
Copy-Item.env.example.env
notepad.env
```

**Linux / macOS:**
```bash
cp.env.example.env
nano.env
```

填写这些变量值：

| 变量 | 是否必填 | 描述 |
|----------|:--------:|-------------|
| `BOT_TOKEN` | ✅ | 来自[@BotFather](https://t.me/BotFather)的机器人令牌（步骤1a）。 |
| `ADMIN_TELEGRAM_ID` | ✅ | 您的Telegram数字ID（步骤1b），即唯一的管理员账号。 |
| `ADMIN_TELEGRAM_USERNAME` | ➖ | 不带`@`的前缀的用户名（用于某些消息）。 |
| `DATABASE_URL` | ➖ | 默认值为`sqlite:///bot_database.db`。如需使用Postgres，则可设置PostgreSQL地址。 |
| `CRYPTO_BOT_API_KEY` | ➖ | CryptoBot加密支付令牌（步骤1c）。留空则禁用加密充值功能。 |
| `TELEGRAM_PROVIDER_TOKEN` | ➖ | Telegram Payments服务提供商令牌（步骤1d）。留空则禁用卡片充值功能。 |
| `PAYMENT_CURRENCY` | ➖ | 卡片账单的货币类型（默认为`USD`）。必须为美元，以便与钱包金额保持一致。 |

在至少设置了 `BOT_TOKEN` 和 `ADMIN_TELEGRAM_ID` 之后，机器人**才会启动**——它在启动时会验证这些参数，若缺少任意一个就会输出明确的提示信息并退出。

## 第 6 步 — 运行机器人

首次运行时会自动创建数据库并填充初始数据——无需额外的设置命令。

**Windows（PowerShell）：**
```powershell
python bot.py
```

**Linux / macOS：**
```bash
python3 bot.py
```

您应该会看到以以下内容结尾的日志行：
```
Bot started successfully!
```

## 第 6 步 — 运行机器人

首次运行时会自动创建数据库并填充初始数据——无需额外的设置命令。

**Windows (PowerShell):**
```powershell
python bot.py
```

# Linux / macOS：
```bash
python3 bot.py
```

您应该会看到以以下内容结尾的日志行：
```
Bot started successfully!
```
请保持此终端窗口打开——只要进程在运行，机器人就会持续工作。按 **Ctrl+C** 即可停止它。

## 第 7 步 — 使用机器人（`/start` 和 `/admin`）

## 第 7 步 — 使用机器人（`/start` 和 `/admin`）

在机器人运行时：

1. 打开 Telegram，根据步骤 1a 中选择的用户名查找您的机器人。
2. 发送 **`/start`** — 您将看到欢迎消息以及主菜单（产品、充值、订单历史、库存状态、支持服务）。
3. 发送 **`/admin`** — 如果您的 Telegram ID 与 `ADMIN_TELEGRAM_ID` 匹配，就会打开**管理员面板**（产品管理、用户管理、订单管理、店铺设置、广播功能）。

如果点击 `/admin` 后出现“访问被拒绝”的提示或没有任何反应，那说明您的 `ADMIN_TELEGRAM_ID` 与账号不匹配——请重新检查第 1b 步的内容，修正 `.env` 文件，然后重启机器人。

🎉 完成！您的机器人现已正式上线。作为管理员首次使用的典型操作流程为：打开 `/admin` → 进入**产品管理** → 创建分类，接着创建产品，最后点击**补货密钥**来添加库存。作为普通用户，则需先执行 `/start` → 选择**充值**为钱包充值，之后再购买商品。

# 可选——Real-time CryptoBot Webhook 功能

## 可选——实时 CryptoBot Webhook

默认情况下，CryptoBot 的支付通过每约 30 秒轮询一次的方式来确认（无需额外设置）。若需实现**即时**确认，则需在机器人旁边运行附带的 webhook 服务器。

1. 启动 webhook 服务器（使用单独的终端，保持相同的虚拟环境）：

   # Windows（PowerShell）：
   ```powershell
   python webhook_server.py
   ```
   # Linux / macOS：
   ```bash
   python3 webhook_server.py
   ```
   它会在**5000**端口上监听请求。

2. 通过 HTTPS 公开该接口（例如使用 [ngrok](https://ngrok.com/)）：
   ```bash
   ngrok http 5000
   ```

3. 在 [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay → My Apps → Webhooks** 中，将 URL 设置为：
   ```
   https://<your-ngrok-or-domain>/webhook/cryptobot
   ```

在 Windows 系统上，你可以使用 `start_with_webhooks.bat` 同时启动机器人和 webhook 服务器（仍需自行运行 ngrok）。  
卡支付无需 webhook——Telegram 会通过机器人的常规更新轮询机制来发送确认信息。

## 可选——让机器人全天候运行

## 可选——让机器人全天候运行

### Linux（systemd）

创建 `/etc/systemd/system/digitalstore-bot.service` 文件（请调整路径和 `User` 参数）：

```ini
[Unit]
Description: 数字产品商店 Telegram 机器人
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/FreeTelegramStoreBot
ExecStart=/home/你的用户名/FreeTelegramStoreBot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

接着启用并启动它：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now digitalstore-bot
sudo systemctl status digitalstore-bot      # 检查是否正在运行
journalctl -u digitalstore-bot -f            # 查看日志动态更新
```

### Windows
可以让 `python bot.py` 的窗口保持打开状态，或者将其作为后台任务/计划任务运行（例如任务计划程序），也可以按照上述步骤在 Linux 服务器上托管它。

## 数据库说明

- **默认设置：** 使用 SQLite，数据存储在项目文件夹中的 `bot_database.db` 文件中，首次运行时会自动创建。
- **备份：** 直接复制 `bot_database.db` 文件即可。
- **重置（删除所有数据）：** 先停止机器人，删除 `bot_database.db` 文件，然后再启动机器人以重新生成空数据库。

  **Windows（PowerShell）：**
  ```powershell
  Remove-Item bot_database.db
  ```

## 数据库说明

- **默认值：** SQLite，存储在项目文件夹中的 `bot_database.db` 文件里。首次运行时会自动创建。
- **备份：** 只需复制 `bot_database.db` 文件即可。
- **重置（删除所有数据）：** 停止该机器人，删除 `bot_database.db` 文件，然后重新启动机器人以生成一个空的数据库。

  **Windows (PowerShell):**
  ```powershell
  Remove-Item bot_database.db
  ```
  **Linux / macOS:**
  ```bash
  rm bot_database.db
  ```
- **PostgreSQL (可选):** 将 `DATABASE_URL` 设置为 PostgreSQL 的连接地址，例如：
  `postgresql+psycopg2://user:password@localhost:5432/digitalstore`
  （`psycopg2-binary` 驱动程序已包含在 `requirements.txt` 中）。
- **升级旧数据库:** 如果你要迁移在类别字段变为可选之前创建的现有 SQLite 数据库，请运行一次以下命令：
  `python migrations/001_make_category_id_nullable.py`（全新安装则无需此操作）。

## 常见问题

**这个项目是什么？**
这是一个开源的、可自托管的**用于销售数字产品的 Telegram 机器人**——支持销售软件许可证/激活密钥以及可下载文件——它拥有面向客户的店铺界面和功能完备的管理员面板，所有功能均在 Telegram 内部实现。

**我可以用它卖什么？**

## 常见问题

**这个项目是什么？**
这是一个开源的、可自行托管的**用于销售数字产品的 Telegram 机器人**——支持销售软件许可/激活密钥以及各类可下载文件——它拥有面向用户的商店界面和功能完备的管理面板，所有功能均在 Telegram 内部实现。

**可以用它销售什么？**
任何数字产品：软件许可证密钥、游戏密钥、礼品卡代码、电子书、PDF 文件、课程、模板，或是通过链接提供的任何可下载文件。

**客户如何付款？**
客户会先往机器人内的**钱包**充值，再用余额进行购买。充值支持通过**CryptoBot**（任意加密货币）以及**卡支付**（Telegram Payments）两种方式完成，这两种方式均为可选，可通过配置开启或关闭。

**商品交付是自动的吗？**
是的。一旦订单确认，许可证密钥会自动从您的库存中分配；而文件类商品则会以下载链接的形式发送，无需人工处理发货流程。

**运行它需要会编程吗？**
不需要。只需克隆仓库，填写 `.env` 文件，然后运行一条命令即可。首次启动时会自动创建数据库。

**它使用哪种数据库？**
默认为 **SQLite**（无需任何配置）。只需修改一个环境变量即可切换为 **PostgreSQL**。

**它在 Windows 和 Linux 上能运行吗？**
可以——[安装指南](#table-of-contents) 中提供了针对 **Windows、Linux 和 macOS** 的分步操作指令，同时还包含用于实现全天候运行的 `systemd` 服务配置。

**它是免费且开源的吗？**
是的——采用 [MIT 许可证](LICENSE) 发布。

---
## 故障排除

| 症状 | 解决方法 |
|---------|-----------|
| `Configuration error: BOT_TOKEN is required` | `.env` 文件缺失，或 `BOT_TOKEN`/`ADMIN_TELEGRAM_ID` 的值为空。请重新检查第5步，并确认 `.env` 文件位于项目根目录中。 |
| 访问 `/admin` 被拒绝或无响应 | `ADMIN_TELEGRAM_ID` 与您的账户不匹配。请重新获取该编号（第1b步），更新 `.env` 文件，然后重启程序。 |
| `ModuleNotFoundError` / 导入错误 | 虚拟环境未激活或依赖项未安装。请重新执行第3步和第4步。 |
| （Windows系统）找不到 `python` | 请重新安装Python时勾选“将Python添加到PATH”，或使用 `py` 启动器（`py bot.py`）。 |
| （Windows系统）激活被阻止 | 执行 `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`，之后再尝试激活。 |
| 卡片按钮显示“未配置” | `TELEGRAM_PROVIDER_TOKEN` 的值为空或无效——请参考第1d步。 |
| 加密充值无法自动确认 | 请核实 `CRYPTO_BOT_API_KEY` 的值，查看控制台中的API错误信息，或设置Webhook以实现即时确认。 |
| 关闭终端后机器人停止运行 | 这是正常现象——请使用[24/7全天候运行方案](#optional--keep-the-bot-running-247)。 |


## 许可证

本程序依据 [MIT License](LICENSE) 发布。

> ⚠️ **注意：请仅将本程序用于合法用途。**
> InDMDev 对您使用我们的任何程序所从事的任何非法行为概不负责，亦未来得及承担此类责任。
