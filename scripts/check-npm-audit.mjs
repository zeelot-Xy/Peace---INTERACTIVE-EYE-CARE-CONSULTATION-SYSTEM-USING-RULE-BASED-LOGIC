import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const command = process.platform === 'win32' ? process.env.ComSpec : 'npm'
const args = process.platform === 'win32'
  ? ['/d', '/s', '/c', 'npm.cmd audit --omit=dev --json']
  : ['audit', '--omit=dev', '--json']
const result = spawnSync(command, args, {
  cwd: path.join(projectRoot, 'frontend'),
  encoding: 'utf8',
})

if (result.error) {
  throw result.error
}

let report
try {
  report = JSON.parse(result.stdout)
} catch {
  process.stderr.write(result.stderr || result.stdout)
  throw new Error('npm audit did not return valid JSON.')
}

const allowedAdvisories = new Map([
  [
    'https://github.com/advisories/GHSA-qwww-vcr4-c8h2',
    'Only unstable React Server Components APIs are affected; this Vite SPA does not use RSC.',
  ],
])
const observedAllowed = new Set()
const vulnerabilities = report.vulnerabilities ?? {}

function isAccepted(name, trail = new Set()) {
  if (trail.has(name)) return false
  const vulnerability = vulnerabilities[name]
  if (!vulnerability) return false
  if (!['high', 'critical'].includes(vulnerability.severity)) return true
  const nextTrail = new Set(trail).add(name)
  return vulnerability.via.length > 0 && vulnerability.via.every((item) => {
    if (typeof item === 'string') return isAccepted(item, nextTrail)
    if (!allowedAdvisories.has(item.url)) return false
    observedAllowed.add(item.url)
    return true
  })
}

const rejected = Object.keys(vulnerabilities).filter((name) => !isAccepted(name))
if (rejected.length > 0) {
  process.stderr.write(`Unaccepted high/critical npm advisories: ${rejected.join(', ')}\n`)
  process.exit(1)
}

if (result.status !== 0 && observedAllowed.size === 0) {
  process.stderr.write(result.stderr || result.stdout)
  process.exit(result.status ?? 1)
}

for (const advisory of observedAllowed) {
  process.stdout.write(`Accepted temporary advisory exception: ${advisory}\n`)
  process.stdout.write(`${allowedAdvisories.get(advisory)}\n`)
}
process.stdout.write('No unaccepted high or critical production npm advisories found.\n')
