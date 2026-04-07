const GRADE_URL = import.meta.env.VITE_GRADE_URL

export async function gradeCard(frontBase64, backBase64, standard) {
  const resp = await fetch(GRADE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ front: frontBase64, back: backBase64, standard }),
  })
  if (!resp.ok) throw new Error(`grade failed: HTTP ${resp.status}`)
  return resp.json()
}
