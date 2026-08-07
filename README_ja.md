# Free-Telegram-Store-Bot

<!-- hy-mt2-i18n:start -->
[English](./README.md) | [中文](./README_zh-CN.md) | **日本語** | [Español](./README_es.md)
<!-- hy-mt2-i18n:end -->


このボットは100％無料で作成しました。

高度なボットカスタマイズについては、[@InDMDev](https://t.me/InDMDev)までメッセージを送ってください。  
このようなボットのさらなる情報や、より高度なボットが公開された際に最初にお知らせを受け取るには、私のチャンネル[@InDMDevBots](https://t.me/InDMDevBots)にご登録ください。  
デジタル製品販売用のTelegramボット：· Telegram上でソフトウェアライセンスキーを販売する機能 · Telegramショップ/ストアボット · 暗号通貨決済ボット · CryptoBot連携機能 · Telegram Paymentsカードによる支払い対応 · 自動的なデジタル商品配信機能 · Pythonを使ったeコマースボット · python-telegram-botストア機能 · SQLAlchemy SQLiteを利用したTelegramボット · 自前でホスト可能なデジタル商品販売ページ。  
> 
# デジタル製品ストア — Telegramボット

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-26A5E4?logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-003B57?logo=sqlite&logoColor=white)
![プラットフォーム](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-555)
[![ライセンス：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

デジタル製品（ソフトウェアのライセンスキーやダウンロード可能なファイル）を販売するためのTelegramボットです。  
顧客はカタログを閲覧し、暗号通貨やクレジットカードで内部ウォレットに資金を入金し、その残高を製品の購入に使用します。  
ライセンスキーは在庫から自動的に送信され、ファイル形式の製品はダウンロードリンクを通じて配布されます。  
Telegram内にある完全な管理パネルを使って、製品、カテゴリ、在庫、注文、トラブルシューティング、ユーザー、放送、およびストアの設定を管理できます。

**Python**、**python-telegram-bot v20**（非同期版）、および **SQLAlchemy**（デフォルトでSQLite）を使用して構築されています。

---

<img width="434" height="501" alt="image" src="https://github.com/user-attachments/assets/45c50008-6b86-4d0c-b0a9-d329b492862b" />

## 目次

# 機能概要
1. [機能](#features)
2. [テクノロジースタック](#tech-stack)
3. [プロジェクト構造](#project-structure)
4. [事前準備](#prerequisites)
5. [ステップ1 — Telegramの認証情報を取得する](#step-1--get-your-telegram-credentials)
6. [ステップ2 — リポジトリをクローンする](#step-2--clone-the-repository)
7. [ステップ3 — 仮想環境を作成する](#step-3--create-a-virtual-environment)
8. [ステップ4 — 依存関係をインストールする](#step-4--install-dependencies)
9. [ステップ5 — 環境変数を設定する](#step-5--configure-environment-variables)
10. [ステップ6 — ボットを実行する](#step-6--run-the-bot)
11. [ステップ7 — ボットの利用方法（`/start` および `/admin`）](#step-7--use-the-bot-start-and-admin)
12. [オプション — Real-time CryptoBotウェブフック](#optional--real-time-cryptobot-webhooks)
13. [オプション — ボットを24時間365日稼働させる](#optional--keep-the-bot-running-247)
14. [データベースに関する注意事項](#database-notes)
15. [トラブルシューティング](#troubleshooting)
16. [セキュリティに関する注意事項](#security-notes)

---

## 機能概要

- 🛒 カテゴリとサブカテゴリを持つ製品カタログ  
- 🔑 2種類の製品タイプ：在庫から自動で配信される**ライセンスキー**、およびリンクとして配信される**ダウンロード可能なファイル**  
- 💰 内部ウォレット — ユーザーがチャージし、その残高を購入に使用する  
- 💳 2つのチャージ方法。どちらもオプションで、設定によって個別に有効化/無効化可能：  
  - **CryptoBot** — [@CryptoBot](https://t.me/CryptoBot) を通じて任意の暗号資産で支払う  
  - **Card** — Telegram Payments を利用したTelegram内蔵のカード決済  
- 🛠 Telegram内で完結する**管理パネル**：製品、カテゴリ、在庫管理/補充、注文、紛争処理、ユーザー管理（禁止/解除）、放送機能、およびストア設定  
- ⏱ 決済確認や定期的な在庫状況の放送を行うバックグラウンドジョブ

## テクノロジースタック

| コンポーネント | バージョン |
|-----------|---------|
| Python | 3.10以上が推奨されます（3.9以上もサポートされています） |
| python-telegram-bot | 20.7 |
| SQLAlchemy | 2.0.23 |
| データベース | SQLite（デフォルト）またはPostgreSQL |

---

# 構成の仕組み：`bot.py`が唯一の連携ポイントとなっています。まずこのファイルで設定ファイル（`config/`）をチェックし、データベース（`database/`）を初期化した後、すべての`handlers/`を登録します。各ハンドラーはTelegramと通信し、`services/`（外部API）や`utils/`（キーボードや補助関数）へ呼び出しを行います。また、すべてのデータアクセスは`database/db.py`内の`get_db_session()`を経由して行われます。

---

## 前提条件

開始する前に、これらをインストールしてください：

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)  
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)  
  - **Windows**環境では、インストーラーで「Add Python to PATH」にチェックを入れてください。  
- **Telegramアカウント**

インストールされているツールを確認してください：

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

---

## ステップ1 — Telegramの認証情報を取得する

**Bot token**と**admin Telegram ID**が必要です。2つの支払い用キーは任意です。

### 1a. Bot token（必須）
1. Telegramで[@BotFather](https://t.me/BotFather)を開きます。
2. `/newbot`と送信し、表示される案内に従って操作します（名前と、`bot`で終わるユーザー名を選択します）。
3. 表示される**API token**をコピーします（例：`1234567890:ABCdef...`のような形式です）。

### 1b. 管理者用Telegram ID（必須）
1. Telegramで[@userinfobot](https://t.me/userinfobot)を開きます。
2. 任意のメッセージを送信すると、そのアカウントから数字で表された**Id**（例: `123456789`）が返信されます。
3. このIDを持つアカウントのみが `/admin` にアクセスできます。

### 1c. CryptoBot APIキー（オプション — 暗号資産によるチャージを有効にする）
1. [@CryptoBot](https://t.me/CryptoBot) を開き、**Crypto Pay** → **My Apps** へ進んでアプリを作成します。
2. **APIトークン**をコピーしてください。CryptoBotオプションを無効にするには空のままにしておきます。

### 1d. Telegram Paymentsプロバイダートークン（オプション — カードによるチャージを有効にする）
1. [@BotFather](https://t.me/BotFather) を開き、自分のボットを選択して **Payments** をタップします。
2. 決済プロバイダーを接続し、**provider token** をコピーします。カードによるチャージ機能を無効にするには空のままにしておきます。
   > カードプロバイダーの利用は地域によって異なりますので、ご自身の国でサポートされているプロバイダーを選んでください。開発中はプロバイダー提供の**TEST**トークンを使用してください。

---

## ステップ2 — リポジトリをクローンする

**Windows (PowerShell) および Linux / macOS**（コマンドは同じ）：
```bash
git clone <YOUR_REPOSITORY_URL>
cd FreeTelegramStoreBot
```
> `<YOUR_REPOSITORY_URL>` をご自身のリポジトリのクローンURLに、また `FreeTelegramStoreBot` が異なる場合はそのフォルダ名に置き換えてください。

---

## ステップ3 — 仮想環境の作成

仮想環境によって、このプロジェクトの依存関係が分離されます。

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> エクゼキューションポリシーにより起動がブロックされている場合は、一度だけ次のコマンドを実行してください：
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned.`
> （またはCMD用のアクティベータを使用しても構いません：`venv\Scripts\activate.bat`）。

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

仮想環境が有効になると、シェルプロンプトの先頭に `(venv)` が付きます。後で無効にするには、`deactivate` を実行してください。

## Step 5 — 環境変数の設定

## ステップ 4 — 依存関係のインストール

仮想環境が有効な状態で：

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

---

## ステップ5 — 環境変数の設定

例のファイルを実際の `.env` ファイルにコピーし、ご自身の値を記入してください。

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

変数の値を入力してください：

| 変数 | 必須 | 説明 |
|----------|:--------:|-------------|
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) から取得したボットトークン（ステップ1a）。 |
| `ADMIN_TELEGRAM_ID` | ✅ | ご自身のTelegramの数字形式のID（ステップ1b）。唯一の管理者アカウントです。 |
| `ADMIN_TELEGRAM_USERNAME` | ➖ | `@` を含まないご自身のユーザーネーム（一部のメッセージで使用されます）。 |
| `DATABASE_URL` | ➖ | デフォルトは `sqlite:///bot_database.db` です。PostgreSQLを使用する場合はそのURLを設定してください。 |
| `CRYPTO_BOT_API_KEY` | ➖ | CryptoBot Crypto Payのトークン（ステップ1c）。空白の場合、暗号通貨によるチャージは無効になります。 |
| `TELEGRAM_PROVIDER_TOKEN` | ➖ | Telegram Paymentsプロバイダーのトークン（ステップ1d）。空白の場合、カードによるチャージは無効になります。 |
| `PAYMENT_CURRENCY` | ➖ | カード請求時の通貨（デフォルトは `USD`）。ウォレット内の金額と一致させるため、必ずUSDで指定してください。 |

`BOT_TOKEN` と `ADMIN_TELEGRAM_ID` の少なくとも一方が設定されていない限り、ボットは起動しません。起動時にこれらの値を確認し、どちらかが欠落している場合は明確なメッセージを表示して終了します。

---

## ステップ6 — ボットの実行

初回実行時にデータベースが自動的に作成され、データも初期化されるため、別途設定コマンドはありません。

**Windows (PowerShell):**
```powershell
python bot.py
```

# 厳格な制約
1. **構造の維持**：元の Markdown のデータ構造、インデント、見出し階層、表、リンク、URL、バッジ、コードブロック、インラインコードを一切変更しないこと。
2. **選択的翻訳**：ユーザーに表示される可視的な自然言語の内容のみを翻訳すること。
3. **変更禁止**：コードタグ、キー名、変数プレースホルダー（{{var}}、${var}、%s、%d など）、コマンド例、ファイルパス、プロジェクト名、API名、パッケージ名、モデル名、識別子、コード記号を翻訳したり変更したりすることは**厳禁**です。背景情報で既に対応する訳名が示されている場合を除く。
4. 用語、スタイル、固有名詞の翻訳は、与えられた背景情報と一致させること。

次のように終わるログ行が表示されるはずです：
```
Bot started successfully!
```
このターミナルは開いたままにしてください。プロセスが実行中である限りボットも動作し続けます。停止するには**Ctrl+C**を押してください。

# 厳格な制約事項
1. **構造の維持**：元の Markdown のデータ構造、インデント、見出しの階層、表、リンク、URL、バッジ、コードブロック、インラインコードを一切変更しないこと。
2. **選択的翻訳**：ユーザーに表示される可視的な自然言語内容のみを翻訳すること。
3. **変更禁止**：コードのタグ、キー名、変数プレースホルダー（{{var}}、${var}、%s、%d など）、コマンド例、ファイルパス、プロジェクト名、API 名、パッケージ名、モデル名、識別子、コード記号を翻訳したり変更したりすることは**厳禁**です。背景情報で既に対応する訳名が示されている場合を除きます。
4. 用語、スタイル、固有名詞の翻訳は、提供された背景情報と一致させること。

## ステップ7 — ボットの利用（`/start` および `/admin`）

ボットが動作中の状態では：

1. Telegramを開き、ステップ1aで選択したユーザー名でボットを検索してください。  
2. **`/start`**を送信すると、ウェルカムメッセージとメインメニュー（Products、Top Up、Order History、Availability、Support）が表示されます。  
3. **`/admin`**を送信すると、Telegram IDが`ADMIN_TELEGRAM_ID`と一致していれば、**管理パネル**（Product Management、User Management、Order Management、Store Settings、Broadcast）が開きます。

もし `/admin` の返答がアクセス拒否と表示されたり、何の反応も示さなかったりする場合は、ご自身の `ADMIN_TELEGRAM_ID` がアカウントと一致していないことを意味します。Step 1b を再度確認し、`.env` ファイルを修正してから、ボットを再起動してください。

🎉 これで完了です——あなたのボットが稼働しました。管理者として初めて実行する典型的な流れは、`/admin` を開いて **Product Management** に進み、カテゴリを作成した後に商品を追加し、さらに **Restock Keys** を使って在庫を登録します。ユーザーとしては、`/start` を選んで **Top Up** に進みウォレットに資金を入金し、その後商品を購入します。

---

## オプション — リアルタイム CryptoBot ウェブフック

デフォルトでは、CryptoBotの支払いは約30秒ごとにポーリングを行うことで確認されます（追加設定は不要です）。**即時**に確認したい場合は、付属のwebhookサーバーをボットと一緒に実行してください。

1. webhookサーバーを起動します（別のターミナルで、同じ仮想環境を使用）。

   # Windows (PowerShell):
   ```powershell
   python webhook_server.py
   ```
   # Linux / macOS:
   ```bash
   python3 webhook_server.py
   ```
   このサーバーはポート **5000** で接続を待機しています。

2. HTTPSを通じて公開する（例：[ngrok](https://ngrok.com/) を使用）：
   ```bash
   ngrok http 5000
   ```

3. [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay → My Apps → Webhooks** に移動し、URLを次のように設定します：
   ```
   https://<your-ngrok-or-domain>/webhook/cryptobot
   ```

Windowsの場合は、`start_with_webhooks.bat`を使用してボットとウェブフックサーバーを同時に起動できます（ngrokの実行は引き続き自分で行う必要があります）。  
カード決済にはウェブフックは不要で、Telegramがボットの通常の更新ポーリングを通じて確認情報を届けます。

---

## オプション — ボットを24時間365日稼働させ続ける

### Linux (systemd)

/etc/systemd/system/digitalstore-bot.service を作成してください（パスと `User` の値は調整してください）：

```ini
[Unit]
Description: Digital Products Store Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/FreeTelegramStoreBot
ExecStart=/home/youruser/FreeTelegramStoreBot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

次に、それを有効化して起動します：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now digitalstore-bot
sudo systemctl status digitalstore-bot      # 実行中か確認する
journalctl -u digitalstore-bot -f            # ログを確認する
```

### Windows
`python bot.py`のウィンドウを開いたままにするか、バックグラウンドタスクやスケジュール済みタスク（例：タスクスケジューラ）として実行するか、または上記の手順を使ってLinuxサーバー上で動作させます。

---

## データベースに関する注意事項

- **デフォルト:** SQLiteを使用し、プロジェクトフォルダ内の`bot_database.db`に保存されます。初回実行時に自動的に作成されます。  
- **バックアップ:** `bot_database.db`ファイルをそのままコピーするだけです。  
- **リセット（すべてのデータを削除）:** ボットを停止し、`bot_database.db`を削除した後、再びボットを起動して空のデータベースを作成します。

  **Windows (PowerShell):**
  ```powershell
  Remove-Item bot_database.db
  ```
  **Linux / macOS:**
  ```bash
  rm bot_database.db
  ```
- **PostgreSQL (任意):** `DATABASE_URL` を PostgreSQL の URL に設定します。例:
  `postgresql+psycopg2://user:password@localhost:5432/digitalstore`
  (`requirements.txt` には `psycopg2-binary` ドライバーが既に含まれています)。
- **古いデータベースのアップグレード:** カテゴリーフィールドが任意になる前に作成された既存の SQLite DB を移行する場合は、1回だけ実行してください:
  `python migrations/001_make_category_id_nullable.py` (新規インストールの場合は不要です)。

---

## よくある質問

# このプロジェクトとは？
ソフトウェアのライセンスキーやアクティベーションキー、ダウンロード可能なファイルといったデジタル製品を販売するための、オープンソースで自前でホスト可能な**Telegramボット**です。Telegram内に顧客向けのショップページと完全な管理パネルが備わっており、すべてがTelegram上で利用できます。

**これを使って何を販売できますか？**
ソフトウェアのライセンスキー、ゲームキー、ギフトカードコード、電子書籍、PDF、講座、テンプレート、またはリンク経由で配信可能なあらゆるダウンロード可能なファイルなど、デジタル製品であれば何でも販売できます。

**顧客はどのように支払いますか？**
顧客はボット内にある**ウォレット**に資金を入金し、その残高を使って商品を購入します。チャージには**CryptoBot**（任意の暗号通貨）や**カード決済**（Telegram Payments）を利用できます。これらの方法はどちらも任意で、設定によって有効/無効を切り替えられます。

**配送は自動的に行われますか？**
はい。購入が確定するとすぐに在庫からライセンスキーが自動的に割り当てられ、ファイル型の商品はダウンロードリンクとして送信されるため、手動での処理は不要です。

**実行するためにコーディングの知識が必要ですか？**
いいえ。リポジトリをクローンし、`.env` ファイルに情報を記入して、1つのコマンドを実行するだけです。初回起動時にデータベースが自動的に作成されます。

# 使用しているデータベースは何ですか？
デフォルトでは設定不要の**SQLite**が使用されます。1つの環境変数を変更するだけで**PostgreSQL**に切り替えることも可能です。

**WindowsやLinuxでも動作しますか？**
はい。[セットアップガイド](#table-of-contents)には**Windows、Linux、macOS**向けの手順別コマンドが記載されており、24時間365日稼働させるための`systemd`サービスも用意されています。

**無料でオープンソースなのですか？**
はい。[MIT License](LICENSE) のもとで公開されています。

---
## トラブルシューティング

| 症状 | 修正方法 |
|---------|----------|
| `Configuration error: BOT_TOKEN is required` | `.env` ファイルが欠落しているか、`BOT_TOKEN`/`ADMIN_TELEGRAM_ID` の値が空です。ステップ5を再確認し、`.env` がプロジェクトのルートにあることを確認してください。 |
| `/admin` へのアクセスが拒否されるか応答がない | `ADMIN_TELEGRAM_ID` がご自身のアカウントと一致していません。ステップ1bで再度IDを取得し、`.env` ファイルを更新してから再起動してください。 |
| `ModuleNotFoundError` またはインポートエラー | バーチャル環境が有効でないか、依存関係がインストールされていません。ステップ3とステップ4をやり直してください。 |
| （Windows）`python` が見つからない | 「PythonをPATHに追加」にチェックを入れてPythonを再インストールするか、`py` ランチャー（`py bot.py`）を使用してください。 |
| （Windows）アクティベーションがブロックされる | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` を実行した後、再度アクティベーションしてください。 |
| カードボタンに「設定されていません」と表示される | `TELEGRAM_PROVIDER_TOKEN` の値が空または無効です。ステップ1dを参照してください。 |
| 暗号資産によるチャージが自動的に確定しない | `CRYPTO_BOT_API_KEY` を確認し、コンソールでAPIエラーがないかチェックするか、即時確定のためにウェブフックを設定してください。 |
| ターミナルを閉じるとボットが停止する | これは正常な動作です。[24時間365日稼働の方法](#optional--keep-the-bot-running-247)をご利用ください。 |


## ライセンス

[MIT License](LICENSE) のもとでリリースされています。

> ⚠️ **注意：このプログラムは合法的な目的でのみご使用ください。**
> InDMDevは、お客様が当社のプログラムを利用して行ういかなる違法な活動についても、現在も将来も一切責任を負いません。
