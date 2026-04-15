import { useState } from 'react'
import styles from './ManualSearch.module.css'

export default function ManualSearch({ onSearch, loading }) {
  const [query, setQuery] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  return (
    <form
      className={styles.form}
      data-testid="manual-search"
      onSubmit={handleSubmit}
    >
      <input
        className={styles.input}
        data-testid="manual-search-input"
        type="text"
        placeholder="Enter card name…"
        value={query}
        onChange={e => setQuery(e.target.value)}
        disabled={loading}
      />
      <button
        className={`${styles.submit}${loading ? ' btn-loading' : ''}`}
        data-testid="manual-search-submit"
        type="submit"
        disabled={loading || !query.trim()}
      >
        {loading ? 'Searching…' : 'Search'}
      </button>
    </form>
  )
}
