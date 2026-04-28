import { useState, useEffect, useRef } from 'react'
import { useGameContext } from '../../store'
import socket from '../../socket'

export default function TurnTimer() {
  const { gameState } = useGameContext()
  const [timeLeft, setTimeLeft] = useState<number | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    function onTurnStarted({ duration }: { duration: number }) {
      if (intervalRef.current) clearInterval(intervalRef.current)
      setTimeLeft(duration)
      intervalRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev === null || prev <= 1) {
            if (intervalRef.current) clearInterval(intervalRef.current)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    socket.on('turn_started', onTurnStarted)
    return () => {
      socket.off('turn_started', onTurnStarted)
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  const display = timeLeft !== null ? timeLeft : (gameState?.turn_time_limit ?? 40)
  const isLow = timeLeft !== null && timeLeft < 10

  return (
    <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: isLow ? '#dc2626' : '#374151', minWidth: 48 }}>
      {display}s
    </div>
  )
}
