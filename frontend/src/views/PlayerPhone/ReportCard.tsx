import { useState } from 'react'
import type { components } from '../../types'
import socket from '../../socket'
import { useGameContext } from '../../store'
import AgentRoster from './AgentRoster'

type Report = components['schemas']['Report']
type Player = components['schemas']['Player']
type ReportOption = components['schemas']['ReportOption']
type Councillor = components['schemas']['Councillor']

interface Props {
  report: Report
  player: Player
  onClose: () => void
}

const RISK_COLORS: Record<string, string> = {
  low: '#16a34a',
  medium: '#d97706',
  high: '#dc2626',
}

function canSeeOption(option: ReportOption, councillor: Councillor): boolean {
  if (!option.min_skill_level || option.min_skill_level === 0) return true
  if (!option.required_skill) return true
  const skill = councillor.skills.find(s => s.skill_name === option.required_skill)
  return skill !== undefined && skill.level >= option.min_skill_level
}

export default function ReportCard({ report, player, onClose }: Props) {
  const { playerIdentity } = useGameContext()
  const [showAgentRoster, setShowAgentRoster] = useState(false)

  const visibleOptions = report.options.filter(opt => canSeeOption(opt, player.councillor))
  const canDefer = !report.urgent && report.defer_count < 2

  function chooseOption(optionId: string) {
    socket.emit('player_action', {
      player_id: playerIdentity.player_id,
      action_type: 'choose_option',
      target_type: 'report',
      target_id: report.report_id,
      option_id: optionId,
    })
    onClose()
  }

  function delegateToAgent(agentId: string) {
    socket.emit('player_action', {
      player_id: playerIdentity.player_id,
      action_type: 'delegate',
      target_type: 'report',
      target_id: report.report_id,
      option_id: agentId,
    })
    onClose()
  }

  function deferReport() {
    socket.emit('player_action', {
      player_id: playerIdentity.player_id,
      action_type: 'defer',
      target_type: 'report',
      target_id: report.report_id,
      option_id: '',
    })
    onClose()
  }

  function escalateReport() {
    socket.emit('player_action', {
      player_id: playerIdentity.player_id,
      action_type: 'escalate',
      target_type: 'report',
      target_id: report.report_id,
      option_id: '',
    })
    onClose()
  }

  return (
    <div style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: 10, padding: '1rem', position: 'relative' }}>
      {showAgentRoster && (
        <AgentRoster
          agents={player.agents ?? []}
          onSelect={delegateToAgent}
          onClose={() => setShowAgentRoster(false)}
        />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <h3 style={{ margin: 0, fontSize: '1rem', lineHeight: 1.4 }}>{report.title}</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', fontSize: '1.1rem', flexShrink: 0, marginLeft: 8 }}>✕</button>
      </div>

      <p style={{ color: '#4b5563', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>
        {report.description}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: '1rem' }}>
        {visibleOptions.map(opt => (
          <div key={opt.option_id} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '0.65rem 0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{opt.label}</span>
              <span style={{ color: RISK_COLORS[opt.risk_level] ?? '#6b7280', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase' }}>
                {opt.risk_level} risk
              </span>
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.8rem', margin: '0 0 8px', lineHeight: 1.4 }}>{opt.description}</p>
            <button
              onClick={() => chooseOption(opt.option_id)}
              style={{
                padding: '0.3rem 0.8rem', background: '#1d4ed8', color: 'white',
                border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: '0.8rem',
              }}
            >
              Choose
            </button>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', borderTop: '1px solid #f3f4f6', paddingTop: '0.75rem' }}>
        <button
          onClick={() => setShowAgentRoster(true)}
          style={{ padding: '0.35rem 0.75rem', background: '#f3f4f6', border: '1px solid #d1d5db', borderRadius: 6, cursor: 'pointer', fontSize: '0.8rem' }}
        >
          Delegate
        </button>
        {canDefer && (
          <button
            onClick={deferReport}
            style={{ padding: '0.35rem 0.75rem', background: '#f3f4f6', border: '1px solid #d1d5db', borderRadius: 6, cursor: 'pointer', fontSize: '0.8rem' }}
          >
            Defer
          </button>
        )}
        <button
          onClick={escalateReport}
          style={{ padding: '0.35rem 0.75rem', background: '#fef3c7', border: '1px solid #fbbf24', borderRadius: 6, cursor: 'pointer', fontSize: '0.8rem' }}
        >
          Flag for Council
        </button>
      </div>
    </div>
  )
}
