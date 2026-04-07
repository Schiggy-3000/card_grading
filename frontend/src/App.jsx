import { HashRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Identify from './pages/Identify'
import Grade from './pages/Grade'
import History from './pages/History'

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/identify" element={<Identify />} />
        <Route path="/grade" element={<Grade />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </HashRouter>
  )
}
