'use client';

import { useState } from 'react';
import Link from 'next/link';

type Location = 'home' | 'office' | 'cafe' | 'commuting' | 'other';

export default function Home() {
  const [fatigueLevel, setFatigueLevel] = useState<number>(5);
  const [duration, setDuration] = useState<number>(30);
  const [location, setLocation] = useState<Location>('office');
  const [showResults, setShowResults] = useState<boolean>(false);

  // ロケーションのラベル
  const locationLabels: Record<Location, string> = {
    home: '家',
    office: 'オフィス',
    cafe: 'カフェ',
    commuting: '移動中',
    other: 'その他'
  };

  // 活動を検索する関数
  const handleFindActivities = () => {
    // 実際にはAPIを呼び出す
    // 今回はモックとして結果表示に切り替え
    setShowResults(true);
  };

  // 戻るボタンのハンドラ
  const handleBack = () => {
    setShowResults(false);
  };

  return (
    <div className="container">
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-primary-color mb-2">タイムブースト</h1>
        <p className="text-gray-600">疲れていても、隙間時間を有効活用</p>
      </header>

      {!showResults ? (
        <div className="card">
          <div className="mb-8">
            <div className="flex items-center mb-2">
              <span className="text-primary-color text-2xl mr-2">⚡</span>
              <h2 className="text-xl font-semibold">今の疲労度は？</h2>
            </div>
            
            <input
              type="range"
              min="1"
              max="10"
              value={fatigueLevel}
              onChange={(e) => setFatigueLevel(parseInt(e.target.value))}
              className="slider"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>元気</span>
              <span>普通</span>
              <span>疲れている</span>
            </div>
            <div className="text-center mt-2">
              <span className="font-semibold text-primary-color">{fatigueLevel}</span>
              <span>/10</span>
            </div>
          </div>
          
          <div className="mb-8">
            <div className="flex items-center mb-2">
              <span className="text-primary-color text-2xl mr-2">⏱️</span>
              <h2 className="text-xl font-semibold">使える時間は？</h2>
            </div>
            
            <div className="grid grid-cols-4 gap-3">
              {[15, 30, 45, 60].map((time) => (
                <button
                  key={time}
                  className={`p-3 rounded-lg border-2 font-semibold transition-all ${
                    duration === time
                      ? 'bg-primary-color text-white border-primary-color'
                      : 'bg-white border-gray-200 text-gray-700'
                  }`}
                  onClick={() => setDuration(time)}
                >
                  {time === 60 ? '1時間' : `${time}分`}
                </button>
              ))}
            </div>
          </div>
          
          <div className="mb-8">
            <div className="flex items-center mb-2">
              <span className="text-primary-color text-2xl mr-2">📍</span>
              <h2 className="text-xl font-semibold">今いる場所は？</h2>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {Object.entries(locationLabels).map(([key, label]) => (
                <button
                  key={key}
                  className={`px-4 py-2 rounded-full text-sm transition-all ${
                    location === key
                      ? 'bg-primary-color text-white'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                  onClick={() => setLocation(key as Location)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          
          <button
            className="action-button"
            onClick={handleFindActivities}
          >
            活動を探す
          </button>
        </div>
      ) : (
        <div>
          <button
            className="flex items-center text-gray-600 mb-4 hover:text-primary-color transition-colors"
            onClick={handleBack}
          >
            <span className="mr-1">←</span>
            <span>条件を変更する</span>
          </button>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <div className="bg-primary-light text-primary-color px-3 py-1 rounded-full text-sm flex items-center">
              <span className="mr-1">⚡</span>
              <span>疲労度: {fatigueLevel}/10</span>
            </div>
            <div className="bg-primary-light text-primary-color px-3 py-1 rounded-full text-sm flex items-center">
              <span className="mr-1">⏱️</span>
              <span>{duration}分</span>
            </div>
            <div className="bg-primary-light text-primary-color px-3 py-1 rounded-full text-sm flex items-center">
              <span className="mr-1">📍</span>
              <span>{locationLabels[location]}</span>
            </div>
          </div>
          
          {/* 活動カードサンプル */}
          <div className="card cursor-pointer hover:-translate-y-1 transition-transform border-l-4 border-primary-color">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">デスクストレッチング</h3>
              <div className="bg-primary-light text-primary-color px-2 py-1 rounded-full text-xs flex items-center">
                <span className="mr-1">🤸</span>
                <span>軽い運動</span>
              </div>
            </div>
            <div className="text-sm text-gray-600 flex items-center mb-2">
              <span className="mr-1">⏱️</span>
              <span>所要時間: 約15分</span>
            </div>
            <p className="text-gray-700 mb-4 text-sm">
              デスクに座ったまま行える全身ストレッチです。肩こりや腰痛の軽減、血行促進に効果的です。
            </p>
            <div className="flex justify-between items-center text-xs">
              <div className="text-gray-500">適した場所: オフィス、家</div>
              <div className="text-primary-color">詳細を見る →</div>
            </div>
          </div>
          
          <div className="card cursor-pointer hover:-translate-y-1 transition-transform border-l-4 border-primary-color">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">マインドフルネス呼吸法</h3>
              <div className="bg-primary-light text-primary-color px-2 py-1 rounded-full text-xs flex items-center">
                <span className="mr-1">🧘</span>
                <span>リラックス</span>
              </div>
            </div>
            <div className="text-sm text-gray-600 flex items-center mb-2">
              <span className="mr-1">⏱️</span>
              <span>所要時間: 約15分</span>
            </div>
            <p className="text-gray-700 mb-4 text-sm">
              5分間の集中呼吸法で、ストレスを軽減し、心を落ち着かせます。疲れた脳をリフレッシュするのに効果的です。
            </p>
            <div className="flex justify-between items-center text-xs">
              <div className="text-gray-500">適した場所: オフィス、家、カフェ、移動中</div>
              <div className="text-primary-color">詳細を見る →</div>
            </div>
          </div>
          
          <div className="card cursor-pointer hover:-translate-y-1 transition-transform border-l-4 border-primary-color">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">集中力回復ポモドーロ</h3>
              <div className="bg-primary-light text-primary-color px-2 py-1 rounded-full text-xs flex items-center">
                <span className="mr-1">🧠</span>
                <span>短時間集中</span>
              </div>
            </div>
            <div className="text-sm text-gray-600 flex items-center mb-2">
              <span className="mr-1">⏱️</span>
              <span>所要時間: 約25分</span>
            </div>
            <p className="text-gray-700 mb-4 text-sm">
              ポモドーロテクニックを使って、25分間の集中作業と5分間の休憩を組み合わせた効率的な作業法です。疲れていても取り組みやすい方法です。
            </p>
            <div className="flex justify-between items-center text-xs">
              <div className="text-gray-500">適した場所: オフィス、家、カフェ</div>
              <div className="text-primary-color">詳細を見る →</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
