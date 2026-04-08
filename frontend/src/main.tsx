import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import App from './App'
import './index.css'

// 添加全局错误处理
window.addEventListener('error', (event) => {
  console.error('[全局错误] 未捕获的错误:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('[全局错误] 未处理的Promise拒绝:', event.reason)
})

console.log('[main] 应用启动，开始挂载React')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)

console.log('[main] React已挂载完成')
