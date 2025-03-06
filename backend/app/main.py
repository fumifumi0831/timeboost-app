from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from . import models
from .database import engine
from .config import settings
from .services import ai_service

# APIルーターのインポート
from .api.routes import activities, users, feedback, auth

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# データベーステーブルの作成
models.Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションの初期化
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="疲れた状態でも最適な活動を提案するAIアシスタント",
    version="0.1.0",
)

# CORSミドルウェアの設定
origins = [
    "http://localhost:3000",  # Next.js開発サーバー
    "http://localhost:8000",  # バックエンド開発サーバー
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# スタートアップイベント
@app.on_event("startup")
async def startup_event():
    logger.info("Starting the application...")
    try:
        # Vertex AI / Gemini 2.0 Flash の初期化
        ai_service.init_vertex_ai()
        logger.info("Vertex AI initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {str(e)}")

# APIルートの登録
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(activities.router, prefix=f"{settings.API_V1_STR}/activities", tags=["activities"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])

@app.get("/")
async def root():
    return {"message": "タイムブースト API へようこそ！"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
