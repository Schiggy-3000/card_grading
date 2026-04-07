import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import ImageUpload from '../components/ImageUpload'
import GradeResult from '../components/GradeResult'
import { gradeCard } from '../api/grade'
import styles from './Grade.module.css'

export default function Grade() {
  const navigate = useNavigate()
  const { gradingStandard, addHistoryEntry } = useApp()

  const [frontB64, setFrontB64] = useState(null)
  const [backB64, setBackB64] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [networkError, setNetworkError] = useState(false)

  const canSubmit = frontB64 && backB64

  async function handleSubmit() {
    if (!canSubmit) return
    setLoading(true)
    setNetworkError(false)
    setResult(null)
    try {
      const data = await gradeCard(frontB64, backB64, gradingStandard)
      setResult(data)
      addHistoryEntry({ tool: 'grade', cardName: null, result: data })
    } catch {
      setNetworkError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/')}>← Back</button>
        <h1 className={styles.title}>Grade Card</h1>
      </header>

      <main className={styles.content}>
        <p className={styles.standardNote}>
          Grading standard: <strong>{gradingStandard.toUpperCase()}</strong>
        </p>

        <div className={styles.uploads}>
          <ImageUpload label="Front" testId="front" onFile={setFrontB64} />
          <ImageUpload label="Back" testId="back" onFile={setBackB64} />
        </div>

        <button
          className={styles.submit}
          data-testid="grade-submit"
          disabled={!canSubmit || loading}
          onClick={handleSubmit}
        >
          {loading ? 'Analyzing…' : 'Analyze Card'}
        </button>

        {networkError && (
          <p className={styles.error} data-testid="error-retry">
            Network error. Please try again.
          </p>
        )}

        {result && <GradeResult result={result} />}
      </main>
    </div>
  )
}
