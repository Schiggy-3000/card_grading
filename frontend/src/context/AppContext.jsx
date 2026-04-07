import { createContext, useContext, useState } from 'react'
import { v4 as uuidv4 } from 'uuid'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [gradingStandard, setGradingStandardState] = useState(
    () => localStorage.getItem('gradingStandard') || 'psa'
  )
  const [sessionHistory, setSessionHistory] = useState([])

  function setGradingStandard(std) {
    localStorage.setItem('gradingStandard', std)
    setGradingStandardState(std)
  }

  function addHistoryEntry({ tool, cardName, result }) {
    setSessionHistory(prev => [{
      id: uuidv4(),
      tool,
      timestamp: new Date().toISOString(),
      cardName: cardName || null,
      result,
    }, ...prev])
  }

  return (
    <AppContext.Provider value={{
      gradingStandard,
      setGradingStandard,
      sessionHistory,
      addHistoryEntry,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
