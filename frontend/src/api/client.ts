const BASE = '/api'
const REQUEST_TIMEOUT_MS = 8000

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function parseErrorMessage(res: Response): Promise<string> {
  const data = await res.json().catch(() => ({}))
  const detail = data.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join('；')
  }
  return `请求失败 (${res.status})`
}

async function fetchWithTimeout(url: string, options?: RequestInit): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  try {
    return await fetch(url, {
      credentials: 'include',
      ...options,
      signal: options?.signal ?? controller.signal
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('无法连接后端服务，请确认后端已启动', 0)
    }
    throw new ApiError('网络请求失败，请检查前后端是否均已启动', 0)
  } finally {
    window.clearTimeout(timeoutId)
  }
}

export async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers)
  if (
    options?.body &&
    typeof options.body === 'string' &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json')
  }

  const res = await fetchWithTimeout(`${BASE}${url}`, {
    ...options,
    headers
  })

  if (res.status === 204) {
    return undefined as T
  }

  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status)
  }

  return res.json() as Promise<T>
}

export async function downloadBlob(url: string, filename: string, options?: RequestInit) {
  const res = await fetchWithTimeout(`${BASE}${url}`, options)
  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status)
  }
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.click()
  URL.revokeObjectURL(objectUrl)
}
