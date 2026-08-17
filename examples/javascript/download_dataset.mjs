// Download the whole Wikiprompt metadata dataset (no API key) to NDJSON.
// Run: node download_dataset.mjs [out.ndjson]
// The prompt body is NOT in the dataset (metadata only) - use the API with a
// key for content (see ../../docs/api.md).
import { writeFileSync, appendFileSync } from 'node:fs'

const BASE = 'https://www.wikiprompt.org'
const OUT = process.argv[2] || 'wikiprompt_dataset.ndjson'

let url = `${BASE}/dataset?limit=500`
let total = 0
writeFileSync(OUT, '')

while (url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'wikiprompt-dataset-example' } })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const page = await res.json()
  for (const rec of page.data ?? []) {
    appendFileSync(OUT, JSON.stringify(rec) + '\n')
    total++
  }
  if (page.total_prompts) console.log(`catalog total: ${page.total_prompts}`)
  console.log(`  ...${total} records`)
  url = page.next // null -> stop
}
console.log(`done: ${total} records -> ${OUT}`)
