// 場所の型定義
export type Location = 'home' | 'office' | 'cafe' | 'commuting' | 'other';

// 場所の日本語表記
export const locationLabels: Record<Location, string> = {
  home: '家',
  office: 'オフィス',
  cafe: 'カフェ',
  commuting: '移動中',
  other: 'その他'
};

// 活動カテゴリの型定義
export type ActivityCategory = 
  | 'relaxation'      // リラックス系
  | 'light_exercise'  // 軽い運動系
  | 'desk_work'       // デスクワーク特化型
  | 'short_focus'     // 短時間集中型
  | 'location_specific'; // 場所固有

// カテゴリの日本語表記
export const categoryLabels: Record<ActivityCategory, string> = {
  relaxation: 'リラックス系',
  light_exercise: '軽い運動系',
  desk_work: 'デスクワーク特化型',
  short_focus: '短時間集中型',
  location_specific: '場所固有'
};

// カテゴリのアイコン
export const categoryIcons: Record<ActivityCategory, string> = {
  relaxation: '🧘',
  light_exercise: '🤸',
  desk_work: '💻',
  short_focus: '🧠',
  location_specific: '📍'
};

// 疲労レベルの範囲
export interface FatigueRange {
  min: number;
  max: number;
}

// 活動の型定義
export interface Activity {
  id: number;
  title: string;
  description: string;
  category: ActivityCategory;
  duration: number; // 分単位
  locations: Location[];
  fatigueRange: FatigueRange;
  steps: string[];
  benefits: string[];
  imageUrl?: string;
  scientificBasis?: string;
  createdAt: string;
  updatedAt: string;
}

// 完了状態の型定義
export type CompletionStatus = 'completed' | 'partial' | 'abandoned';

// フィードバックの型定義
export interface Feedback {
  id: number;
  userId: number;
  activityId: number;
  rating: number; // 1-10
  fatigueLevel: number;
  location: Location;
  duration: number;
  completionStatus: CompletionStatus;
  comments?: string;
  createdAt: string;
}

// API通信用の型
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// エラーレスポンスの型
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// ユーザープロファイルの型
export interface UserProfile {
  id: number;
  userId: number;
  interests: string[];
  workStyle: string;
  restPreferences: string[];
  textualProfile?: string;
  createdAt: string;
  updatedAt: string;
}
