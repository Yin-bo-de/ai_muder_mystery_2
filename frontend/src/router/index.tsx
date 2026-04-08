import { createBrowserRouter } from 'react-router-dom'
import AppWrapper from '@/App'
import Home from '@/pages/Home'
import Game from '@/pages/Game'
import Investigation from '@/pages/Investigation'
import Interrogation from '@/pages/Interrogation'
import ClueLibrary from '@/pages/ClueLibrary'
import Accuse from '@/pages/Accuse'
import Report from '@/pages/Report'
import GameLayout from '@/components/Layout/GameLayout'

// 页面包装组件 - 独立包装GameLayout
const InvestigationPage = () => (
  <GameLayout>
    <Investigation />
  </GameLayout>
)

const InterrogationPage = () => (
  <GameLayout>
    <Interrogation />
  </GameLayout>
)

const ClueLibraryPage = () => (
  <GameLayout>
    <ClueLibrary />
  </GameLayout>
)

const AccusePage = () => (
  <GameLayout>
    <Accuse />
  </GameLayout>
)

const ReportPage = () => (
  <GameLayout>
    <Report />
  </GameLayout>
)

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppWrapper />,
    children: [
      { index: true, element: <Home /> },
      { path: 'game', element: <Game /> },
      { path: 'investigation', element: <InvestigationPage /> },
      { path: 'interrogation', element: <InterrogationPage /> },
      { path: 'clues', element: <ClueLibraryPage /> },
      { path: 'accuse', element: <AccusePage /> },
      { path: 'report', element: <ReportPage /> },
    ],
  },
])
