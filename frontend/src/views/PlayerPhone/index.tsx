import { useState, useEffect } from 'react'
import { useGameContext } from '../../store'
import ReportQueue from './ReportQueue'
import ReportCard from './ReportCard'
import TurnTimer from './TurnTimer'
import ExtensionButton from './ExtensionButton'
import VoiceButton from './VoiceButton'

const ROLE_COLORS: Record<string, string> = {
  transport: '#3b82f6',
  finance: '#7c3aed',
  infrastructure: '#d97706',
}

export default function PlayerPhone() {
  const { gameState, playerIdentity } = useGameContext()
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null)

  if (!gameState) {
    return <div style={{ padding: '2rem', color: '#9ca3af', textAlign: 'center' }}>Connecting to game...</div>
  }

  const player = gameState.players[playerIdentity.player_id]
  if (!player) {
    return <div style={{ padding: '2rem', color: '#9ca3af', textAlign: 'center' }}>Player not found — check localStorage player_id</div>
  }

  const myReports = gameState.pending_reports?.[playerIdentity.player_id] ?? []
  const selectedReport = myReports.find(r => r.report_id === selectedReportId) ?? null
  const roleColor = ROLE_COLORS[player.role] ?? '#6b7280'

  // Auto-close ReportCard when the selected report is no longer pending
  // (covers voice dispatch, manual click, and AI deciding the report)
  useEffect(() => {
    if (selectedReport && selectedReport.status !== 'pending') {
      setSelectedReportId(null)
    }
  }, [selectedReport?.status])

  function toggleReport(id: string) {
    setSelectedReportId(prev => prev === id ? null : id)
  }

  return (
    <div style={{ maxWidth: 480, margin: '0 auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'white', padding: '0.75rem 1rem', borderRadius: 10, border: '1px solid #e5e7eb',
        flexWrap: 'wrap', gap: 8,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{
            background: roleColor, color: 'white', borderRadius: 6,
            padding: '2px 10px', fontSize: '0.78rem', textTransform: 'capitalize',
          }}>
            {player.role}
          </span>
          <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{player.councillor.name}</span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <TurnTimer />
          <ExtensionButton />
          <VoiceButton reportId={selectedReportId} />
        </div>
      </div>

      {/* Report queue */}
      <ReportQueue
        reports={myReports}
        selectedId={selectedReportId}
        onSelect={toggleReport}
      />

      {/* Report detail (shown when a report is selected) */}
      {selectedReport && (
        <ReportCard
          report={selectedReport}
          player={player}
          onClose={() => setSelectedReportId(null)}
        />
      )}
    </div>
  )
}
