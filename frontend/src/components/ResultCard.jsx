import React from 'react'

const normalizeList = (value) => {
  if (!value) {
    return []
  }
  if (Array.isArray(value)) {
    return value
      .flatMap((item) => {
        if (!item) {
          return []
        }
        if (typeof item === 'object') {
          return [JSON.stringify(item)]
        }
        return [String(item)]
      })
      .filter(Boolean)
  }
  if (typeof value === 'string') {
    return value.split(/[;；、,\n]/).map((item) => item.trim()).filter(Boolean)
  }
  if (typeof value === 'object') {
    return [JSON.stringify(value)]
  }
  return []
}

const formatBasicProfile = (basicProfile) => {
  if (!basicProfile || typeof basicProfile !== 'object') {
    return []
  }

  return Object.entries(basicProfile).map(([key, value]) => {
    if (Array.isArray(value)) {
      return `${key}：${value.map((item) => (typeof item === 'object' ? JSON.stringify(item) : String(item))).join('，')}`
    }

    if (typeof value === 'object' && value !== null) {
      return `${key}：${JSON.stringify(value)}`
    }

    return `${key}：${String(value)}`
  })
}

const SectionList = ({ title, items, tone = 'neutral' }) => {
  const list = normalizeList(items)

  if (list.length === 0) {
    return null
  }

  return (
    <div className={`knowledge-block ${tone}`}>
      <div className="knowledge-block-title">{title}</div>
      <div className="knowledge-tags">
        {list.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </div>
  )
}

export const ResultCard = ({ result }) => {
  if (!result) {
    return null
  }

  const recognition = result.recognition || {}
  const knowledge = result.knowledge || {}
  const top3 = recognition.top_3 || []
  const topSpecies = recognition.top_1 || top3[0] || { species: 'Unknown Species', confidence: 0 }
  const confidence = Number(topSpecies.confidence || 0)

  const confidenceClass = confidence >= 0.8 ? 'is-high' : confidence >= 0.6 ? 'is-medium' : 'is-low'
  const agentEnabled = knowledge.enabled || knowledge.provider === 'qwen'

  return (
    <div className="space-y-6">
      <section className="analysis-hero glass-panel">
        <div className="analysis-hero-top">
          <div>
            <p className="eyebrow">Model Recognition</p>
            <h2>{topSpecies.species}</h2>
            <p className="analysis-summary">
              {result.summary || knowledge.summary || recognition.suggestion || 'Recognition complete, preparing knowledge cards.'}
            </p>
          </div>

          <div className={`confidence-pill ${confidenceClass}`}>
            <span>Confidence</span>
            <strong>{(confidence * 100).toFixed(1)}%</strong>
          </div>
        </div>

        <div className="confidence-bar">
          <div className="confidence-bar-fill" style={{ width: `${Math.max(4, confidence * 100)}%` }} />
        </div>

        <div className="result-meta-row">
          <span>{recognition.model_ready ? 'Model Ready' : 'Demo Mode'}</span>
          <span>{agentEnabled ? `Qwen Agent: ${knowledge.model || 'qwen'}` : 'Local Fallback Enabled'}</span>
          <span>{recognition.heatmap_base64 ? 'Heatmap Ready' : 'No Heatmap'}</span>
        </div>
      </section>

      {recognition.suggestion && (
        <section className="callout-panel">
          <p>
            <strong>Recognition Tip:</strong>
            {' '}
            {recognition.suggestion}
          </p>
        </section>
      )}

      <section className="glass-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Top 3 Predictions</p>
            <h3>Candidate Ranking</h3>
          </div>
        </div>

        <div className="rank-list">
          {top3.map((item) => (
            <div className="rank-row" key={`${item.rank}-${item.species}`}>
              <div className="rank-label">#{item.rank}</div>
              <div className="rank-body">
                <div className="rank-species">{item.species}</div>
                <div className="rank-bar">
                  <div className="rank-bar-fill" style={{ width: `${Math.max(2, Number(item.confidence || 0) * 100)}%` }} />
                </div>
              </div>
              <div className="rank-confidence">{(Number(item.confidence || 0) * 100).toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </section>

      {recognition.heatmap_base64 && (
        <section className="glass-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Heatmap</p>
              <h3>Model Attention Region</h3>
            </div>
          </div>
          <img src={recognition.heatmap_base64} alt="Recognition Heatmap" className="heatmap-image" />
        </section>
      )}

      <section className="glass-panel knowledge-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Qwen Knowledge Base</p>
            <h3>Auto-generated knowledge card around the recognition result</h3>
          </div>
        </div>

        <div className="knowledge-summary">
          <p>{knowledge.summary || result.summary || 'No knowledge summary yet'}</p>
        </div>

        <div className="knowledge-grid">
          <SectionList title="Basic Information" items={formatBasicProfile(knowledge.basic_profile)} tone="amber" />
          <SectionList title="Habitat" items={knowledge.habitat} tone="green" />
          <SectionList title="Appearance" items={knowledge.appearance} tone="gold" />
          <SectionList title="Diet" items={knowledge.diet} tone="cyan" />
          <SectionList title="Behavior" items={knowledge.behavior} tone="violet" />
          <SectionList title="Distribution & Conservation" items={[...(normalizeList(knowledge.distribution)), ...(normalizeList([knowledge.conservation]))]} tone="rose" />
          <SectionList title="Observation Tips" items={knowledge.observation_tips} tone="indigo" />
          <SectionList title="Fun Facts" items={knowledge.interesting_facts} tone="neutral" />
        </div>

        <div className="search-term-row">
          <div className="search-term-title">Recommended Search Terms</div>
          <div className="knowledge-tags">
            {normalizeList(knowledge.search_terms).map((term) => (
              <span key={term}>{term}</span>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default ResultCard
