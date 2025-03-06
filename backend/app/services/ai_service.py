from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from typing import Dict, List
import json
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def init_vertex_ai():
    """Vertex AIの初期化"""
    try:
        aiplatform.init(project=settings.GCP_PROJECT_ID)
        logger.info(f"Vertex AI initialized with project: {settings.GCP_PROJECT_ID}")
    except Exception as e:
        logger.error(f"Error initializing Vertex AI: {str(e)}")
        raise

async def generate_textual_profile(preferences: Dict) -> str:
    """
    ユーザーの好みに基づいて文章形式のプロファイルを生成
    """
    try:
        # 入力情報の整形
        interests = ", ".join(preferences.get("interests", []))
        work_style = preferences.get("work_style", "")
        rest_preferences = ", ".join(preferences.get("rest_preferences", []))
        
        # Gemini 2.0 Flash モデルのセットアップ
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
    except Exception as e:
        logger.error(f"Error generating profile: {str(e)}")
        return "プロファイル生成中にエラーが発生しました。しばらく経ってからお試しください。"

async def get_recommended_categories(
    textual_profile: str,
    fatigue_level: int,
    location: str
) -> List[str]:
    """
    ユーザープロファイルと状況に基づいて推奨カテゴリを取得
    """
    try:
        # Gemini 2.0 Flash モデルのセットアップ
        model = GenerativeModel("gemini-1.5-flash")
        
        # プロンプト作成
        prompt = f"""あなたは活動提案カテゴリを生成するAIです。
        
        以下のユーザープロファイルと状況から、最適な活動カテゴリを3つ選択してください。
        カテゴリ名のみをカンマ区切りでリスト化してください。
        
        ユーザープロファイル: {textual_profile}
        現在の疲労度: {fatigue_level}/10
        現在の場所: {location}
        
        選択可能なカテゴリ:
        - relaxation（リラックス系）
        - light_exercise（軽い運動系）
        - desk_work（デスクワーク特化型活動）
        - short_focus（短時間集中型の生産活動）
        - location_specific（場所固有の活動）"""
        
        # モデルから回答を生成
        response = model.generate_content(prompt)
        
        # カンマ区切りの文字列をリストに変換
        categories = [cat.strip() for cat in response.text.split(',')]
        
        # カテゴリ名が正しいかチェック
        valid_categories = ['relaxation', 'light_exercise', 'desk_work', 'short_focus', 'location_specific']
        return [cat for cat in categories if cat in valid_categories]
    except Exception as e:
        logger.error(f"Error generating categories: {str(e)}")
        # エラー時はデフォルトカテゴリを返す
        return ['relaxation', 'light_exercise', 'desk_work']

async def personalize_activities(user_profile: str, fatigue_level: int, previous_feedbacks: List[Dict]) -> List[str]:
    """
    ユーザーの過去のフィードバックを考慮して活動をパーソナライズ
    """
    try:
        # Gemini 2.0 Flash モデルのセットアップ
        model = GenerativeModel("gemini-1.5-flash")
        
        # 過去のフィードバックを文字列化
        feedbacks_str = ""
        if previous_feedbacks:
            for i, fb in enumerate(previous_feedbacks[:5]):  # 最新5件まで
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
        
        # モデルから回答を生成
        response = model.generate_content(prompt)
        
        # JSONを抽出して解析
        try:
            json_str = response.text
            # JSONブロックを抽出
            if "```json" in json_str and "```" in json_str.split("```json")[1]:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str and "```" in json_str.split("```")[1]:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            result = json.loads(json_str)
            return result.get("recommended_activity_types", ["relaxation", "light_exercise"])
        except Exception as json_err:
            logger.error(f"Error parsing JSON from model response: {str(json_err)}")
            return ["relaxation", "light_exercise"]
            
    except Exception as e:
        logger.error(f"Error personalizing activities: {str(e)}")
        return ["relaxation", "light_exercise"]
