import { useGameContext } from '../../store'
import socket from '../../socket'

export default function ExtensionButton() {
  const { gameState } = useGameContext()
  const remaining = gameState?.council_extensions_remaining ?? 0
  const disabled = remaining === 0

  return (
    <button
      disabled={disabled}
      onClick={() => socket.emit('council_extension')}
      title="Add 30 seconds to the council turn"
      style={{
        padding: '0.35rem 0.7rem',
        background: disabled ? '#e5e7eb' : '#3b82f6',
        color: disabled ? '#9ca3af' : 'white',
        border: 'none',
        borderRadius: 6,
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '0.8rem',
        whiteSpace: 'nowrap',
      }}
    >
      +30s ({remaining})
    </button>
  )
}
