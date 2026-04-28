import type { components } from '../../types'

type Agent = components['schemas']['Agent']

interface Props {
  agents: Agent[]
  onSelect: (agentId: string) => void
  onClose: () => void
}

function riskLabel(profile: number): string {
  if (profile < 0.35) return 'Low'
  if (profile > 0.65) return 'High'
  return 'Medium'
}

function riskColor(profile: number): string {
  if (profile < 0.35) return '#16a34a'
  if (profile > 0.65) return '#dc2626'
  return '#d97706'
}

export default function AgentRoster({ agents, onSelect, onClose }: Props) {
  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 100,
    }}>
      <div style={{
        background: 'white', borderRadius: 12, padding: '1.5rem',
        maxWidth: 400, width: '90%', maxHeight: '80vh', overflowY: 'auto',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0, fontSize: '1rem' }}>Delegate to Agent</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem', color: '#9ca3af' }}>✕</button>
        </div>

        {agents.length === 0 ? (
          <p style={{ color: '#9ca3af', fontStyle: 'italic' }}>No agents available for this domain.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {agents.map(agent => (
              <div
                key={agent.agent_id}
                onClick={() => { onSelect(agent.agent_id); onClose() }}
                style={{
                  padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: 8,
                  cursor: 'pointer', background: '#f9fafb',
                  transition: 'background 0.1s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = '#eff6ff')}
                onMouseLeave={e => (e.currentTarget.style.background = '#f9fafb')}
              >
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{agent.name}</div>
                <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: 6 }}>
                  {agent.specialisations.join(', ')}
                </div>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.78rem' }}>
                  <span style={{ color: riskColor(agent.risk_profile) }}>
                    Risk: {riskLabel(agent.risk_profile)}
                  </span>
                  <span style={{ color: '#6b7280' }}>Track record: {agent.track_record}</span>
                  <span style={{ color: '#374151', marginLeft: 'auto' }}>£{agent.hiring_cost}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
