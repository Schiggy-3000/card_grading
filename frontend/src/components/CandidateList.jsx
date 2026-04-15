import styles from './CandidateList.module.css'

function confidencePct(score) {
  return `${Math.round(score * 100)}%`
}

function confClass(score) {
  if (score >= 0.85) return styles.confHigh
  if (score >= 0.55) return styles.confMid
  return styles.confLow
}

export default function CandidateList({ candidates, lowConfidence, onSelect }) {
  return (
    <div data-testid="candidate-list">
      {lowConfidence && (
        <p className={styles.warning} data-testid="low-confidence-warning">
          Results may not be accurate — try a clearer photo or use manual search.
        </p>
      )}
      {candidates.map((c, i) => (
        <button
          key={i}
          className={styles.item}
          data-testid="candidate-item"
          onClick={() => onSelect(c)}
        >
          <span className={styles.name}>{c.name}</span>
          <span className={styles.edition}>{c.edition}{c.foil ? ' · Foil' : ''} · {c.language}</span>
          <span className={confClass(c.confidence)}>{confidencePct(c.confidence)}</span>
        </button>
      ))}
    </div>
  )
}
