import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import ImageUpload from '../components/ImageUpload'
import CandidateList from '../components/CandidateList'
import CardDetail from '../components/CardDetail'
import ManualSearch from '../components/ManualSearch'
import { recognizeImage, recognizeQuery } from '../api/recognize'
import styles from './Identify.module.css'

export default function Identify() {
  const navigate = useNavigate()
  const { addHistoryEntry } = useApp()

  const [game, setGame] = useState(null)
  const [imageB64, setImageB64] = useState(null)
  const [imagePreviewUrl, setImagePreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [candidates, setCandidates] = useState(null)
  const [lowConfidence, setLowConfidence] = useState(false)
  const [ocrFailed, setOcrFailed] = useState(false)
  const [ocrText, setOcrText] = useState(null)
  const [selected, setSelected] = useState(null)
  const [showManualSearch, setShowManualSearch] = useState(false)
  const [noResults, setNoResults] = useState(false)
  const [networkError, setNetworkError] = useState(false)

  const canSubmit = game && imageB64

  async function handleSubmit() {
    if (!canSubmit) return
    setLoading(true)
    setNetworkError(false)
    setOcrFailed(false)
    setOcrText(null)
    setCandidates(null)
    setSelected(null)
    setNoResults(false)
    try {
      const data = await recognizeImage(imageB64, game)
      if (data.ocr_failed) {
        setOcrFailed(true)
        setShowManualSearch(true)
      } else {
        setOcrText(data.ocr_text || null)
        setCandidates(data.candidates)
        setLowConfidence(data.low_confidence)
      }
    } catch {
      setNetworkError(true)
    } finally {
      setLoading(false)
    }
  }

  async function handleManualSearch(query) {
    setLoading(true)
    setNetworkError(false)
    setNoResults(false)
    setCandidates(null)
    setSelected(null)
    try {
      const data = await recognizeQuery(query, game)
      if (data.candidates.length === 0) {
        setNoResults(true)
      } else {
        setCandidates(data.candidates)
        setLowConfidence(data.low_confidence)
        setOcrFailed(false)
      }
    } catch {
      setNetworkError(true)
    } finally {
      setLoading(false)
    }
  }

  function handleSelect(candidate) {
    setSelected(candidate)
    addHistoryEntry({ tool: 'identify', cardName: candidate.name, result: candidate })
  }

  function handleNotRightCard() {
    setSelected(null)
    setShowManualSearch(true)
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/')}>← Back</button>
        <h1 className={styles.title}>Identify Card</h1>
      </header>

      <main className={styles.content}>
        {/* Game selector */}
        <div className={styles.gameSelector}>
          {['mtg', 'fab'].map(g => (
            <button
              key={g}
              className={`${styles.gameBtn} ${game === g ? styles.gameBtnActive : ''}`}
              data-testid={`game-${g}`}
              aria-pressed={game === g}
              onClick={() => setGame(g)}
            >
              {g.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Upload */}
        <ImageUpload
          label="Front of card"
          testId="front"
          onFile={setImageB64}
          onPreview={setImagePreviewUrl}
        />

        {/* Submit */}
        <button
          className={styles.submit}
          data-testid="identify-submit"
          disabled={!canSubmit || loading}
          onClick={handleSubmit}
        >
          {loading ? 'Identifying…' : 'Identify Card'}
        </button>

        {/* Network error */}
        {networkError && (
          <p className={styles.error} data-testid="error-retry">
            Network error. Please try again.
          </p>
        )}

        {/* OCR failed */}
        {ocrFailed && (
          <p className={styles.warning} data-testid="ocr-failed-msg">
            Could not read card — try a clearer photo or search by name below.
          </p>
        )}

        {/* Manual search */}
        {showManualSearch && !selected && (
          <ManualSearch onSearch={handleManualSearch} loading={loading} />
        )}

        {/* No results */}
        {noResults && (
          <p className={styles.noResults} data-testid="no-results-msg">
            No cards found — try a different name or spelling.
          </p>
        )}

        {/* Candidates */}
        {candidates && candidates.length > 0 && !selected && (
          <CandidateList
            candidates={candidates}
            lowConfidence={lowConfidence}
            onSelect={handleSelect}
          />
        )}

        {/* Card detail */}
        {selected && (
          <CardDetail
            candidate={selected}
            onNotRightCard={handleNotRightCard}
          />
        )}

        {/* Uploaded image + OCR text side by side */}
        {ocrText && (
          <div className={styles.ocrRow}>
            {imagePreviewUrl && (
              <img
                className={styles.ocrPreview}
                src={imagePreviewUrl}
                alt="Uploaded card"
                data-testid="uploaded-image"
              />
            )}
            <details className={styles.ocrSection}>
              <summary className={styles.ocrToggle}>Raw OCR text</summary>
              <pre className={styles.ocrText} data-testid="ocr-text">{ocrText}</pre>
            </details>
          </div>
        )}
      </main>
    </div>
  )
}
