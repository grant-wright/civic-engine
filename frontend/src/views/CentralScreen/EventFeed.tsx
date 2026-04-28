import type { components } from '../../types'

type GameEventType = components['schemas']['GameEventType']
type GameEvent = components['schemas']['GameEvent']

import { useGameState } from '../../hooks/useGameState'

function eventColor(type: GameEventType): string {
  if (['milestone_bronze', 'milestone_silver', 'milestone_gold', 'segment_complete', 'waypoint_complete', 'engineering_feat'].includes(type))
    return '#f59e0b'
  if (['railway_crisis', 'canal_mania', 'canal_mania_burst', 'game_over', 'waypoint_blocked'].includes(type))
    return '#ef4444'
  if (type === 'agent_success') return '#22c55e'
  if (type === 'agent_failure') return '#ef4444'
  if (['election_survived', 'network_effect'].includes(type)) return '#a78bfa'
  if (['council_extension', 'major_decision'].includes(type)) return '#f59e0b'
  if (type === 'railway_activated') return '#fca5a5'
  return '#6b7280'
}

function eventLabel(type: GameEventType): string {
  return type.replace(/_/g, ' ')
}

function EventRow({ event }: { event: GameEvent }) {
  const color = eventColor(event.event_type)
  return (
    <div style={{ display: 'flex', gap: 8, padding: '5px 0', borderBottom: '1px solid #1f2028' }}>
      <div style={{ marginTop: 5, flexShrink: 0, width: 7, height: 7, borderRadius: '50%', background: color }} />
      <div style={{ minWidth: 0 }}>
        <div style={{ color: '#9ca3af', fontSize: 10, marginBottom: 1 }}>
          <span style={{ color }}>C{event.cycle} T{event.turn}</span>
          {' '}
          <span style={{ textTransform: 'capitalize' }}>{eventLabel(event.event_type)}</span>
        </div>
        <div style={{ color: '#d1d5db', fontSize: 11, lineHeight: 1.3, wordBreak: 'break-word' }}>
          {event.description}
        </div>
      </div>
    </div>
  )
}

export default function EventFeed() {
  const gameState = useGameState()
  if (!gameState) return null

  const events = [...gameState.event_log].reverse()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div style={{ padding: '10px 14px 6px', color: '#f3f4f6', fontWeight: 600, fontSize: 12, textTransform: 'uppercase', letterSpacing: 1, flexShrink: 0 }}>
        Events
        <span style={{ color: '#6b7280', fontWeight: 400, fontSize: 10, marginLeft: 6 }}>({events.length})</span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 14px 12px' }}>
        {events.length === 0 ? (
          <div style={{ color: '#6b7280', fontSize: 11, marginTop: 8 }}>No events yet.</div>
        ) : (
          events.map(e => <EventRow key={e.event_id} event={e} />)
        )}
      </div>
    </div>
  )
}
