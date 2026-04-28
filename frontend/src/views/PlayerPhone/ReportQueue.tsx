import type { components } from '../../types'

type Report = components['schemas']['Report']

interface Props {
  reports: Report[]
  selectedId: string | null
  onSelect: (id: string) => void
}

const DOMAIN_COLORS: Record<string, string> = {
  transport: '#3b82f6',
  finance: '#7c3aed',
  infrastructure: '#d97706',
}

export default function ReportQueue({ reports, selectedId, onSelect }: Props) {
  const pending = [...reports]
    .filter(r => r.status === 'pending')
    .sort((a, b) => {
      if (a.urgent !== b.urgent) return a.urgent ? -1 : 1
      return a.turn_deadline - b.turn_deadline
    })

  if (pending.length === 0) {
    return (
      <div style={{ padding: '1.5rem', color: '#9ca3af', fontStyle: 'italic', textAlign: 'center', background: 'white', borderRadius: 10, border: '1px solid #e5e7eb' }}>
        No pending reports
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {pending.map(report => (
        <div
          key={report.report_id}
          onClick={() => onSelect(report.report_id)}
          style={{
            padding: '0.75rem',
            borderRadius: 8,
            border: report.urgent ? '2px solid #dc2626' : '1px solid #e5e7eb',
            background: selectedId === report.report_id ? '#eff6ff' : 'white',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{report.title}</span>
            {report.defer_count > 0 && (
              <span style={{ background: '#fef3c7', color: '#92400e', borderRadius: 4, padding: '1px 6px', fontSize: '0.72rem' }}>
                Deferred ×{report.defer_count}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{
              background: DOMAIN_COLORS[report.domain] ?? '#6b7280',
              color: 'white',
              borderRadius: 4,
              padding: '1px 8px',
              fontSize: '0.72rem',
              textTransform: 'capitalize',
            }}>
              {report.domain}
            </span>
            {report.urgent && (
              <span style={{ color: '#dc2626', fontSize: '0.72rem', fontWeight: 700 }}>URGENT</span>
            )}
            <span style={{ color: '#9ca3af', fontSize: '0.72rem', marginLeft: 'auto' }}>
              Due turn {report.turn_deadline}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
