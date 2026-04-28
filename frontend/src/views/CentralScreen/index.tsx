import CityMap from './CityMap'

export default function CentralScreen() {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      display: 'flex',
      flexDirection: 'row',
      overflow: 'hidden',
      background: '#0f1117',
    }}>
      <div style={{ flex: 1, minWidth: 0, minHeight: 0 }}>
        <CityMap />
      </div>
      <div style={{
        width: 300,
        background: '#1a1b23',
        borderLeft: '1px solid #2e303a',
        padding: '1rem',
        color: '#9ca3af',
        fontSize: 14,
        overflowY: 'auto',
        flexShrink: 0,
      }}>
        <div style={{ color: '#f3f4f6', fontWeight: 600, marginBottom: 8 }}>Dashboard</div>
        <p>Metrics, influence meter, and event feed coming in step 7.</p>
      </div>
    </div>
  )
}
