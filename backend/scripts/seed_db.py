#!/usr/bin/env python3
"""
データベースに初期データを投入するスクリプト
"""
import json
import os
import sys
import logging
from pathlib import Path

# backendディレクトリをPythonのパスに追加
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal, engine
from app.models import Base, activity, user, feedback
from app.services import ai_service
from app.config import settings

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def init_db():
    """データベースの初期化"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("データベースを初期化しました")

def seed_activities():
    """活動データの投入"""
    db = SessionLocal()
    try:
        # 活動データのJSONファイルを読み込む
        data_path = Path(backend_dir) / "data" / "seed_activities.json"
        
        if not data_path.exists():
            logger.error(f"ファイルが見つかりません: {data_path}")
            return

        with open(data_path, "r", encoding="utf-8") as f:
            activities_data = json.load(f)
            
        activities = []
        for data in activities_data:
            # JSONデータをSQLAlchemyモデルに変換
            act = activity.Activity(
                title=data["title"],
                description=data["description"],
                category=data["category"],
                duration=data["duration"],
                locations=json.dumps(data["locations"]),
                fatigue_min=data["fatigue_min"],
                fatigue_max=data["fatigue_max"],
                steps=json.dumps(data["steps"]) if "steps" in data else None,
                benefits=json.dumps(data["benefits"]) if "benefits" in data else None,
                scientific_basis=data.get("scientific_basis")
            )
            activities.append(act)
            
        # 一括でデータベースに追加
        db.add_all(activities)
        db.commit()
        logger.info(f"{len(activities)}件の活動データを投入しました")
        
    except Exception as e:
        logger.error(f"活動データの投入中にエラーが発生しました: {str(e)}")
    finally:
        db.close()

def create_test_user():
    """テストユーザーの作成"""
    db = SessionLocal()
    try:
        # パスワードのハッシュ化（実際の実装ではPasswordHasherを使用）
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # テストユーザーデータ
        test_user = user.User(
            email="test@example.com",
            password_hash=pwd_context.hash("password123"),
            name="テストユーザー"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # ユーザープロファイルの作成
        interests = ["読書", "運動", "学習"]
        work_style = "デスクワーク中心"
        rest_preferences = ["静かに過ごす", "軽い運動"]
        
        # AI生成プロファイル（実際の実装ではGemini APIs使用）
        try:
            # Vertex AIの初期化
            ai_service.init_vertex_ai()
            
            textual_profile = "このユーザーはデスクワーク中心の仕事をしており、休憩時には静かに読書をしたり、軽い運動をすることを好みます。知的好奇心が強く、学習活動も好むため、短時間の集中的な学習活動や、リラックスしながら知識を得られる活動が向いています。"
        except Exception as e:
            logger.warning(f"AIプロファイル生成に失敗しました: {str(e)}")
            textual_profile = "このユーザーはデスクワーク中心の仕事をしており、休憩時には静かに読書をしたり、軽い運動をすることを好みます。"
        
        # ユーザープロファイルの作成
        profile = user.UserProfile(
            user_id=test_user.id,
            interests=json.dumps(interests),
            work_style=work_style,
            rest_preferences=json.dumps(rest_preferences),
            textual_profile=textual_profile
        )
        
        db.add(profile)
        db.commit()
        logger.info(f"テストユーザーとプロファイルを作成しました: ID {test_user.id}")
        
    except Exception as e:
        logger.error(f"テストユーザー作成中にエラーが発生しました: {str(e)}")
    finally:
        db.close()

def main():
    """メイン実行関数"""
    logger.info("データベースシードスクリプトを開始します...")
    init_db()
    seed_activities()
    create_test_user()
    logger.info("データベースシードが完了しました")

if __name__ == "__main__":
    main()
