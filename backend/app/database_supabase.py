"""
Supabaseを使用したデータベース接続の設定
開発環境と本番環境の両方でSupabaseを使用する場合はこのファイルを使用します
"""
import os
from typing import Generator
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Supabase接続情報
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")  # PostgreSQL接続文字列

# SQLAlchemy設定
engine = create_engine(SUPABASE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Supabaseクライアント
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db() -> Generator:
    """データベースセッションの依存性関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase() -> Client:
    """Supabaseクライアントの依存性関数"""
    return supabase
