import axios from 'axios';
import { Activity, ApiResponse, Feedback, Location, UserProfile } from '@/types';

// APIのベースURL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// AxiosインスタンスのセットアップAPI
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエスト前に認証トークンを設定
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 推奨活動を取得する
export const getRecommendedActivities = async (
  fatigueLevel: number,
  location: Location,
  duration: number
): Promise<Activity[]> => {
  try {
    const response = await api.get<ApiResponse<Activity[]>>('/activities/recommended', {
      params: { fatigue_level: fatigueLevel, location, duration }
    });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching recommended activities:', error);
    throw new Error('活動を取得できませんでした');
  }
};

// 活動詳細を取得する
export const getActivity = async (activityId: number): Promise<Activity> => {
  try {
    const response = await api.get<ApiResponse<Activity>>(`/activities/${activityId}`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching activity details:', error);
    throw new Error('活動詳細を取得できませんでした');
  }
};

// フィードバックを送信する
export interface FeedbackSubmit {
  activityId: number;
  rating: number;
  fatigueLevel: number;
  location: Location;
  duration: number;
  completionStatus: 'completed' | 'partial' | 'abandoned';
  comments?: string;
}

export const submitFeedback = async (feedback: FeedbackSubmit): Promise<Feedback> => {
  try {
    const response = await api.post<ApiResponse<Feedback>>('/feedback', {
      activity_id: feedback.activityId,
      rating: feedback.rating,
      fatigue_level: feedback.fatigueLevel,
      location: feedback.location,
      duration: feedback.duration,
      completion_status: feedback.completionStatus,
      comments: feedback.comments
    });
    return response.data.data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw new Error('フィードバックを送信できませんでした');
  }
};

// ユーザープロファイルを取得する
export const getUserProfile = async (): Promise<UserProfile> => {
  try {
    const response = await api.get<ApiResponse<UserProfile>>('/users/profile');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw new Error('プロファイルを取得できませんでした');
  }
};

// ユーザープロファイルを更新する
export const updateUserProfile = async (
  interests: string[],
  workStyle: string,
  restPreferences: string[]
): Promise<UserProfile> => {
  try {
    const response = await api.post<ApiResponse<UserProfile>>('/users/profile', {
      interests,
      work_style: workStyle,
      rest_preferences: restPreferences
    });
    return response.data.data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw new Error('プロファイルを更新できませんでした');
  }
};

// ログイン
export const login = async (email: string, password: string): Promise<{ token: string }> => {
  try {
    const response = await api.post<ApiResponse<{ token: string }>>('/auth/login', {
      email,
      password
    });
    return response.data.data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw new Error('ログインできませんでした');
  }
};

// サインアップ
export const signup = async (name: string, email: string, password: string): Promise<{ token: string }> => {
  try {
    const response = await api.post<ApiResponse<{ token: string }>>('/auth/signup', {
      name,
      email,
      password
    });
    return response.data.data;
  } catch (error) {
    console.error('Error signing up:', error);
    throw new Error('アカウント作成できませんでした');
  }
};
