import { useGameState } from '../../hooks/useGameState'

export default function VotePanel() {
  const gameState = useGameState()
  if (!gameState?.pending_vote) return null

  const vote = gameState.pending_vote
  const totalVotes = Object.keys(vote.votes).length

  return (
    <div style={{
      margin: '10px 14px',
      border: '1px solid #f59e0b',
      borderRadius: 6,
      background: '#1c1a0e',
      padding: '10px 12px',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ color: '#fcd34d', fontWeight: 700, fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Council Vote
        </div>
        {vote.mayor_tiebreaker && (
          <div style={{ background: '#451a03', color: '#fdba74', fontSize: 10, padding: '2px 6px', borderRadius: 3 }}>
            MAYOR TIEBREAKER
          </div>
        )}
      </div>

      <div style={{ color: '#9ca3af', fontSize: 10, marginBottom: 8 }}>
        {totalVotes} vote{totalVotes !== 1 ? 's' : ''} cast · {vote.status}
      </div>

      {vote.options.map(opt => {
        const count = Object.values(vote.votes).filter(v => v === opt.option_id).length
        return (
          <div key={opt.option_id} style={{ marginBottom: 6, padding: '6px 8px', background: '#2e303a', borderRadius: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <span style={{ color: '#f3f4f6', fontSize: 11, fontWeight: 600 }}>{opt.label}</span>
              <span style={{ color: '#f59e0b', fontSize: 11, fontWeight: 700 }}>{count}</span>
            </div>
            <div style={{ color: '#9ca3af', fontSize: 10 }}>{opt.description}</div>
          </div>
        )
      })}

      {vote.result && (
        <div style={{ marginTop: 8, color: '#22c55e', fontSize: 11, fontWeight: 600 }}>
          Result: {vote.result}
        </div>
      )}
    </div>
  )
}
