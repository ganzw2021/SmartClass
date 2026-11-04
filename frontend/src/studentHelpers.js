export function courseOptions(data) {
  const rows = Array.isArray(data) ? data : data?.courses || []
  return [...new Map(rows.map(course => [String(course.id), { ...course, id: String(course.id) }])).values()]
}

export function formatScore(value) {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value))
    ? Number(value).toFixed(1) : '—'
}

export function studentError(error, fallback = '加载失败，请稍后重试') {
  if (error?.response?.status === 401) return '登录已过期，请退出后重新登录'
  return error?.response?.data?.message || fallback
}
