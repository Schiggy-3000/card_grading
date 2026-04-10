import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import CardDetail from '../components/CardDetail'
import GradeResult from '../components/GradeResult'
import styles from './History.module.css'

function formatTime(iso) {
  return new Date(iso).toLocaleString()
}

export default function History() {
  const navigate = useNavigate()
  const { sessionHistory } = useApp()
  const [selectedEntry, setSelectedEntry] = useState(null)

  function handleEntryClick(entry) {
    setSelectedEntry(prev => prev?.id === entry.id ? null : entry)
  }

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
              <li key={entry.id} className={styles.entryWrapper}>
                <button
                  className={`${styles.entry} ${selectedEntry?.id === entry.id ? styles.entryActive : ''}`}
                  data-testid="history-entry"
                  onClick={() => handleEntryClick(entry)}
                >
                  <span className={styles.tool}>{entry.tool}</span>
                  {entry.cardName && (
                    <span className={styles.cardName}>{entry.cardName}</span>
                  )}
                  <span className={styles.time}>{formatTime(entry.timestamp)}</span>
                </button>

                {selectedEntry?.id === entry.id && (
                  <div className={styles.resultPanel} data-testid="history-result">
                    {entry.tool === 'identify' && (
                      <CardDetail candidate={entry.result} onNotRightCard={() => setSelectedEntry(null)} />
                    )}
                    {entry.tool === 'grade' && (
                      <GradeResult result={entry.result} />
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  )
}
