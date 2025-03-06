# タイムブースト - プロジェクト詳細概要

## プロジェクトの目的と背景

「タイムブースト」は、現代社会において増加している「疲れているのに休み方が分からない」「隙間時間を有効活用したいけど何をすべきか分からない」という課題に対する具体的な解決策として開発されました。ユーザーの現在の疲労度、利用可能時間、現在地という3つの要素を考慮し、その状況に最適な活動を提案するパーソナライズアプリです。

### ターゲットユーザー
- デスクワーク中心の知識労働者
- 時間管理と効率性を重視する忙しい現代人
- 適切な休息と生産性のバランスを模索している人
- 健康的な習慣形成を目指している人

### 解決する課題
1. **休息の質の低下**: 疲労時に適切な休息方法を選択できないことによる回復効率の悪さ
2. **隙間時間の無駄**: 短い時間をどう活用すべきか決断できないことでの機会損失
3. **場所制約への対応**: 異なる環境での効果的な活動選択の難しさ
4. **個人差の考慮**: 一般的なアドバイスではなく個人に最適化された提案の不足

## システム全体像と技術詳細

### アーキテクチャ
タイムブーストは、モダンでスケーラブルなアーキテクチャを採用しています：

- **フロントエンド**: Next.js（TypeScript）を用いたシングルページアプリケーション
- **バックエンド**: FastAPI（Python）を用いたRESTful API
- **データベース**: SQLite（開発環境）/ PostgreSQL（本番環境）
- **AI/ML**: Gemini Flash 2.0 APIとTensorFlow/Scikit-learnによる機械学習機能

### 主要機能と技術的特徴

#### 1. 三軸最適化による活動提案メカニズム

- **疲労度に応じたパーソナライズ**
  - 1〜10段階の疲労度スライダーによるユーザー状態の定量化
  - 疲労レベル別に最適化された活動データベース（疲労度5以下、6-8、9-10などの区分）
  - バックエンドでの`fatigue_min`と`fatigue_max`によるフィルタリングロジック

- **時間枠に応じた活動提案**
  - 15分、30分、45分、1時間の4つの時間帯対応
  - 厳密な所要時間管理（選択時間の最大25%増しまで許容する調整機能）
  - `duration`パラメータに基づくクエリフィルタリング

- **場所を考慮した活動**
  - 5種類の場所識別（家、オフィス、カフェ、移動中、その他）
  - JSONフィールドを用いた柔軟な複数場所対応システム
  - 場所条件に基づくフィルタリングアルゴリズム

#### 2. Gemini Flash 2.0による高度なAIパーソナライゼーション

- **テキストベースのユーザープロファイリング**
  - ユーザー情報を文章形式のプロファイルとしてモデル化
  - Gemini Flash 2.0によるプロファイル生成処理（`generate_textual_profile`）
  - ユーザーの興味関心、仕事スタイル、休息の好みを統合した自然言語表現

```python
# Gemini Flash 2.0を用いたプロファイル生成の例
async def generate_textual_profile(preferences: Dict) -> str:
    model = GenerativeModel("gemini-1.5-flash")
    
    # プロンプト作成
    prompt = f"""あなたはユーザープロファイルを分析し、その人に合った活動提案をするAIです。
    
    以下のユーザー情報から、この人物がどのようなタイプで、どのような活動が向いているのかを
    200字程度でまとめてください:
    
    興味関心: {interests}
    仕事スタイル: {work_style}
    休息の好み: {rest_preferences}"""
    
    # モデルから回答を生成
    response = model.generate_content(prompt)
    return response.text
```

- **複合情報に基づくパーソナライズ**
  - ユーザープロファイル、現在状況、過去フィードバックの三要素統合
  - プロンプトエンジニアリングによる最適カテゴリ推論
  - JSON応答形式を用いた構造化データ抽出

```python
# フィードバックデータを活用したパーソナライズの例
async def personalize_activities(user_profile: str, fatigue_level: int, previous_feedbacks: List[Dict]) -> List[str]:
    model = GenerativeModel("gemini-1.5-flash")
    
    # 過去のフィードバックをプロンプトに組み込み
    feedbacks_str = ""
    for i, fb in enumerate(previous_feedbacks[:5]):
        feedbacks_str += f"活動{i+1}: {fb['activity_title']} - 評価: {fb['rating']}/10, 疲労度: {fb['fatigue_level']}/10\n"
    
    # プロンプト作成
    prompt = f"""あなたは個別化された活動提案を行うAIアシスタントです。
    
    以下のユーザープロファイルと過去のフィードバック、現在の疲労度に基づいて、
    このユーザーに最適な活動タイプを分析してください。回答は以下のJSONフォーマットで返してください:
    
    ```json
    {{
        "recommended_activity_types": ["タイプ1", "タイプ2", "タイプ3"],
        "reasoning": "推奨理由の簡潔な説明"
    }}
    ```
    
    ユーザープロファイル: {user_profile}
    
    過去のフィードバック:
    {feedbacks_str if feedbacks_str else "まだフィードバックはありません"}
    
    現在の疲労度: {fatigue_level}/10
    """
    
    # JSONレスポンスを解析して活動タイプを抽出
    response = model.generate_content(prompt)
    parsed_response = parse_json_from_response(response.text)
    return parsed_response.get("recommended_activity_types", ["relaxation", "light_exercise"])
```

- **フィードバックによる継続的学習**
  - 活動完了後の10段階評価システム
  - 完了状況追跡（完全完了、一部完了、途中中断）
  - フィードバックを基にした次回推薦の精度向上

#### 3. 科学的根拠に基づく活動データベース

- **活動データの構造**
  - 活動タイトルと説明
  - カテゴリ、所要時間、適した場所、適した疲労度範囲
  - 手順（ステップバイステップガイド）
  - 期待される効果
  - 科学的根拠（研究引用）

- **カテゴリと実装された活動例**
  - **リラックス系（30活動）**
    - マインドフルネス呼吸法（15分）
    - 5分間パワーナップ（15分）
    - 感謝日記（10分）

  - **軽い運動系（30活動）**
    - デスクストレッチング（15分）
    - 創造的思考ウォーキング（30分）
    - 階段ウォーキング（10分）

  - **デスクワーク特化型（30活動）**
    - 目の疲れ解消エクササイズ（10分）
    - デスク整理・環境最適化（15分）
    - 20-20-20ルール視覚休憩（15分）

  - **短時間集中型（30活動）**
    - 集中力回復ポモドーロ（30分）
    - マインドマッピング（20分）
    - フリーライティング（15分）

  - **場所固有活動（30活動）**
    - カフェ瞬間リフレッシュ（15分）
    - 通勤電車マインドフルネス（15分）
    - オープンオフィス集中力維持テクニック（20分）

## プロジェクト構成詳細

### バックエンド構造
```
backend/
├── app/
│   ├── api/                    # API関連
│   │   ├── deps.py             # 依存関係（認証など）
│   │   └── routes/             # エンドポイント定義
│   │       ├── activities.py   # 活動関連API
│   │       ├── auth.py         # 認証関連API
│   │       ├── feedback.py     # フィードバック関連API
│   │       └── users.py        # ユーザー関連API
│   ├── crud/                   # データベース操作
│   │   ├── activity.py         # 活動CRUD操作
│   │   ├── feedback.py         # フィードバックCRUD操作
│   │   └── user.py             # ユーザーCRUD操作
│   ├── models/                 # データベースモデル
│   │   ├── activity.py         # 活動モデル
│   │   ├── feedback.py         # フィードバックモデル
│   │   └── user.py             # ユーザー/プロファイルモデル
│   ├── schemas/                # Pydanticスキーマ
│   │   ├── activity.py         # 活動スキーマ
│   │   ├── feedback.py         # フィードバックスキーマ
│   │   └── user.py             # ユーザースキーマ
│   ├── services/               # ビジネスロジック
│   │   └── ai_service.py       # Gemini AIインテグレーション
│   ├── config.py               # 環境設定
│   ├── database.py             # DB接続設定
│   └── main.py                 # アプリケーションエントリーポイント
├── data/                       # サンプルデータ
│   └── seed_activities.json    # 初期活動データ
├── scripts/                    # ユーティリティスクリプト
│   └── seed_db.py              # DBシード処理
└── requirements.txt            # 依存関係
```

### フロントエンド構造
```
frontend/
├── src/
│   ├── app/                    # Next.jsページ
│   │   ├── layout.tsx          # 共通レイアウト
│   │   ├── page.tsx            # メインページ
│   │   ├── activities/         # 活動詳細ページ
│   │   ├── dashboard/          # ダッシュボード
│   │   ├── login/              # ログインページ
│   │   ├── profile/            # プロファイル設定
│   │   └── register/           # 登録ページ
│   ├── components/             # UIコンポーネント
│   │   ├── activities/         # 活動関連コンポーネント
│   │   ├── feedback/           # フィードバック関連
│   │   └── ui/                 # 基本UIコンポーネント
│   ├── lib/                    # ユーティリティ
│   │   └── api.ts              # API通信
│   └── types/                  # TypeScript型定義
│       └── index.ts            # 共通型定義
├── public/                     # 静的ファイル
└── package.json                # 依存関係
```

## データベース設計

### 主要テーブル構造

#### usersテーブル
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_profilesテーブル
```sql
CREATE TABLE user_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  interests TEXT, -- JSON文字列で格納
  work_style TEXT NOT NULL,
  rest_preferences TEXT, -- JSON文字列で格納
  textual_profile TEXT, -- AI生成された文章形式のプロファイル
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### activitiesテーブル
```sql
CREATE TABLE activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL, -- 'relaxation', 'light_exercise', 'desk_work', 'short_focus', 'location_specific'
  duration INTEGER NOT NULL, -- 分単位: 15, 30, 45, 60, etc.
  locations TEXT NOT NULL, -- JSONで格納: ['home', 'office', 'cafe', etc.]
  fatigue_min INTEGER NOT NULL, -- 1-10
  fatigue_max INTEGER NOT NULL, -- 1-10
  steps TEXT, -- JSONで手順を格納
  benefits TEXT, -- JSON形式で効果を格納
  image_url TEXT,
  scientific_basis TEXT, -- 科学的根拠（論文参照など）
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### feedbacksテーブル
```sql
CREATE TABLE feedbacks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  activity_id INTEGER NOT NULL,
  rating INTEGER NOT NULL, -- 1-10
  fatigue_level INTEGER NOT NULL, -- 1-10
  location TEXT NOT NULL,
  duration INTEGER NOT NULL, -- 選択した時間（分）
  completion_status TEXT NOT NULL, -- 'completed', 'partial', 'abandoned'
  comments TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (activity_id) REFERENCES activities (id)
);
```

## APIエンドポイント

### 活動関連
- `GET /api/v1/activities/` - すべての活動を取得
- `GET /api/v1/activities/recommended` - 推奨活動を取得（パラメータ: fatigue_level, location, duration）
- `GET /api/v1/activities/{activity_id}` - 特定の活動詳細を取得
- `POST /api/v1/activities/` - 新規活動を作成（管理者用）

### ユーザー関連
- `GET /api/v1/users/me` - 現在のユーザー情報を取得
- `GET /api/v1/users/profile` - ユーザープロファイルを取得
- `POST /api/v1/users/profile` - プロファイルを作成/更新

### フィードバック関連
- `POST /api/v1/feedback/` - フィードバックを送信
- `GET /api/v1/feedback/me` - ユーザーのフィードバック履歴を取得
- `GET /api/v1/feedback/summary` - フィードバックサマリーを取得

### 認証関連
- `POST /api/v1/auth/login` - ログイン処理
- `POST /api/v1/auth/signup` - ユーザー登録

## 今後の拡張計画

1. **モバイルアプリ展開**
   - ネイティブiOS/Androidアプリの開発
   - オフライン機能の強化

2. **AIパーソナライズの進化**
   - 時間帯や曜日、気象条件など外部要素の考慮
   - 生体機能リズム（サーカディアンリズム）に基づく最適化

3. **コミュニティ・社会的機能**
   - チーム向け健康管理機能
   - 専門家による活動提案システム

4. **健康データ連携**
   - ウェアラブルデバイスとの統合
   - 睡眠データや活動量を考慮した推薦

## 技術的課題と対策

1. **パーソナライズの精度向上**
   - 課題: 初期段階での推薦精度の低さ
   - 対策: 3〜4回の利用で顕著な改善が見られる学習率調整

2. **Gemini API応答速度の最適化**
   - 課題: AIモデル呼び出しによるレイテンシ
   - 対策: キャッシング戦略とバックグラウンド処理

3. **データプライバシー対応**
   - 課題: 個人の活動パターンとフィードバックの安全な管理
   - 対策: データ最小化原則とGDPR対応設計

4. **スケーラビリティ確保**
   - 課題: ユーザー数増加に伴うシステム負荷
   - 対策: クラウドサービスの段階的スケーリング計画
