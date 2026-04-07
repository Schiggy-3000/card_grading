import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import styles from './History.module.css'

function formatTime(iso) {
  return new Date(iso).toLocaleString()
}

export default function History() {
  const navigate = useNavigate()
  const { sessionHistory } = useApp()

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/')}>← Back</button>
        <h1 className={styles.title}>Session History</h1>
      </header>

      <main className={styles.content}>
        {sessionHistory.length === 0 ? (
          <p className={styles.empty} data-testid="history-empty">
            No entries yet. Identify or grade a card to get started.
          </p>
        ) : (
          <ul className={styles.list}>
            {sessionHistory.map(entry => (
              <li key={entry.id} className={styles.entry} data-testid="history-entry">
                <span className={styles.tool}>{entry.tool}</span>
                {entry.cardName && (
                  <span className={styles.cardName}>{entry.cardName}</span>
                )}
                <span className={styles.time}>{formatTime(entry.timestamp)}</span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  )
}
