import { getStraightPath, BaseEdge } from '@xyflow/react'
import type { EdgeProps } from '@xyflow/react'
import WaypointMarker from './WaypointMarker'
import type { components } from '../types'

type CanalSegment = components['schemas']['CanalSegment']
type SegmentStatus = components['schemas']['SegmentStatus']

const SEGMENT_COLORS: Record<SegmentStatus, string> = {
  proposed: '#6b7280',
  approved: '#a78bfa',
  under_construction: '#f59e0b',
  complete: '#3b82f6',
}

interface CanalEdgeData {
  segment: CanalSegment
}

export default function CanalEdge({
  id, sourceX, sourceY, targetX, targetY, data
}: EdgeProps) {
  const { segment } = (data ?? {}) as CanalEdgeData
  const status = (segment?.status ?? 'proposed') as SegmentStatus
  const color = SEGMENT_COLORS[status] ?? '#6b7280'
  const dashed = status === 'proposed'

  const [edgePath] = getStraightPath({ sourceX, sourceY, targetX, targetY })
  const waypoints = segment?.waypoints ?? []

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: color,
          strokeWidth: dashed ? 1.5 : 2.5,
          strokeDasharray: dashed ? '6 4' : undefined,
        }}
      />
      {waypoints.map((wp, i) => {
        const t = (i + 1) / (waypoints.length + 1)
        const x = sourceX + (targetX - sourceX) * t
        const y = sourceY + (targetY - sourceY) * t
        return <WaypointMarker key={wp.waypoint_id} x={x} y={y} waypoint={wp} />
      })}
    </>
  )
}
