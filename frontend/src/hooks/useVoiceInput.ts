import { useState, useRef, useCallback, useEffect } from 'react'
import socket from '../socket'

export type VoiceStatus = 'idle' | 'listening' | 'processing' | 'clarifying' | 'error'

export interface VoiceState {
  status: VoiceStatus
  transcript: string
  clarificationPrompt: string | null
  errorMessage: string | null
}

interface UseVoiceInputOptions {
  playerId: string
  reportId: string | null
}

export function useVoiceInput({ playerId, reportId }: UseVoiceInputOptions) {
  const [state, setState] = useState<VoiceState>({
    status: 'idle',
    transcript: '',
    clarificationPrompt: null,
    errorMessage: null,
  })
  const recognitionRef = useRef<any>(null)
  // Ref so confirmTranscript can read the current transcript without stale closures
  // and without putting socket.emit inside a setState updater (Strict Mode double-fires those)
  const transcriptRef = useRef('')

  // Listen for server-side clarification requests
  useEffect(() => {
    function onClarification(data: { prompt: string; transcript: string }) {
      setState(s => ({ ...s, status: 'clarifying', clarificationPrompt: data.prompt }))
    }
    socket.on('voice_clarification', onClarification)
    return () => { socket.off('voice_clarification', onClarification) }
  }, [])

  const startListening = useCallback(() => {
    const SpeechRecognition =
      (window as any).webkitSpeechRecognition ?? (window as any).SpeechRecognition
    if (!SpeechRecognition) {
      setState(s => ({
        ...s,
        status: 'error',
        errorMessage: 'Speech recognition requires Chrome or Edge.',
      }))
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-NZ'
    recognition.continuous = false
    recognition.interimResults = false
    recognitionRef.current = recognition

    recognition.onstart = () => {
      setState(s => ({ ...s, status: 'listening', errorMessage: null }))
    }

    recognition.onresult = (event: any) => {
      const result = event.results[0]
      const transcript: string = result[0].transcript
      const confidence: number = result[0].confidence ?? 1.0

      transcriptRef.current = transcript
      setState(s => ({ ...s, transcript }))

      if (confidence < 0.6) {
        // Low confidence — ask the player to confirm before sending
        setState(s => ({
          ...s,
          status: 'clarifying',
          clarificationPrompt: `Did you say: "${transcript}"?`,
        }))
      } else {
        setState(s => ({ ...s, status: 'processing' }))
        socket.emit('voice_command', { player_id: playerId, transcript, report_id: reportId })
        setState(s => ({ ...s, status: 'idle' }))
      }
    }

    recognition.onerror = (event: any) => {
      const msg =
        event.error === 'not-allowed'
          ? 'Microphone access denied.'
          : event.error === 'no-speech'
          ? 'No speech detected. Try again.'
          : 'Voice recognition error.'
      setState(s => ({ ...s, status: 'error', errorMessage: msg }))
    }

    recognition.onend = () => {
      // Only revert to idle if we haven't already moved to another state
      setState(s => (s.status === 'listening' ? { ...s, status: 'idle' } : s))
    }

    recognition.start()
  }, [playerId, reportId])

  const confirmTranscript = useCallback(() => {
    const t = transcriptRef.current
    if (t) {
      socket.emit('voice_command', { player_id: playerId, transcript: t, report_id: reportId })
    }
    setState(s => ({ ...s, status: 'idle', clarificationPrompt: null }))
  }, [playerId, reportId])

  const submitText = useCallback((text: string) => {
    socket.emit('voice_command', { player_id: playerId, transcript: text, report_id: reportId })
    setState(s => ({ ...s, status: 'idle', clarificationPrompt: null, transcript: '' }))
  }, [playerId, reportId])

  const reset = useCallback(() => {
    recognitionRef.current?.abort()
    setState({ status: 'idle', transcript: '', clarificationPrompt: null, errorMessage: null })
  }, [])

  return { ...state, startListening, confirmTranscript, submitText, reset }
}
