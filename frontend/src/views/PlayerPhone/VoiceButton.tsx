import { useState } from 'react'
import { useGameContext } from '../../store'
import { useVoiceInput } from '../../hooks/useVoiceInput'

interface Props {
  reportId: string | null
}

export default function VoiceButton({ reportId }: Props) {
  const { playerIdentity } = useGameContext()
  const [textInput, setTextInput] = useState('')
  const { status, transcript, clarificationPrompt, errorMessage, startListening, confirmTranscript, submitText, reset } =
    useVoiceInput({ playerId: playerIdentity.player_id, reportId })

  function handleTextSubmit() {
    const t = textInput.trim()
    if (t) { submitText(t); setTextInput('') }
  }

  // Clarification / error modal
  if (status === 'clarifying' || status === 'error') {
    return (
      <div style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
      }}>
        <div style={{
          background: 'white', borderRadius: 10, padding: '1.25rem',
          maxWidth: 320, width: '90%', display: 'flex', flexDirection: 'column', gap: 12,
        }}>
          <p style={{ margin: 0, fontWeight: 600 }}>
            {status === 'error' ? 'Voice unavailable' : 'Confirm or rephrase'}
          </p>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
            {status === 'error' ? errorMessage : clarificationPrompt}
          </p>

          {status === 'clarifying' && transcript && (
            <button
              onClick={confirmTranscript}
              style={{
                padding: '0.4rem 0.8rem', background: '#1d4ed8', color: 'white',
                border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: '0.85rem',
              }}
            >
              Yes, proceed
            </button>
          )}

          <p style={{ margin: 0, fontSize: '0.8rem', color: '#9ca3af' }}>
            {status === 'error' ? 'Type your command instead:' : 'Or type a correction:'}
          </p>
          <div style={{ display: 'flex', gap: 6 }}>
            <input
              value={textInput}
              onChange={e => setTextInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleTextSubmit() }}
              placeholder="e.g. choose option one"
              autoFocus
              style={{
                flex: 1, padding: '0.35rem 0.5rem',
                border: '1px solid #d1d5db', borderRadius: 6, fontSize: '0.85rem',
              }}
            />
            <button
              onClick={handleTextSubmit}
              disabled={!textInput.trim()}
              style={{
                padding: '0.35rem 0.6rem', background: '#1d4ed8', color: 'white',
                border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: '0.85rem',
              }}
            >
              Send
            </button>
          </div>
          <button
            onClick={reset}
            style={{ padding: '0.3rem', background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: '0.8rem' }}
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  // Listening state — pulsing red button to cancel
  if (status === 'listening') {
    return (
      <button
        onClick={reset}
        style={{
          padding: '0.35rem 0.7rem',
          background: '#fee2e2', border: '2px solid #dc2626',
          borderRadius: 6, cursor: 'pointer', fontSize: '0.8rem',
        }}
      >
        🔴 Listening…
      </button>
    )
  }

  // Idle / processing
  return (
    <button
      onClick={startListening}
      disabled={status === 'processing' || !reportId}
      title={!reportId ? 'Select a report first' : 'Speak a command'}
      style={{
        padding: '0.35rem 0.7rem',
        background: '#f3f4f6', border: '1px solid #d1d5db',
        borderRadius: 6, fontSize: '0.8rem',
        cursor: reportId && status !== 'processing' ? 'pointer' : 'not-allowed',
        opacity: !reportId ? 0.5 : 1,
      }}
    >
      {status === 'processing' ? '⏳' : '🎙 Voice'}
    </button>
  )
}
