import { ReactFlow, Background, ConnectionMode } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { Node, Edge } from '@xyflow/react'
import { useGameContext } from '../../store'
import DistrictNode from '../../components/DistrictNode'
import CanalEdge from '../../components/CanalEdge'
import RailwayEdge from '../../components/RailwayEdge'
import type { components } from '../../types'

type CityMap = components['schemas']['CityMap']

const WIDTH = 700
const HEIGHT = 500

const nodeTypes = { districtNode: DistrictNode }
const edgeTypes = { canalEdge: CanalEdge, railwayEdge: RailwayEdge }

function edgeHandles(fromId: string, toId: string, cityMap: CityMap) {
  const from = cityMap.nodes[fromId]
  const to = cityMap.nodes[toId]
  if (!from || !to) return {}
  const dx = to.position[0] - from.position[0]
  const dy = to.position[1] - from.position[1]
  if (Math.abs(dx) >= Math.abs(dy)) {
    return {
      sourceHandle: dx >= 0 ? 'right' : 'left',
      targetHandle: dx >= 0 ? 'left' : 'right',
    }
  } else {
    return {
      sourceHandle: dy >= 0 ? 'bottom' : 'top',
      targetHandle: dy >= 0 ? 'top' : 'bottom',
    }
  }
}

export default function CityMap() {
  const { gameState } = useGameContext()

  if (!gameState) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        color: '#6b7280',
        background: '#0f1117',
      }}>
        Waiting for game state...
      </div>
    )
  }

  const cityMap = gameState.city_map

  const nodes: Node[] = Object.values(cityMap.nodes).map(n => ({
    id: n.node_id,
    position: { x: n.position[0] * WIDTH, y: n.position[1] * HEIGHT },
    type: 'districtNode',
    data: n as unknown as Record<string, unknown>,
  }))

  const canalEdges: Edge[] = Object.values(cityMap.canal_segments).map(seg => ({
    id: seg.segment_id,
    source: seg.from_node,
    target: seg.to_node,
    type: 'canalEdge',
    data: { segment: seg } as Record<string, unknown>,
    ...edgeHandles(seg.from_node, seg.to_node, cityMap),
  }))

  const railwayEdges: Edge[] = (cityMap.railway_segments ?? []).map(seg => ({
    id: seg.segment_id,
    source: seg.from_node,
    target: seg.to_node,
    type: 'railwayEdge',
    data: { segment: seg } as Record<string, unknown>,
    ...edgeHandles(seg.from_node, seg.to_node, cityMap),
  }))

  return (
    <div style={{ width: '100%', height: '100%', background: '#0f1117' }}>
      <ReactFlow
        nodes={nodes}
        edges={[...canalEdges, ...railwayEdges]}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1f2028" gap={24} />
      </ReactFlow>
    </div>
  )
}
