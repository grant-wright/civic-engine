import { io } from 'socket.io-client'

const socket = io('http://localhost:8000', {
  autoConnect: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5,
})

export default socket
