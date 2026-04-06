import { createBrowserRouter } from 'react-router-dom'
import App from '@/App'
import Home from '@/pages/Home'
import Game from '@/pages/Game'
import Investigation from '@/pages/Investigation'
import Interrogation from '@/pages/Interrogation'
import ClueLibrary from '@/pages/ClueLibrary'
import Accuse from '@/pages/Accuse'
import Report from '@/pages/Report'
import GameLayout from '@/components/Layout/GameLayout'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: 'game', element: <Game /> },
      {
        element: <GameLayout />,
        children: [
          { path: 'investigation', element: <Investigation /> },
          { path: 'interrogation', element: <Interrogation /> },
          { path: 'clues', element: <ClueLibrary /> },
          { path: 'accuse', element: <Accuse /> },
          { path: 'report', element: <Report /> },
        ],
      },
    ],
  },
])
