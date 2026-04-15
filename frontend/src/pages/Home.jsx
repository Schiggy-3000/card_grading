import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import SettingsPanel from '../components/SettingsPanel'
import styles from './Home.module.css'

export default function Home() {
  const navigate = useNavigate()
  const { gradingStandard, sessionHistory } = useApp()
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Card Grading</h1>
        <button
          className={styles.settingsBtn}
          data-testid="settings-btn"
          onClick={() => setShowSettings(true)}
          aria-label="Open settings"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </header>

      <main className={styles.tools}>
        <button
          className={styles.toolCard}
          data-tool="identify"
          onClick={() => navigate('/identify')}
        >
          <span className={styles.toolIcon}>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </span>
          <span className={styles.toolName}>Identify</span>
          <span className={styles.toolDesc}>
            Upload a photo — get card name, edition, and price
          </span>
        </button>

        <button
          className={styles.toolCard}
          data-tool="grade"
          onClick={() => navigate('/grade')}
        >
          <span className={styles.toolIcon}>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18 20V10M12 20V4M6 20v-6"/>
            </svg>
          </span>
          <span className={styles.toolName}>Grade</span>
          <span className={styles.toolDesc}>
            Upload front &amp; back — get a condition grade estimate
          </span>
        </button>
      </main>

      <footer className={styles.footer} data-testid="footer">
        <span>Standard: <strong>{gradingStandard.toUpperCase()}</strong></span>
        <button
          className={styles.historyLink}
          onClick={() => navigate('/history')}
        >
          History ({sessionHistory.length})
        </button>
      </footer>

      {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}
    </div>
  )
}
