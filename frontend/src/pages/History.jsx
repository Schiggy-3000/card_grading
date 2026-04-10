import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import GradeResult from '../components/GradeResult'
import styles from './History.module.css'

function formatTime(iso) {
  return new Date(iso).toLocaleString()
}

function IdentifyResult({ result }) {
  const { candidates, ocr_text, imagePreviewUrl } = result
  return (
    <div className={styles.identifyResult}>
      {imagePreviewUrl && (
        <img
          className={styles.identifyImage}
          src={imagePreviewUrl}
          alt="Uploaded card"
        />
      )}
      <ul className={styles.candidateList}>
        {candidates.map((c, i) => (
          <li key={i} className={styles.candidateItem}>
            <span className={styles.candidateName}>{c.name}</span>
            <span className={styles.candidateMeta}>{c.edition}{c.foil ? ' · Foil' : ''} · {c.language}</span>
            <span className={styles.candidateConf}>{Math.round(c.confidence * 100)}%</span>
          </li>
        ))}
      </ul>
      {ocr_text && (
        <details className={styles.ocrSection}>
          <summary className={styles.ocrToggle}>Raw OCR text</summary>
          <pre className={styles.ocrText}>{ocr_text}</pre>
        </details>
      )}
    </div>
  )
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
                      <IdentifyResult result={entry.result} />
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
