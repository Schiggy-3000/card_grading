# Card Grading Application — Design Spec

**Date:** 2026-04-01  
**Status:** Approved

---

## Context

Collectors, buyers, and sellers of Magic the Gathering and Flesh and Blood trading cards need a quick, accessible way to assess card condition and identify card versions before trading or selling. This app provides two tools: card recognition (identification + pricing) and card grading (condition assessment), so both parties in a trade can establish a shared, objective baseline without sending cards to a professional grading service first.

---

## Users

- Sellers assessing cards before listing
- Buyers verifying condition before purchasing
- Both parties seeking a shared baseline during a trade

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, deployed to GitHub Pages |
| Backend | Python, deployed as Google Cloud Functions |
| Computer Vision | Google Cloud Vision API (OCR + image analysis) |
| Physical Analysis | OpenCV (defect detection within GCF) |
| Card DB — MTG | Scryfall API (no key required) |
| Card DB — FAB | the-fab-cube/flesh-and-blood-cards JSON repo; images from cards.fabtcg.com |
| Pricing — MTG | Scryfall API (current price only) |
| Pricing — FAB | Not available — show "Price not available" placeholder |
| Testing | Playwright (Python — chosen to match backend developer familiarity) |
| CI/CD | GitHub Actions → GitHub Pages + GCF |

---

## Architecture

Two specialized Cloud Functions, one React frontend. No user accounts, no server-side state.

```
React App (GitHub Pages)
    │
    ├──→ GCF /recognize   → Cloud Vision API, Scryfall API, FAB JSON repo
    └──→ GCF /grade       → Cloud Vision API, OpenCV
```

**Why two functions:** Clean separation of concerns, independent scaling and deployment, isolated failure domains. Maps naturally to two CI/CD deployment targets.

**CI/CD note:** Both functions are deployed together on green. Staging environment and per-function independent deploy are out of scope for v1 — to be addressed in a separate infrastructure spec.

---

## Frontend

### Navigation

Landing page (Home) with two large tool-card buttons: **Identify** and **Grade**. Settings accessible from Home only via a settings icon. There is no persistent navigation bar — users must return to Home to switch tools or change settings. Changing the grading standard mid-workflow requires navigating back to Home.

### Visual Design

Dark & Premium aesthetic:
- Background: near-black (`#0d0d0d`)
- Surface: dark grey (`#1a1a1a`) with subtle borders
- Accent: gold (`#c9a84c`)
- Labels: uppercase, wide letter-spacing
- Font: system sans-serif (UI), serif optional for headings

### Image Upload Constraints

Applies to all image upload areas (Identify front, Grade front, Grade back):
- Accepted formats: JPEG, PNG, WEBP
- Maximum file size: 10 MB
- Recommended minimum resolution: 1000px on the shortest side (shown as a hint, not enforced)
- Validation is client-side; errors shown inline before upload

### Screens

**Home**
- Two tool cards: Identify and Grade
- Footer strip: current grading standard + session history count
- Settings icon → Settings panel

**Settings Panel**
- Grading standard selector: PSA / BGS / CGC / TAG (toggle buttons)
- Standard persisted to `localStorage`; defaults to PSA on first launch if no value is stored

**Identify Workflow**
1. Game selector: MTG / FAB toggle (required before or alongside upload)
2. Image upload area (drag & drop or file picker, front of card only)
3. On submit: show top 3–5 ranked candidate matches (name, edition, foil type, language, confidence %)
   - Candidates are always returned (up to 5); if confidence is below 0.3 for all results, show a low-confidence warning above the list
4. User selects the correct version
5. Show: fetched card image, version details, current price (MTG only; FAB shows "Price not available")
6. Fallback: "Not the right card?" link → text search input → query Scryfall/FAB using the already-selected game → show matching versions using same candidate schema → user picks
   - If manual search returns zero results: show "No cards found — try a different name or spelling"

**Grade Workflow**
1. Two independent upload areas side by side: **Front** (required) and **Back** (required) — each has its own file picker/drag-drop zone so the user can upload the two photos separately (photograph front → upload → flip card → photograph back → upload)
2. The "Analyze Card" button is disabled until both upload areas are filled
3. Grading standard shown (from persistent setting)
4. On submit: show grade results
5. Results: physical analysis sub-grades (Centering, Corners, Edges, Surface) shown as informational breakdown + overall grade estimate mapped to the selected standard's scale + plain-text reasoning per category

**Session History**
- Stored in React Context (in-memory, clears on tab close/refresh)
- Accessible from Home (history count shown in footer)
- Entry schema:
```json
{
  "id": "<uuid>",
  "tool": "identify" | "grade",
  "timestamp": "<ISO 8601>",
  "cardName": "Lightning Bolt" | null,
  "result": { /* full API response snapshot */ }
}
```
- `cardName`: populated from the selected candidate name for Identify entries; always `null` for Grade entries (no card identification occurs in the Grade workflow)

### State Management

React Context holds:
- `gradingStandard` (string, one of `"psa" | "bgs" | "cgc" | "tag"`) — persisted to `localStorage`
- `sessionHistory` (array of history entry objects) — in-memory only, no images retained after API response

---

## Backend

### GCF: `/recognize`

**Input:**
```json
{
  "image": "<base64-encoded front image>",
  "game": "mtg" | "fab"
}
```

**Steps:**
1. Send image to Cloud Vision API for OCR — extract card name, set symbol, collector number
2. Query Scryfall (MTG) or FAB JSON repo with extracted text
3. Rank results: confidence = composite of Cloud Vision OCR confidence score × fuzzy string match ratio against card name/set fields
4. Return up to 5 candidates, sorted descending by confidence (always return available results even if confidence is low)

**Manual search mode** (triggered when user types a card name):
```json
{ "query": "Lightning Bolt", "game": "mtg" }
```
Skips Cloud Vision — queries database directly by name using fuzzy match, returns matching versions using the same candidate schema. On zero results, returns HTTP 200 with `"candidates": []`. In manual search mode, `confidence` equals the fuzzy match ratio alone (no OCR component; range 0.0–1.0).

**Output per candidate:**
```json
{
  "name": "Lightning Bolt",
  "edition": "Alpha",
  "foil": false,
  "language": "EN",
  "collector_number": "161",
  "image_url": "...",
  "price_usd": 240.00,
  "confidence": 0.94
}
```
- `price_usd`: current price from Scryfall for MTG; `null` for FAB
- `confidence`: float 0.0–1.0

---

### GCF: `/grade`

**Input:**
```json
{
  "front": "<base64-encoded front image>",
  "back": "<base64-encoded back image>",
  "standard": "psa" | "bgs" | "cgc" | "tag"
}
```

Grading logic is game-agnostic (card dimensions and back design are standardised across MTG and FAB); no `game` field is required.

**Steps:**
1. Send both images to Cloud Vision API for general image analysis
2. Run OpenCV within the function for defect detection: corner wear, edge nicks, surface scratches, centering measurement
3. Compute physical sub-grades (Centering, Corners, Edges, Surface) on a 1–10 internal scale as an informational breakdown
4. Derive overall grade estimate mapped to the selected standard's published scale and format:
   - PSA: integer 1–10
   - BGS: half-point increments (e.g. 9.5), scale 1–10
   - CGC: half-point increments with a text label (e.g. 9.5 / "Mint+") — returned as `"overall": 9.5` plus `"label": "Mint+"` in the response
   - TAG: tenths (e.g. 9.4), scale 1–10
5. Return results

**Output:**
```json
{
  "standard": "psa",
  "overall": 8,
  "label": null,
  "subgrades": {
    "centering": 8.5,
    "corners": 7.0,
    "edges": 8.0,
    "surface": 7.0
  },
  "reasoning": {
    "centering": "Left-right offset within acceptable range.",
    "corners": "Minor wear visible on bottom-left corner.",
    "edges": "Clean with no visible nicks.",
    "surface": "Light scratching under direct light on front surface."
  }
}
```
- `overall`: type and range depend on standard (see step 4 above)
- `label`: string for CGC only (e.g. `"Mint+"`); `null` for all other standards
- `subgrades`: always returned as floats on the internal 1–10 scale regardless of standard; shown in UI as informational breakdown, not as official sub-grades

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Invalid file type or size | Client-side validation before upload; show inline error |
| Cloud Vision returns no usable text | Show "Could not read card — try a clearer photo" + manual search prompt |
| All recognition candidates below confidence 0.3 | Show results with a low-confidence warning: "Results may not be accurate — try a clearer photo or use manual search" |
| Manual search returns zero results | Show "No cards found — try a different name or spelling" |
| Partial grading failure (one sub-category fails) | Show available sub-grades; show error indicator for failed category |
| Network error (any API) | Show retry prompt; no silent failures |
| FAB JSON repo unreachable | Treat as network error; show retry prompt |
| FAB price unavailable | Show "Price not available" placeholder (by design, not an error) |

---

## Testing

- **Playwright (Python):** end-to-end tests for both workflows
  - Identify: upload image → see candidate list → select version → see price
  - Grade: upload front + back → see sub-grades + overall + reasoning
  - Manual search: trigger fallback → type name → see results
  - Low-confidence: mock low-confidence response → verify warning shown
- **GitHub Actions:** runs Playwright suite on every push; deploys to GitHub Pages + GCF only on green

---

## Out of Scope

- User accounts or authentication
- Server-side history or persistence
- Historical price graphs (current price only)
- Back-of-card recognition
- Mobile camera capture (upload only)
- FAB pricing (placeholder shown)
- Batch grading of multiple cards
- Per-function independent CI/CD deploy (both functions deploy together)
