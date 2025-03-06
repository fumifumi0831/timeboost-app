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

## 開発セットアップ

### 前提条件
- Node.js 18+
- Python 3.11+
- Git

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

### 開発サーバーの起動

```bash
# フロントエンド開発サーバー
cd frontend
npm run dev

# バックエンド開発サーバー
cd backend
python -m app.main
```

## ライセンス

MIT