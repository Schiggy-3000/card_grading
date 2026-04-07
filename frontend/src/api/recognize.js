const RECOGNIZE_URL = import.meta.env.VITE_RECOGNIZE_URL

export async function recognizeImage(imageBase64, game) {
  const resp = await fetch(RECOGNIZE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64, game }),
  })
  if (!resp.ok) throw new Error(`recognize failed: HTTP ${resp.status}`)
  return resp.json()
}

export async function recognizeQuery(query, game) {
  const resp = await fetch(RECOGNIZE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, game }),
  })
  if (!resp.ok) throw new Error(`recognize failed: HTTP ${resp.status}`)
  return resp.json()
}
