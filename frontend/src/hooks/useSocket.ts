import { useEffect } from 'react'
import socket from '../socket'
import { useGameContext } from '../store'

export function useSocket() {
  const { playerIdentity } = useGameContext()

  useEffect(() => {
    function onConnect() {
      socket.emit('register', {
        client_type: 'player',
        player_id: playerIdentity.player_id,
        role: playerIdentity.role,
        session_id: playerIdentity.session_id,
      })
    }

    socket.on('connect', onConnect)
    if (socket.connected) onConnect()

    return () => {
      socket.off('connect', onConnect)
    }
  }, [playerIdentity])
}
