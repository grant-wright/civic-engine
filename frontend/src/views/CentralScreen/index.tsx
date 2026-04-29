import CityMap from './CityMap'
import MetricsDash from './MetricsDash'
import InfluenceMeter from './InfluenceMeter'
import EventFeed from './EventFeed'
import VotePanel from './VotePanel'
import DevPanel from '../../components/DevPanel'

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
        width: 360,
        background: '#1a1b23',
        borderLeft: '1px solid #2e303a',
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}>
        <VotePanel />
        <InfluenceMeter />
        <MetricsDash />
        <EventFeed />
      </div>
      <DevPanel />
    </div>
  )
}
