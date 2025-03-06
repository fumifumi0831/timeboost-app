# タイムブースト (TimeBoost)

疲労度、利用可能時間、現在の場所に基づいて最適な活動を提案するパーソナライズアプリ。Gemini Flash 2.0を活用した機械学習による個人最適化機能を備えています。

## 概要

タイムブーストは、ユーザーが疲れている状態でも隙間時間を有効活用できるように設計されたアプリです。ユーザーの状態（疲労度）、利用可能な時間、現在いる場所の3つの情報を基に、その時の状況に最適な活動を提案します。さらに、ユーザーからのフィードバックを学習し、提案の精度を向上させていきます。

## 主な機能

- **疲労度に応じたパーソナライズ**: 1〜10段階の疲労度に応じた活動提案
- **時間枠に応じた活動提案**: 15分、30分、45分、1時間から選択可能
- **場所を考慮した活動**: 家、オフィス、カフェなど場所に応じた活動提案
- **Gemini Flash 2.0によるAI最適化**: ユーザーの好みや過去の評価を学習
- **フィードバックシステム**: 活動後の評価を収集し、提案精度を向上

## 技術スタック

### フロントエンド
- Next.js 14 (TypeScript)
- Material-UI (MUI)
- React Context API + SWR

### バックエンド
- FastAPI (Python)
- SQLAlchemy
- SQLite (開発) / PostgreSQL (本番)

### AI/機械学習
- Gemini Flash 2.0 API
- TensorFlow/Scikit-learn

## Gemini Flash 2.0の活用

本プロジェクトでは、Google Cloudの最新モデルであるGemini Flash 2.0を活用して以下の機能を実現しています：

1. **ユーザープロファイルの生成**
   - ユーザーの興味関心、仕事スタイル、休息の好みからテキスト形式のプロファイルを生成
   - バックエンドは`ai_service.generate_textual_profile`でGemini Flash 2.0 APIを呼び出し

2. **活動カテゴリーの推奨**
   - ユーザープロファイル、現在の疲労度、場所を考慮してユーザーに最適な活動カテゴリを選定
   - `ai_service.get_recommended_categories`で実装

3. **活動のパーソナライズ**
   - ユーザーの過去のフィードバックデータを分析し、ユーザーの好みを学習
   - `ai_service.personalize_activities`でフィードバックデータに基づくパーソナライズを実現

これらの機能は全て`backend/app/services/ai_service.py`に実装されています。
    
## 開発セットアップ

### 前提条件
- Node.js 18+
- Python 3.11+
- Git
- Google Cloud APIアクセス（Gemini Flash 2.0の利用）

### インストール手順

```bash
# リポジトリのクローン
git clone https://github.com/fumifumi0831/timeboost-app.git
cd timeboost-app

# フロントエンド依存関係のインストール
cd frontend
npm install

# バックエンド依存関係のインストール
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 環境変数の設定

バックエンドのルートディレクトリに `.env` ファイルを作成し、以下の内容を設定します：

```
# 基本設定
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google Cloud / Vertex AI 設定
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
GCP_PROJECT_ID=your-gcp-project-id
```

### データベースの初期化

```bash
cd backend
python -m scripts.seed_db
```

### 開発サーバーの起動

```bash
# バックエンド開発サーバー（一つのターミナルで）
cd backend
python -m app.main

# フロントエンド開発サーバー（別のターミナルで）
cd frontend
npm run dev
```

## ディレクトリ構造

### バックエンド
```
backend/
├── app/
│   ├── api/              # API エンドポイント
│   ├── crud/             # データベース操作
│   ├── models/           # データベースモデル
│   ├── schemas/          # Pydantic スキーマ
│   ├── services/         # ビジネスロジック
│   ├── config.py         # 設定
│   ├── database.py       # DB設定
│   └── main.py           # アプリケーションエントリーポイント
├── data/                 # サンプルデータ
├── scripts/              # スクリプト
└── requirements.txt      # 依存関係
```

### フロントエンド
```
frontend/
├── src/
│   ├── app/              # Next.js ページ
│   ├── components/       # React コンポーネント
│   ├── lib/              # ユーティリティ
│   └── types/            # TypeScript 型定義
├── public/               # 静的ファイル
└── package.json          # 依存関係
```

## ライセンス

MIT
