import React from 'react'

export const ResultCard = ({ result }) => {
  if (!result) return null

  const { top_3, suggestion, heatmap_base64 } = result
  const topSpecies = top_3[0]

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-orange-600 bg-orange-50'
  }

  const getConfidenceBgColor = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-500'
    if (confidence >= 0.6) return 'bg-yellow-500'
    return 'bg-orange-500'
  }

  return (
    <div className="space-y-6">
      {/* 主要结果 */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">识别结果</h2>
        
        <div className={`rounded-lg p-6 ${getConfidenceColor(topSpecies.confidence)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">最可能的物种</p>
              <h3 className="text-2xl font-bold text-gray-900">{topSpecies.species}</h3>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-700">置信度</p>
              <p className="text-3xl font-bold">
                {(topSpecies.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
            <div
              className={`h-2 rounded-full transition-all ${getConfidenceBgColor(topSpecies.confidence)}`}
              style={{ width: `${topSpecies.confidence * 100}%` }}
            />
          </div>
        </div>

        {suggestion && (
          <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <p className="text-blue-800 text-sm">
              <span className="font-semibold">💡 建议：</span> {suggestion}
            </p>
          </div>
        )}
      </div>

      {/* Top-3 结果列表 */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Top-3 预测结果</h3>
        <div className="space-y-3">
          {top_3.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-4 flex-1">
                <span className="text-lg font-bold text-blue-600 w-8">#{item.rank}</span>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">{item.species}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-gray-700">
                  {(item.confidence * 100).toFixed(1)}%
                </p>
                <div className="w-48 h-2 bg-gray-200 rounded-full mt-1">
                  <div
                    className="h-2 bg-blue-500 rounded-full"
                    style={{ width: `${item.confidence * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 热力图可视化 */}
      {heatmap_base64 && (
        <div className="card">
          <h3 className="text-lg font-bold text-gray-800 mb-4">热力图分析</h3>
          <p className="text-sm text-gray-600 mb-3">红色区域表示模型关注的核心特征</p>
          <img
            src={heatmap_base64}
            alt="Heatmap"
            className="w-full rounded-lg border border-gray-200"
          />
        </div>
      )}
    </div>
  )
}

export default ResultCard
