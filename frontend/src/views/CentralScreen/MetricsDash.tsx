import { useGameState } from '../../hooks/useGameState'

function metricBar(value: number, invert: boolean) {
  // invert=true means high is bad (Road Rage), invert=false means high is good
  const effective = invert ? 100 - value : value
  const color = effective >= 60 ? '#22c55e' : effective >= 35 ? '#f59e0b' : '#ef4444'
  return { color, pct: value }
}

function Bar({ label, value, invert }: { label: string; value: number; invert: boolean }) {
  const { color, pct } = metricBar(value, invert)
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
        <span style={{ color: '#9ca3af', fontSize: 11 }}>{label}</span>
        <span style={{ color, fontWeight: 700, fontSize: 12 }}>{Math.round(value)}</span>
      </div>
      <div style={{ height: 6, background: '#2e303a', borderRadius: 3 }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 3, transition: 'width 0.4s' }} />
      </div>
    </div>
  )
}

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0', borderBottom: '1px solid #2e303a' }}>
      <span style={{ color: '#9ca3af', fontSize: 11 }}>{label}</span>
      <span style={{ color: '#d1d5db', fontSize: 11, fontWeight: 600 }}>{value}</span>
    </div>
  )
}

export default function MetricsDash() {
  const gameState = useGameState()
  if (!gameState) return null
  const m = gameState.metrics
  const budget = m.budget

  return (
    <div style={{ padding: '12px 14px', borderBottom: '1px solid #2e303a' }}>
      <div style={{ color: '#f3f4f6', fontWeight: 600, fontSize: 12, marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1 }}>
        Metrics
      </div>

      <Bar label="Road Rage Index" value={m.road_rage_index} invert={true} />
      <Bar label="Canal Efficiency" value={m.canal_efficiency_index} invert={false} />
      <Bar label="Aesthetic Index" value={m.aesthetic_index} invert={false} />

      <div style={{ marginTop: 10, marginBottom: 6, color: '#6b7280', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8 }}>
        Quarterly
      </div>
      <StatRow label="Citizen Happiness" value={Math.round(m.citizen_happiness)} />
      <StatRow label="Horse Pollution" value={Math.round(m.horse_pollution)} />
      <StatRow label="Accidents" value={m.accidents_this_cycle} />
      <StatRow label="Projects Delayed" value={m.projects_delayed} />
      <StatRow label="Tradies Non-billing" value={m.tradies_nonbilling} />

      {budget && (
        <>
          <div style={{ marginTop: 10, marginBottom: 6, color: '#6b7280', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.8 }}>
            Budgets
          </div>
          <StatRow label="Finance" value={`£${budget.finance.toLocaleString()}`} />
          <StatRow label="Infrastructure" value={`£${budget.infrastructure.toLocaleString()}`} />
          <StatRow label="Transport" value={`£${budget.transport.toLocaleString()}`} />
        </>
      )}

      <div style={{ marginTop: 8, display: 'flex', gap: 6 }}>
        <div style={{ flex: 1, background: '#2e303a', borderRadius: 4, padding: '4px 6px', textAlign: 'center' }}>
          <div style={{ color: '#6b7280', fontSize: 9, textTransform: 'uppercase' }}>Polling</div>
          <div style={{ color: m.election_polling < 50 ? '#ef4444' : '#22c55e', fontWeight: 700, fontSize: 13 }}>
            {Math.round(m.election_polling)}%
          </div>
        </div>
        <div style={{ flex: 1, background: '#2e303a', borderRadius: 4, padding: '4px 6px', textAlign: 'center' }}>
          <div style={{ color: '#6b7280', fontSize: 9, textTransform: 'uppercase' }}>Economy</div>
          <div style={{ color: '#d1d5db', fontWeight: 700, fontSize: 13 }}>{Math.round(m.economy_index)}</div>
        </div>
        <div style={{ flex: 1, background: '#2e303a', borderRadius: 4, padding: '4px 6px', textAlign: 'center' }}>
          <div style={{ color: '#6b7280', fontSize: 9, textTransform: 'uppercase' }}>Turn</div>
          <div style={{ color: '#d1d5db', fontWeight: 700, fontSize: 13 }}>{gameState.turn}/20</div>
        </div>
        <div style={{ flex: 1, background: '#2e303a', borderRadius: 4, padding: '4px 6px', textAlign: 'center' }}>
          <div style={{ color: '#6b7280', fontSize: 9, textTransform: 'uppercase' }}>Cycle</div>
          <div style={{ color: '#d1d5db', fontWeight: 700, fontSize: 13 }}>{gameState.cycle}/{gameState.game_length}</div>
        </div>
      </div>
    </div>
  )
}
