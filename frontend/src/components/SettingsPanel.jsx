import { useApp } from '../context/AppContext'
import styles from './SettingsPanel.module.css'

const STANDARDS = [
  { key: 'psa', label: 'PSA' },
  { key: 'bgs', label: 'BGS' },
  { key: 'cgc', label: 'CGC' },
  { key: 'tag', label: 'TAG' },
]

export default function SettingsPanel({ onClose }) {
  const { gradingStandard, setGradingStandard } = useApp()

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={styles.panel}
        data-testid="settings-panel"
        onClick={e => e.stopPropagation()}
      >
        <h2 className={styles.title}>Settings</h2>
        <p className={styles.label}>Grading Standard</p>
        <div className={styles.toggleGroup}>
          {STANDARDS.map(({ key, label }) => (
            <button
              key={key}
              className={`${styles.toggle} ${gradingStandard === key ? styles.active : ''}`}
              aria-pressed={gradingStandard === key}
              data-testid={`std-${key}`}
              onClick={() => setGradingStandard(key)}
            >
              {label}
            </button>
          ))}
        </div>
        <button className={styles.close} onClick={onClose} aria-label="Close settings">✕</button>
      </div>
    </div>
  )
}
