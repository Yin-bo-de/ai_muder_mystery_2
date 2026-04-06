import { Outlet } from 'react-router-dom'
import { ConfigProvider, theme, App } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import './App.css'

function AppWrapper() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#722ed1',
          borderRadius: 8,
          colorBgContainer: '#141414',
          colorBgElevated: '#1f1f1f',
        },
      }}
    >
      <App>
        <Outlet />
      </App>
    </ConfigProvider>
  )
}

export default AppWrapper
