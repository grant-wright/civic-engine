import { Handle, Position } from '@xyflow/react'
import type { NodeProps } from '@xyflow/react'
import type { components } from '../types'

type MapNode = components['schemas']['MapNode']

const NODE_TYPE_COLORS: Record<string, string> = {
  port: '#3b82f6',
  industrial: '#f97316',
  residential: '#22c55e',
  commercial: '#a855f7',
  market: '#eab308',
}

const handleStyle = { opacity: 0, pointerEvents: 'none' as const, width: 6, height: 6 }

export default function DistrictNode({ data }: NodeProps) {
  const node = data as unknown as MapNode
  const color = NODE_TYPE_COLORS[node.node_type] ?? '#9ca3af'

  return (
    <div style={{
      background: '#1a1b23',
      border: `2px solid ${color}`,
      borderRadius: 6,
      padding: '4px 8px',
      minWidth: 80,
      textAlign: 'center',
      fontSize: 11,
      color: '#f3f4f6',
      boxShadow: '0 2px 6px rgba(0,0,0,0.5)',
      cursor: 'default',
    }}>
      <Handle id="top"    type="source" position={Position.Top}    style={handleStyle} />
      <Handle id="right"  type="source" position={Position.Right}  style={handleStyle} />
      <Handle id="bottom" type="source" position={Position.Bottom} style={handleStyle} />
      <Handle id="left"   type="source" position={Position.Left}   style={handleStyle} />

      <div style={{ fontWeight: 700, fontSize: 11, marginBottom: 2 }}>{node.name}</div>
      <span style={{
        background: color,
        color: '#fff',
        borderRadius: 3,
        padding: '1px 4px',
        fontSize: 8,
        textTransform: 'uppercase',
        letterSpacing: 0.4,
      }}>{node.node_type}</span>
      {node.has_railway_station && (
        <div style={{ fontSize: 9, marginTop: 2, color: '#fbbf24' }}>🚂 station</div>
      )}
      {node.has_canal_wharf && (
        <div style={{ fontSize: 9, color: '#60a5fa' }}>⚓ wharf</div>
      )}
    </div>
  )
}
