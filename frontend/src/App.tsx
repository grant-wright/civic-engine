import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useSocket } from './hooks/useSocket'
import CentralScreen from './views/CentralScreen'
import PlayerPhone from './views/PlayerPhone'

function AppInner() {
  useSocket()
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/central" element={<CentralScreen />} />
        <Route path="/phone" element={<PlayerPhone />} />
        <Route path="*" element={<Navigate to="/central" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default function App() {
  return <AppInner />
}
