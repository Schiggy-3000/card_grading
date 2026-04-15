import { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react'
import styles from './ImageUpload.module.css'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_BYTES = 10 * 1024 * 1024

const ImageUpload = forwardRef(function ImageUpload(
  { label, testId, onFile = () => {}, onPreview = () => {} },
  ref
) {
  const inputRef = useRef(null)
  const readerRef = useRef(null)
  const [fileName, setFileName] = useState(null)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)

  useEffect(() => {
    return () => { readerRef.current?.abort() }
  }, [])

  useImperativeHandle(ref, () => ({
    async load(url, displayName) {
      setError(null)
      setFileName(null)
      try {
        const resp = await fetch(url)
        if (!resp.ok) throw new Error('fetch failed')
        const blob = await resp.blob()
        const dataUrl = await new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => resolve(reader.result)
          reader.onerror = reject
          reader.readAsDataURL(blob)
        })
        setFileName(displayName)
        onPreview(dataUrl)
        onFile(dataUrl.split(',')[1])
      } catch {
        setError('Could not load sample image.')
      }
    }
  }))

  async function handleFile(file) {
    setError(null)
    setFileName(null)
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Unsupported format. Use JPEG, PNG, or WEBP.')
      if (inputRef.current) inputRef.current.value = ''
      return
    }
    if (file.size > MAX_SIZE_BYTES) {
      setError('File too large. Maximum size is 10 MB.')
      if (inputRef.current) inputRef.current.value = ''
      return
    }
    try {
      const b64 = await new Promise((resolve, reject) => {
        readerRef.current?.abort()
        const reader = new FileReader()
        readerRef.current = reader
        reader.onload = () => { onPreview(reader.result); resolve(reader.result.split(',')[1]) }
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
      readerRef.current = null
      setFileName(file.name)
      onFile(b64)
    } catch {
      setError('Could not read the file. Please try again.')
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div
      className={`${styles.zone} ${dragging ? styles.dragging : ''} ${fileName ? styles.filled : ''}`}
      data-testid={`upload-zone-${testId}`}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={e => { if (!e.currentTarget.contains(e.relatedTarget)) setDragging(false) }}
      onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      onClick={() => { setError(null); inputRef.current.click() }}
      role="button"
      tabIndex={0}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inputRef.current.click() } }}
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
})

export default ImageUpload
