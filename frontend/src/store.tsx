import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import type { components } from './types'
import socket from './socket'

export type GameState = components['schemas']['GameState']

export interface PlayerIdentity {
  player_id: string
  role: string
  session_id: string
}

interface GameContextValue {
  gameState: GameState | null
  playerIdentity: PlayerIdentity
  setPlayerIdentity: (identity: PlayerIdentity) => void
}

const GameContext = createContext<GameContextValue | null>(null)

function loadIdentity(): PlayerIdentity {
  const session_id = localStorage.getItem('session_id') ?? crypto.randomUUID()
  if (!localStorage.getItem('session_id')) {
    localStorage.setItem('session_id', session_id)
  }
  return {
    player_id: localStorage.getItem('player_id') ?? 'player_transport',
    role: localStorage.getItem('role') ?? 'transport',
    session_id,
  }
}

export function GameStateProvider({ children }: { children: ReactNode }) {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [playerIdentity, setPlayerIdentityState] = useState<PlayerIdentity>(loadIdentity)

  function setPlayerIdentity(identity: PlayerIdentity) {
    localStorage.setItem('player_id', identity.player_id)
    localStorage.setItem('role', identity.role)
    localStorage.setItem('session_id', identity.session_id)
    setPlayerIdentityState(identity)
  }

  useEffect(() => {
    socket.on('game_state_update', setGameState)
    return () => {
      socket.off('game_state_update', setGameState)
    }
  }, [])

  return (
    <GameContext.Provider value={{ gameState, playerIdentity, setPlayerIdentity }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGameContext() {
  const ctx = useContext(GameContext)
  if (!ctx) throw new Error('useGameContext must be used within GameStateProvider')
  return ctx
}
