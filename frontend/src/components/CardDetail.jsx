import styles from './CardDetail.module.css'

function formatPrice(usd) {
  if (usd == null) return 'Price not available'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(usd)
}

export default function CardDetail({ candidate, onNotRightCard }) {
  return (
    <div className={styles.detail} data-testid="card-detail">
      {candidate.image_url && (
        <img
          className={styles.image}
          src={candidate.image_url}
          alt={candidate.name}
        />
      )}
      <div className={styles.info}>
        <h2 className={styles.name}>{candidate.name}</h2>
        <p className={styles.edition}>{candidate.edition}</p>
        <p className={styles.meta}>
          {candidate.foil ? 'Foil' : 'Non-foil'} · {candidate.language}
          {candidate.collector_number && ` · #${candidate.collector_number}`}
        </p>
        <p className={styles.price}>{formatPrice(candidate.price_usd)}</p>
        <button
          className={styles.notRight}
          data-testid="not-right-card"
          onClick={onNotRightCard}
        >
          Not the right card?
        </button>
      </div>
    </div>
  )
}
