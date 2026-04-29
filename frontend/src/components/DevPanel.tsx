import { useState, useEffect, useCallback, CSSProperties } from 'react'

const SCENARIOS = [
  'fresh_game',
  'fresh_game_seeded',
  'canal_progress',
  'railway_activation',
  'canal_mania',
  'heritage',
  'election_pressure',
  'crisis',
]

const SLIDERS = [
  { label: 'Election Polling', field: 'metrics.election_polling', init: 65 },
  { label: 'Aesthetic Index', field: 'metrics.aesthetic_index', init: 40 },
  { label: 'Railway Influence', field: 'railway_party.influence', init: 20 },
]

function getToken() {
  return import.meta.env.VITE_ADMIN_TOKEN ?? localStorage.getItem('admin_token') ?? 'dev-admin'
}

async function adminPost(path: string, params: Record<string, string | number> = {}) {
  const qs = new URLSearchParams({
    token: getToken(),
    ...Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)])),
  })
  const res = await fetch(`http://localhost:8000${path}?${qs}`, { method: 'POST' })
  if (!res.ok) {
    const detail = await res.text().catch(() => res.status.toString())
    throw new Error(`${path} ${res.status}: ${detail}`)
  }
  return res.json()
}

const btn: CSSProperties = {
  flex: 1,
  padding: '4px 0',
  background: '#1f2937',
  color: '#d1d5db',
  border: '1px solid #374151',
  borderRadius: 4,
  cursor: 'pointer',
  fontSize: '0.72rem',
  fontFamily: 'monospace',
}

const sectionLabel: CSSProperties = {
  color: '#6b7280',
  fontSize: '0.65rem',
  letterSpacing: '0.1em',
  marginTop: 12,
  marginBottom: 4,
}

export default function DevPanel() {
  const [visible, setVisible] = useState(false)
  const [status, setStatus] = useState('')
  const [sliderVals, setSliderVals] = useState<Record<string, number>>(
    Object.fromEntries(SLIDERS.map(s => [s.field, s.init]))
  )

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault()
        setVisible(v => !v)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const call = useCallback(async (fn: () => Promise<any>, label?: string) => {
    setStatus(label ? `${label}...` : '...')
    try {
      const r = await fn()
      const info = r.turn != null
        ? `turn ${r.turn} cycle ${r.cycle ?? '?'}`
        : r.saved ? `saved → ${r.slot}` : 'ok'
      setStatus(`✓ ${info}`)
    } catch (err: any) {
      setStatus(`✗ ${err.message}`)
    }
  }, [])

  if (!import.meta.env.DEV || !visible) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      bottom: 0,
      width: 220,
      background: '#0d1117',
      color: '#e5e7eb',
      zIndex: 9999,
      overflowY: 'auto',
      padding: '0.75rem',
      borderLeft: '2px solid #f59e0b',
      fontFamily: 'monospace',
      fontSize: '0.72rem',
      boxSizing: 'border-box',
    }}>
      <div style={{ color: '#f59e0b', fontWeight: 700, marginBottom: 2 }}>DEV PANEL</div>
      <div style={{ color: '#4b5563', fontSize: '0.62rem', marginBottom: 8 }}>Ctrl+Shift+D to close</div>

      {/* Scenarios */}
      <div style={sectionLabel}>SCENARIOS</div>
      {SCENARIOS.map(s => (
        <button
          key={s}
          onClick={() => call(() => adminPost('/admin/seed-scenario', { scenario: s }), s)}
          style={{ display: 'block', width: '100%', marginBottom: 3, padding: '3px 6px', ...btn, textAlign: 'left' }}
        >
          {s.replace(/_/g, ' ')}
        </button>
      ))}

      {/* Turn controls */}
      <div style={sectionLabel}>TURNS</div>
      <div style={{ display: 'flex', gap: 6 }}>
        <button onClick={() => call(() => adminPost('/admin/advance-turn', { count: 1 }), '+1 turn')} style={btn}>+1 turn</button>
        <button onClick={() => call(() => adminPost('/admin/advance-turn', { count: 5 }), '+5 turns')} style={btn}>+5 turns</button>
      </div>

      {/* Metric sliders */}
      <div style={sectionLabel}>METRICS</div>
      {SLIDERS.map(({ label, field }) => (
        <div key={field} style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
            <span style={{ color: '#9ca3af' }}>{label}</span>
            <span style={{ color: '#f3f4f6' }}>{sliderVals[field]}</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            value={sliderVals[field]}
            style={{ width: '100%', accentColor: '#f59e0b' }}
            onChange={e => setSliderVals(v => ({ ...v, [field]: Number(e.target.value) }))}
            onMouseUp={e => {
              const val = (e.target as HTMLInputElement).value
              call(() => adminPost('/admin/set-field', { field, value: val }), label)
            }}
          />
        </div>
      ))}

      {/* Save / restore */}
      <div style={sectionLabel}>QUICKSAVE</div>
      <div style={{ display: 'flex', gap: 6 }}>
        <button onClick={() => call(() => adminPost('/admin/save-state', { slot: 'quicksave' }), 'save')} style={btn}>Save</button>
        <button onClick={() => call(() => adminPost('/admin/load-state', { slot: 'quicksave' }), 'restore')} style={btn}>Restore</button>
      </div>

      {/* Status line */}
      <div style={{
        marginTop: 12,
        padding: '4px 6px',
        background: '#111827',
        borderRadius: 4,
        color: status.startsWith('✗') ? '#ef4444' : '#6ee7b7',
        minHeight: 20,
        wordBreak: 'break-all',
      }}>
        {status || ' '}
      </div>
    </div>
  )
}
