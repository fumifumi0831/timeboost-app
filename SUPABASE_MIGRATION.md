# Supabase移行ガイド

このドキュメントでは、タイムブーストアプリをSupabaseに移行する手順を説明します。

## 1. Supabaseセットアップ

### 1.1 Supabaseプロジェクト作成

1. [Supabase](https://supabase.com/) にアクセスし、アカウントを作成またはログインします。
2. 新しいプロジェクトを作成します。
3. プロジェクト作成時に設定したデータベースパスワードを安全に保管してください。

### 1.2 必要な環境変数の取得

Supabaseプロジェクトのダッシュボードから以下の情報を取得します：

1. **Project URL**: プロジェクト設定の「API」タブから `Project URL` を取得
2. **API Key**: プロジェクト設定の「API」タブから `anon` (public) キーを取得
3. **Database Connection String**: プロジェクト設定の「データベース」タブから接続文字列を取得

## 2. データベーススキーマ設定

Supabaseでのデータベーススキーマ設定は、SQLエディタまたはマイグレーションスクリプトを使用して行います。

### 2.1 テーブル作成（SQLエディタ使用）

Supabaseダッシュボードの「SQLエディタ」を開き、以下のSQLを実行してテーブルを作成します：

```sql
-- プロファイルテーブル（ユーザー拡張情報用）
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT,
  interests JSONB,
  work_style TEXT,
  rest_preferences JSONB,
  textual_profile TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- アクティビティテーブル
CREATE TABLE activities (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  duration INTEGER NOT NULL,
  locations JSONB NOT NULL,
  fatigue_min INTEGER NOT NULL,
  fatigue_max INTEGER NOT NULL,
  steps JSONB,
  benefits JSONB,
  image_url TEXT,
  scientific_basis TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- フィードバックテーブル
CREATE TABLE feedbacks (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL,
  fatigue_level INTEGER NOT NULL,
  location TEXT NOT NULL,
  duration INTEGER NOT NULL,
  completion_status TEXT NOT NULL,
  comments TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (RLS) ポリシーの設定
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;

-- プロファイルのRLSポリシー
CREATE POLICY "プロファイルは所有者のみアクセス可" 
  ON profiles FOR ALL USING (auth.uid() = id);

-- フィードバックのRLSポリシー
CREATE POLICY "フィードバックは所有者のみアクセス可" 
  ON feedbacks FOR ALL USING (auth.uid() = user_id);

-- アクティビティは全ユーザーから読み取り可能
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "アクティビティは全員が読み取り可能" 
  ON activities FOR SELECT USING (true);

-- インデックス作成
CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX idx_feedbacks_activity_id ON feedbacks(activity_id);
CREATE INDEX idx_activities_category ON activities(category);
```

### 2.2 初期データの投入

サンプルの活動データをSupabaseに投入するためのスクリプトを作成します：

```python
# backend/scripts/seed_supabase.py
import json
import os
import sys
from pathlib import Path
from supabase import create_client

# Supabase接続情報
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    sys.exit(1)

# Supabaseクライアント初期化
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# データディレクトリパス
backend_dir = Path(__file__).resolve().parent.parent
data_path = backend_dir / "data" / "seed_activities.json"

# 活動データの読み込み
if not data_path.exists():
    print(f"Error: File not found: {data_path}")
    sys.exit(1)

with open(data_path, "r", encoding="utf-8") as f:
    activities = json.load(f)

# データの投入
for activity in activities:
    # データベースに合わせてデータ形式を整形
    activity_data = {
        "title": activity["title"],
        "description": activity["description"],
        "category": activity["category"],
        "duration": activity["duration"],
        "locations": activity["locations"],  # JSONBフィールドなのでリストのままOK
        "fatigue_min": activity["fatigue_min"],
        "fatigue_max": activity["fatigue_max"],
        "steps": activity.get("steps"),
        "benefits": activity.get("benefits"),
        "scientific_basis": activity.get("scientific_basis")
    }
    
    # Supabaseにデータ挿入
    response = supabase.table("activities").insert(activity_data).execute()
    
    if hasattr(response, 'error') and response.error:
        print(f"Error inserting activity: {response.error}")
    else:
        print(f"Inserted: {activity['title']}")

print("Data seeding completed!")
```

## 3. 環境変数の設定

### 3.1 開発環境の設定

開発環境で使用する `.env` ファイルを作成し、以下の環境変数を設定します：

```
# Supabase接続情報
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres:your-db-password@your-project-id.supabase.co:5432/postgres

# Google Cloud / Vertex AI設定
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
GCP_PROJECT_ID=your-gcp-project-id

# アプリ設定
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3.2 本番環境の設定

本番環境では、環境変数を直接設定するか、アプリケーションのデプロイ先（Vercel、Heroku、Railway等）の環境変数設定を使用します。

## 4. アプリケーションの実行

### 4.1 SQLiteからSupabaseへの切り替え

Supabaseを使用するには、以下のファイルを置き換えるだけです：

1. `app.database.py` → `app.database_supabase.py`
2. `app.api.deps.py` → `app.api.deps_supabase.py`
3. `app.api.routes.auth.py` → `app.api.routes.auth_supabase.py`
4. `app.main.py` → `app.main_supabase.py`

または、開発環境と本番環境の両方で一貫してSupabaseを使用する場合は、直接元のファイルを更新することもできます。

### 4.2 開発サーバーの起動

Supabaseを使用して開発サーバーを起動するには：

```bash
cd backend
python -m app.main_supabase  # Supabase版を使用
```

## 5. フロントエンドの更新

フロントエンドの API 接続を更新するには、`frontend/src/lib/api.ts` ファイルを編集して、認証ロジックをSupabaseクライアントに置き換えます。

必要に応じて、Supabaseの公式クライアントライブラリを利用することも検討してください：

```bash
cd frontend
npm install @supabase/supabase-js
```

## 6. 開発環境と本番環境の統一

開発環境と本番環境の両方でSupabaseを使用することには、以下のメリットがあります：

1. **環境の一貫性**: 開発環境と本番環境の違いによるバグを防止できます
2. **コード簡素化**: 環境に応じた条件分岐が不要になります
3. **データの共有**: 開発チーム間でのデータ共有が容易になります
4. **認証の一元管理**: Supabaseの認証機能を一貫して利用できます

一方で、ローカルのSQLiteは依存関係が少なく、ネットワーク接続なしに動作するため、オフライン開発には有利です。

## 7. PostgreSQL vs Supabaseの比較

### PostgreSQLの利点
- フルコントロール
- カスタマイズの自由度が高い
- コスト効率（自己ホスティングの場合）

### Supabaseの利点
- 認証機能の統合
- リアルタイム機能
- ストレージ
- データベースGUI
- スケーラビリティ
- 管理コスト削減

タイムブーストのようなパーソナライズアプリでは、ユーザー管理、データ保管、将来的なリアルタイム機能の導入などを考慮すると、Supabaseの利点が大きいと言えるでしょう。
