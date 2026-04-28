import { useGameState } from '../../hooks/useGameState'

export default function InfluenceMeter() {
  const gameState = useGameState()
  if (!gameState) return null

  const canal = gameState.canal_party.influence
  const railway = gameState.railway_party.influence
  const diff = canal - railway
  const crisis = railway >= canal
  const approaching = !crisis && diff <= 10

  return (
    <div style={{ padding: '12px 14px', borderBottom: '1px solid #2e303a' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ color: '#f3f4f6', fontWeight: 600, fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
          Party Influence
        </div>
        {crisis && (
          <div style={{ background: '#7f1d1d', color: '#fca5a5', fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 3, letterSpacing: 0.5 }}>
            RAILWAY CRISIS
          </div>
        )}
        {approaching && (
          <div style={{ background: '#78350f', color: '#fcd34d', fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 3, letterSpacing: 0.5 }}>
            APPROACHING CROSSOVER
          </div>
        )}
      </div>

      <div style={{ marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
          <span style={{ color: '#93c5fd', fontSize: 11 }}>Canal Party</span>
          <span style={{ color: '#93c5fd', fontWeight: 700, fontSize: 12 }}>{Math.round(canal)}</span>
        </div>
        <div style={{ height: 8, background: '#2e303a', borderRadius: 4 }}>
          <div style={{ height: '100%', width: `${canal}%`, background: '#3b82f6', borderRadius: 4, transition: 'width 0.4s' }} />
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
          <span style={{ color: '#fca5a5', fontSize: 11 }}>Railway Party</span>
          <span style={{ color: '#fca5a5', fontWeight: 700, fontSize: 12 }}>{Math.round(railway)}</span>
        </div>
        <div style={{ height: 8, background: '#2e303a', borderRadius: 4 }}>
          <div style={{
            height: '100%',
            width: `${railway}%`,
            background: crisis ? '#ef4444' : '#b91c1c',
            borderRadius: 4,
            transition: 'width 0.4s',
            animation: crisis ? 'pulse 1.5s ease-in-out infinite' : 'none',
          }} />
        </div>
      </div>

      <div style={{ marginTop: 8, color: '#6b7280', fontSize: 10 }}>
        Phase: <span style={{ color: '#9ca3af', textTransform: 'capitalize' }}>{gameState.railway_party.phase}</span>
        {' · '}Activates at {gameState.railway_party.activation_threshold}
      </div>
    </div>
  )
}
