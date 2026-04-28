import type { components } from '../types'

type Waypoint = components['schemas']['Waypoint']
type WaypointStatus = components['schemas']['WaypointStatus']

const STATUS_COLORS: Record<WaypointStatus, string> = {
  unstarted: '#6b7280',
  under_construction: '#f59e0b',
  complete: '#10b981',
  blocked: '#ef4444',
  contested: '#f97316',
}

interface WaypointMarkerProps {
  x: number
  y: number
  waypoint: Waypoint
}

export default function WaypointMarker({ x, y, waypoint }: WaypointMarkerProps) {
  const color = STATUS_COLORS[waypoint.status as WaypointStatus] ?? '#6b7280'
  return (
    <g>
      <circle cx={x} cy={y} r={5} fill={color} stroke="#0f1117" strokeWidth={1.5} />
      <title>{waypoint.name} · {waypoint.status.replace('_', ' ')}</title>
    </g>
  )
}
