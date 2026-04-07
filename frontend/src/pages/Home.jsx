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
          ⚙
        </button>
      </header>

      <main className={styles.tools}>
        <button
          className={styles.toolCard}
          data-tool="identify"
          onClick={() => navigate('/identify')}
        >
          <span className={styles.toolIcon}>🔍</span>
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
          <span className={styles.toolIcon}>📊</span>
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
