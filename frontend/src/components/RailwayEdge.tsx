import { getStraightPath, BaseEdge } from '@xyflow/react'
import type { EdgeProps } from '@xyflow/react'

export default function RailwayEdge({ id, sourceX, sourceY, targetX, targetY }: EdgeProps) {
  const [edgePath] = getStraightPath({ sourceX, sourceY, targetX, targetY })
  return (
    <BaseEdge
      id={id}
      path={edgePath}
      style={{ stroke: '#7f1d1d', strokeWidth: 3 }}
    />
  )
}
