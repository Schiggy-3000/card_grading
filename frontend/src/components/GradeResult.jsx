import styles from './GradeResult.module.css'

const DIM_LABELS = {
  centering: 'Centering',
  corners: 'Corners',
  edges: 'Edges',
  surface: 'Surface',
}

export default function GradeResult({ result }) {
  const { standard, overall, label, subgrades, reasoning } = result

  return (
    <div className={styles.result} data-testid="grade-result">
      <div className={styles.overall}>
        <p className={styles.standardLabel}>{standard.toUpperCase()} Grade Estimate</p>
        <p className={styles.grade} data-testid="overall-grade">
          {overall}
          {label && <span className={styles.label}> — {label}</span>}
        </p>
      </div>

      <div className={styles.subgrades}>
        {Object.entries(subgrades).map(([key, score]) => {
          const failed = score == null
          return (
            <div key={key} className={`${styles.subgrade} ${failed ? styles.failed : ''}`}>
              <span className={styles.dimName}>{DIM_LABELS[key]}</span>
              {failed ? (
                <span
                  className={styles.dimError}
                  data-testid={`subgrade-error-${key}`}
                >
                  Analysis failed
                </span>
              ) : (
                <>
                  <span className={styles.dimScore}>{score.toFixed(1)}</span>
                  <p className={styles.dimReason}>{reasoning[key]}</p>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
