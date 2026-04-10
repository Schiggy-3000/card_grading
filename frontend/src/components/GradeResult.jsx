import styles from './GradeResult.module.css'

const DIM_LABELS = {
  centering: 'Centering',
  corners: 'Corners',
  edges: 'Edges',
  surface: 'Surface',
}

function GradeSide({ side, standard, sideLabel }) {
  const { overall, label, subgrades, reasoning, bbox_image } = side
  return (
    <div className={styles.side}>
      <h3 className={styles.sideLabel}>{sideLabel}</h3>

      {bbox_image && (
        <img
          className={styles.bboxImage}
          src={`data:image/jpeg;base64,${bbox_image}`}
          alt={`${sideLabel} with detected card boundary`}
        />
      )}

      <div className={styles.overall}>
        <p className={styles.standardLabel}>{standard.toUpperCase()} Grade</p>
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

export default function GradeResult({ result }) {
  const { standard, front, back } = result
  return (
    <div className={styles.result} data-testid="grade-result">
      <GradeSide side={front} standard={standard} sideLabel="Front" />
      <GradeSide side={back} standard={standard} sideLabel="Back" />
    </div>
  )
}
