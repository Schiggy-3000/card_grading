import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import ImageUpload from '../components/ImageUpload'
import GradeResult from '../components/GradeResult'
import { gradeCard } from '../api/grade'
import styles from './Grade.module.css'

const SAMPLE_FRONT = `${import.meta.env.BASE_URL}samples/MTG/Black_Lotus_Unlimited_Front.jpg`
const SAMPLE_BACK  = `${import.meta.env.BASE_URL}samples/MTG/Black_Lotus_Unlimited_Back.jpg`

export default function Grade() {
  const navigate = useNavigate()
  const { gradingStandard, addHistoryEntry } = useApp()

  const frontRef = useRef(null)
  const backRef  = useRef(null)

  const [frontB64, setFrontB64] = useState(null)
  const [backB64, setBackB64] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [networkError, setNetworkError] = useState(false)
  const [resetKey, setResetKey] = useState(0)

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

  async function loadSample() {
    await Promise.all([
      frontRef.current?.load(SAMPLE_FRONT, 'Black_Lotus_Unlimited_Front.jpg'),
      backRef.current?.load(SAMPLE_BACK,  'Black_Lotus_Unlimited_Back.jpg'),
    ])
  }

  function handleReset() {
    setFrontB64(null)
    setBackB64(null)
    setResult(null)
    setNetworkError(false)
    setResetKey(k => k + 1)
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
          <ImageUpload key={`front-${resetKey}`} ref={frontRef} label="Front" testId="front" onFile={setFrontB64} />
          <ImageUpload key={`back-${resetKey}`}  ref={backRef}  label="Back"  testId="back"  onFile={setBackB64} />
        </div>

        <button className={styles.sampleBtn} onClick={loadSample}>
          No card? Load Black Lotus Unlimited as sample →
        </button>

        <button
          className={`${styles.submit}${loading ? ' btn-loading' : ''}`}
          data-testid="grade-submit"
          disabled={!canSubmit || loading}
          onClick={handleSubmit}
          title={!canSubmit ? 'Upload front and back images first' : undefined}
        >
          {loading ? 'Analyzing…' : 'Analyze Card'}
        </button>

        {networkError && (
          <p className={styles.error} data-testid="error-retry" role="alert">
            Network error. Please try again.
          </p>
        )}

        {result && <GradeResult result={result} />}

        {result && (
          <button className={styles.reset} onClick={handleReset}>
            Grade another card
          </button>
        )}
      </main>
    </div>
  )
}
