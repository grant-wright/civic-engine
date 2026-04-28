import { useGameContext } from '../store'

export function useGameState() {
  return useGameContext().gameState
}
