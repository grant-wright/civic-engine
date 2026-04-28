import { useState } from 'react'

export default function VoiceButton() {
  const [showHint, setShowHint] = useState(false)

  function handleClick() {
    setShowHint(true)
    setTimeout(() => setShowHint(false), 2000)
  }

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onClick={handleClick}
        style={{
          padding: '0.35rem 0.7rem',
          background: '#f3f4f6',
          border: '1px solid #d1d5db',
          borderRadius: 6,
          cursor: 'pointer',
          fontSize: '0.8rem',
        }}
      >
        🎙 Voice
      </button>
      {showHint && (
        <div style={{
          position: 'absolute',
          bottom: '110%',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#1f2937',
          color: 'white',
          padding: '0.4rem 0.7rem',
          borderRadius: 6,
          fontSize: '0.75rem',
          whiteSpace: 'nowrap',
          zIndex: 10,
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
        }}>
          Voice commands coming in step 11
        </div>
      )}
    </div>
  )
}
