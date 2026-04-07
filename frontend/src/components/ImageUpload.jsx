import { useRef, useState } from 'react'
import styles from './ImageUpload.module.css'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_BYTES = 10 * 1024 * 1024

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export default function ImageUpload({ label, testId, onFile }) {
  const inputRef = useRef(null)
  const [fileName, setFileName] = useState(null)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)

  async function handleFile(file) {
    setError(null)
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Unsupported format. Use JPEG, PNG, or WEBP.')
      return
    }
    if (file.size > MAX_SIZE_BYTES) {
      setError('File too large. Maximum size is 10 MB.')
      return
    }
    setFileName(file.name)
    const b64 = await fileToBase64(file)
    onFile(b64)
  }

  return (
    <div
      className={`${styles.zone} ${dragging ? styles.dragging : ''} ${fileName ? styles.filled : ''}`}
      data-testid={`upload-zone-${testId}`}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      onClick={() => inputRef.current.click()}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && inputRef.current.click()}
      aria-label={label}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(',')}
        onChange={e => { const f = e.target.files[0]; if (f) handleFile(f) }}
        style={{ display: 'none' }}
        data-testid={`upload-input-${testId}`}
      />
      <p className={styles.zoneLabel}>{label}</p>
      {!fileName && (
        <p className={styles.hint} data-testid="upload-hint">
          Drag & drop or click to choose<br />
          <span className={styles.formats}>JPEG · PNG · WEBP · max 10 MB</span>
        </p>
      )}
      {fileName && (
        <p className={styles.fileName} data-testid="file-name">{fileName}</p>
      )}
      {error && (
        <p className={styles.error} role="alert">{error}</p>
      )}
    </div>
  )
}
