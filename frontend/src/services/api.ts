import axios from 'axios'
import { message } from 'antd'

// 生成UUID v4
const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

// 创建Axios实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 180000, // 延长超时到180秒，适配LLM生成案件的时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 生成追踪ID
    const requestId = generateUUID()
    config.headers['X-Request-ID'] = requestId

    console.log(`[api] 请求发送 [${requestId}]:`, {
      url: config.url,
      method: config.method,
      baseURL: config.baseURL,
      fullUrl: `${config.baseURL}${config.url}`,
      params: config.params,
      data: config.data,
    })
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    const requestId = error.config?.headers?.['X-Request-ID'] || 'unknown'
    console.error(`[api] 请求错误 [${requestId}]:`, error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const requestId = response.headers['x-request-id'] || response.config.headers?.['X-Request-ID'] || 'unknown'
    console.log(`[api] 响应接收 [${requestId}]:`, {
      url: response.config.url,
      status: response.status,
      data: response.data,
    })
    const res = response.data
    // 如果返回的是错误格式
    if (res.code && res.code !== 200) {
      console.error(`[api] API返回错误 [${requestId}]:`, res)
      message.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    const requestId = error.config?.headers?.['X-Request-ID'] || 'unknown'
    console.error(`[api] 响应错误 [${requestId}]:`, {
      message: error.message,
      config: error.config,
      response: error.response,
      request: error.request,
    })
    let errorMessage = '网络错误，请稍后重试'

    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          errorMessage = data.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          break
        case 403:
          errorMessage = '禁止访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求失败 (${status})`
      }
    } else if (error.request) {
      errorMessage = '服务器无响应，请检查网络连接'
    }

    message.error(errorMessage)
    return Promise.reject(error)
  }
)

export default request
