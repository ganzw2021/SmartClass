/**
 * API 服务层 - 智慧课堂教师端
 * 基于 Axios 封装所有后端接口
 */
import axios from 'axios'
import { ref } from 'vue'

// API 基础配置
// 开发环境：'http://localhost:5000/api'
// 生产/公网：使用相对路径（前端和后端部署在同一域名下）
const API_BASE = '/api'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// 响应状态
export const apiLoading = ref(false)
export const apiError = ref(null)

// 请求拦截器 - 添加 Token
api.interceptors.request.use(config => {
  // 按优先级：admin > student > teacher
  const token = sessionStorage.getItem('tc_admin_token') || sessionStorage.getItem('tc_student_token') || sessionStorage.getItem('tc_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    apiError.value = error.message
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ============ 认证相关 ============

/**
 * 教师登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 */
export async function teacherLogin(username, password) {
  const res = await api.post('/auth/login', { username, password, type: 'teacher' })
  if (res.success && res.data) {
    sessionStorage.setItem('tc_token', res.data.token)
    sessionStorage.setItem('tc_teacher', JSON.stringify(res.data.user))
  }
  return res
}

/**
 * 管理员登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 */
export async function adminLogin(username, password) {
  const res = await api.post('/auth/login', { username, password, type: 'admin' })
  if (res.success && res.data) {
    sessionStorage.setItem('tc_admin_token', res.data.token)
    sessionStorage.setItem('tc_admin_user', JSON.stringify(res.data.user))
  }
  return res
}

/**
 * 学生登录
 * @param {string} username - 学号
 * @param {string} password - 密码
 */
export async function studentLogin(username, password) {
  const res = await api.post('/auth/login', { username, password, type: 'student' })
  if (res.success && res.data) {
    sessionStorage.setItem('tc_student_token', res.data.token)
    sessionStorage.setItem('tc_student_user', JSON.stringify(res.data.user))
  }
  return res
}

/**
 * 获取当前教师信息
 */
export async function getTeacherInfo() {
  return await api.get('/auth/teacher/info')
}

/**
 * 登出
 */
export function teacherLogout() {
  localStorage.removeItem('tc_token')
  localStorage.removeItem('tc_teacher')
}

// ============ 班级管理 ============

/**
 * 获取班级列表
 */
export async function getClasses() {
  return await api.get('/classes')
}

/**
 * 获取所有班级（供课程关联用）
 */
export async function getAllClasses() {
  return await api.get('/classes/all')
}

/**
 * 获取班级学生
 * @param {number} classId - 班级ID
 */
export async function getClassStudents(classId) {
  return await api.get(`/classes/${classId}/students`)
}

/**
 * 创建班级
 * @param {object} data - { name }
 */
export async function createClass(data) {
  return await api.post('/classes', data)
}

/**
 * 更新班级
 * @param {number} classId - 班级ID
 * @param {object} data - { name }
 */
export async function updateClass(classId, data) {
  return await api.put(`/classes/${classId}`, data)
}

/**
 * 删除班级
 * @param {number} classId - 班级ID
 */
export async function deleteClass(classId) {
  return await api.delete(`/classes/${classId}`)
}

/**
 * 添加学生到班级
 * @param {number} classId - 班级ID
 * @param {Array} students - 学生列表 [{name, student_number}]
 */
export async function addStudentsToClass(classId, students) {
  return await api.post(`/admin/classes/${classId}/students`, { students })
}

/**
 * 批量导入学生
 * @param {number} classId - 班级ID
 * @param {string} text - 文本格式学生数据
 */
export async function importStudents(classId, text) {
  const students = text.split('\n')
    .map(line => line.trim())
    .filter(line => line)
    .map(name => ({ name }))
  return await addStudentsToClass(classId, students)
}

/**
 * 删除学生
 * @param {number} classId - 班级ID
 * @param {number} studentId - 学生ID
 */
export async function removeStudent(classId, studentId) {
  return await api.delete(`/classes/${classId}/students/${studentId}`)
}

// ============ 课程管理 ============

/**
 * 获取课程列表
 */
export async function getCourses() {
  return await api.get('/courses')
}

/**
 * 创建课程
 * @param {object} data - { name, term }
 */
export async function createCourse(data) {
  return await api.post('/courses', data)
}

/**
 * 更新课程
 * @param {number} courseId - 课程ID
 * @param {object} data - { name, term }
 */
export async function updateCourse(courseId, data) {
  return await api.put(`/courses/${courseId}`, data)
}

/**
 * 删除课程
 * @param {number} courseId - 课程ID
 */
export async function deleteCourse(courseId) {
  return await api.delete(`/courses/${courseId}`)
}

/**
 * 获取教师关联的课程
 * @param {string} term - 学期筛选（可选）
 */
export async function getTeacherCourses(term = '') {
  const url = term ? `/courses?term=${encodeURIComponent(term)}` : '/courses'
  return await api.get(url)
}

// ============ 考勤签到 ============

/**
 * 开启签到会话
 * POST /attendance/start
 * 返回: { session_key, qr_url }
 */
export async function startAttendance(courseId, classId) {
  return await api.post('/attendance/start', {
    course_id: courseId,
    class_id: classId
  })
}

/**
 * 刷新二维码 URL
 * GET /attendance/qr?course_id=xx&class_id=xx
 * 返回: { qr_url, token }
 */
export async function refreshQRCodeUrl(courseId, classId) {
  return await api.get(`/attendance/qr?course_id=${courseId}&class_id=${classId}`)
}

/**
 * 获取当前会话已签到名单
 * GET /attendance/current_session?course_id=xx&class_id=xx
 * 返回: { session_key, signed_names[] }
 */
export async function getCurrentSession(courseId, classId) {
  return await api.get(`/attendance/current_session?course_id=${courseId}&class_id=${classId}`)
}

/**
 * 重置签到会话
 * POST /attendance/reset
 */
export async function resetAttendance(courseId) {
  return await api.post('/attendance/reset', { course_id: courseId })
}

/**
 * 手动补签
 * POST /attendance/manual
 */
export async function manualSign(courseId, classId, studentName, sessionKey) {
  return await api.post('/attendance/manual', {
    course_id: courseId,
    class_id: classId,
    student_name: studentName,
    session_key: sessionKey
  })
}

/**
 * 获取历史签到记录
 * GET /attendance/list?course_id=xx&class_id=xx
 */
export async function getAttendanceList(courseId, classId) {
  let url = `/attendance/list?course_id=${courseId}`
  if (classId) url += `&class_id=${classId}`
  return await api.get(url)
}

/**
 * 保存考勤报表
 * POST /attendance/save_report
 */
export async function saveAttendanceReport(data) {
  return await api.post('/attendance/save_report', data)
}

// ============ 考勤报表 ============

/**
 * 获取考勤报表列表
 * @param {object} params - { courseId, classId, page, pageSize }
 */
export async function getAttendanceReports(params = {}) {
  const p = new URLSearchParams()
  if (params.courseId) p.append('course_id', params.courseId)
  if (params.classId) p.append('class_id', params.classId)
  if (params.page) p.append('page', params.page)
  if (params.pageSize) p.append('page_size', params.pageSize)
  return await api.get(`/attendance/reports?${p.toString()}`)
}

/**
 * 获取考勤报表详情
 * @param {number} reportId
 */
export async function getAttendanceReportDetail(reportId) {
  return await api.get(`/attendance/report/${reportId}`)
}

/**
 * 删除考勤报表
 * @param {number} reportId
 */
export async function deleteAttendanceReport(reportId) {
  return await api.delete(`/attendance/report/${reportId}`)
}

/**
 * 更新学生考勤状态（迟到/请假/缺勤）
 * @param {number} recordId - 学生考勤记录ID
 * @param {string} status - signed/absent/late/leave
 * @param {string} note - 备注
 */
export async function updateStudentAttendanceStatus(recordId, status, note = '') {
  return await api.put('/attendance/student_status', {
    record_id: recordId,
    status,
    note
  })
}

// ============ 平时分管理 ============

/**
 * 获取平时分
 * @param {number} courseId - 课程ID
 * @param {number} classId - 班级ID
 */
export async function getScores(courseId, classId) {
  return await api.get(`/scores?course_id=${courseId}&class_id=${classId}`)
}

/**
 * 批量保存平时分
 * @param {number} courseId - 课程ID
 * @param {number} classId - 班级ID
 * @param {Array} scores - 分数数组 [{student_id, att_score, interact_score, hw_score}]
 */
export async function saveScores(courseId, classId, scores) {
  return await api.post('/scores/batch', {
    course_id: courseId,
    class_id: classId,
    scores
  })
}

// ============ 管理端 API ============

/** 获取统计数据 */
export async function getAdminStats() {
  return await api.get('/admin/stats')
}

/** 获取看板详细统计数据 */
export async function getAdminDashboard() {
  return await api.get('/admin/dashboard')
}

/** 获取学生活跃统计（近7天） */
export async function getAdminStudentActivity() {
  return await api.get('/admin/student_activity')
}

/** 作业统计（管理端） */
export async function getAdminHomeworkStats(params = {}) {
  return await api.get('/admin/homework_stats', { params })
}

/** 考勤统计（管理端） */
export async function getAdminAttendanceStats(params = {}) {
  return await api.get('/admin/attendance_stats', { params })
}

/** 管理端课程列表（用于筛选器） */
export async function getAdminCourseList() {
  return await api.get('/admin/course_list')
}

/** 课程管理 CRUD */
export async function getAdminCourses() {
  return await api.get('/admin/courses')
}
export async function createAdminCourse(data) {
  return await api.post('/admin/courses', data)
}
export async function updateAdminCourse(id, data) {
  return await api.put(`/admin/courses/${id}`, data)
}
export async function deleteAdminCourse(id) {
  return await api.delete(`/admin/courses/${id}`)
}
export async function batchCreateCourses(data) {
  return await api.post('/admin/courses/batch', data)
}

/** 管理端班级列表（用于筛选器） */
export async function getAdminClassList() {
  return await api.get('/admin/class_list')
}

/** 教师管理 */
export async function getAdminTeachers() {
  return await api.get('/admin/teachers')
}
export async function createAdminTeacher(data) {
  return await api.post('/admin/teachers', data)
}
export async function updateAdminTeacher(id, data) {
  return await api.put(`/admin/teachers/${id}`, data)
}
export async function deleteAdminTeacher(id) {
  return await api.delete(`/admin/teachers/${id}`)
}
export async function resetAdminTeacherToken(id) {
  return await api.post(`/admin/teachers/${id}/reset_token`)
}
export async function resetAdminTeacherPassword(id, newPassword) {
  return await api.post(`/admin/teachers/${id}/reset_password`, { new_password: newPassword })
}

/** 班级管理 */
export async function getAdminClasses() {
  return await api.get('/admin/classes')
}
export async function createAdminClass(data) {
  return await api.post('/admin/classes', data)
}
export async function updateAdminClass(id, data) {
  return await api.put(`/admin/classes/${id}`, data)
}
export async function deleteAdminClass(id) {
  return await api.delete(`/admin/classes/${id}`)
}
export async function getAdminClassStudents(classId) {
  return await api.get(`/admin/classes/${classId}/students`)
}
export async function addAdminClassStudent(classId, data) {
  return await api.post(`/admin/classes/${classId}/students`, data)
}
export async function deleteAdminStudent(id) {
  return await api.delete(`/admin/students/${id}`)
}
export async function createAdminStudentAccounts(classId, defaultPassword) {
  return await api.post('/admin/students/create_accounts', { class_id: classId, default_password: defaultPassword || '123456' })
}
export async function resetAdminStudentPassword(accountId, newPassword) {
  return await api.post('/admin/students/reset_password', { account_id: accountId, new_password: newPassword || '123456' })
}

/**
 * 批量清除学生账号数据（账号变为未开通状态，学生端数据全部清除）
 * @param {Array} studentIds - 学生ID数组
 */
export async function clearAdminStudentAccounts(studentIds) {
  return await api.post('/admin/students/clear_accounts', { student_ids: studentIds })
}

/** 课程管理 */

/**
 * 更新单个学生分数
 * @param {number} studentId - 学生ID
 * @param {number} courseId - 课程ID
 * @param {object} data - { att_score, interact_score, hw_score }
 */
export async function updateStudentScore(studentId, courseId, data) {
  return await api.put(`/scores/${studentId}`, { course_id: courseId, ...data })
}

// ============ 作业管理 ============

/**
 * 获取作业列表
 * @param {object} params - 筛选参数 { courseId, classId }
 */
export async function getHomeworkList({ courseId, classId } = {}) {
  let url = '/homework'
  const params = []
  if (courseId) params.push(`course_id=${courseId}`)
  if (classId) params.push(`class_id=${classId}`)
  if (params.length > 0) url += '?' + params.join('&')
  return await api.get(url)
}

/**
 * 获取作业详情
 * @param {number} homeworkId - 作业ID
 */
export async function getHomeworkDetail(homeworkId) {
  return await api.get(`/homework/${homeworkId}`)
}

/**
 * 创建作业
 * @param {FormData} formData - 作业数据
 */
export async function createHomework(formData) {
  return await api.post('/homework', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 更新作业
 * @param {number} homeworkId - 作业ID
 * @param {FormData} formData - 作业数据
 */
export async function updateHomework(homeworkId, formData) {
  return await api.put(`/homework/${homeworkId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 删除作业
 * @param {number} homeworkId - 作业ID
 */
export async function deleteHomework(homeworkId) {
  return await api.delete(`/homework/${homeworkId}`)
}

/**
 * 获取作业提交列表
 * @param {number} homeworkId - 作业ID
 */
export async function getHomeworkSubmissions(homeworkId) {
  return await api.get(`/homework/${homeworkId}/submissions`)
}

/**
 * 评分作业
 * @param {number} homeworkId - 作业ID
 * @param {number} studentId - 学生ID
 * @param {object} data - { score, feedback }
 */
export async function gradeHomework(homeworkId, studentId, data) {
  return await api.post(`/homework/${homeworkId}/grade`, {
    student_id: studentId,
    score: data.score,
    feedback: data.feedback
  })
}

/**
 * 上传评分脚本
 * @param {number} homeworkId - 作业ID
 * @param {FormData} formData - 包含 script 文件和 enable_auto, regrade_all 选项
 */
export async function uploadGradingScript(homeworkId, formData) {
  return await api.post(`/homework/${homeworkId}/grading_script`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取评分脚本信息
 * @param {number} homeworkId - 作业ID
 */
export async function getGradingScript(homeworkId) {
  return await api.get(`/homework/${homeworkId}/grading_script`)
}

/**
 * 获取评分脚本内容
 * @param {number} homeworkId - 作业ID
 */
export async function getGradingScriptContent(homeworkId) {
  return await api.get(`/homework/${homeworkId}/grading_script/content`)
}

/**
 * 切换自动评分开关
 * @param {number} homeworkId - 作业ID
 * @param {boolean} enable - 是否启用
 */
export async function toggleGradingAuto(homeworkId, enable) {
  return await api.post(`/homework/${homeworkId}/grading_script/toggle_auto`, { enable })
}

/**
 * 下载评分脚本（触发浏览器下载）
 * @param {number} homeworkId - 作业ID
 */
export function downloadGradingScript(homeworkId) {
  const token = sessionStorage.getItem('tc_token')
  const url = `${api.defaults.baseURL}/homework/${homeworkId}/grading_script/download?token=${token}`
  const a = document.createElement('a')
  a.href = url
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

/**
 * 删除评分脚本
 * @param {number} homeworkId - 作业ID
 */
export async function deleteGradingScript(homeworkId) {
  return await api.delete(`/homework/${homeworkId}/grading_script`)
}

// ============ 课程资源 ============

/**
 * 获取课程资源列表
 * @param {object} params - { courseId, term }
 */
export async function getCourseResources(params = {}) {
  const p = new URLSearchParams()
  if (params.courseId) p.append('course_id', params.courseId)
  if (params.term) p.append('term', params.term)
  return await api.get(`/resources?${p.toString()}`)
}

/**
 * 上传课程资源
 * @param {FormData} formData - 包含 course_id, course_name, term, title, description, file
 */
export async function uploadCourseResource(formData) {
  return await api.post('/resources/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 删除课程资源
 * @param {number} resourceId
 */
export async function deleteCourseResource(resourceId) {
  return await api.delete(`/resources/${resourceId}`)
}

/**
 * 下载课程资源
 * @param {number} resourceId
 */
export function downloadCourseResource(resourceId) {
  const studentToken = sessionStorage.getItem('tc_student_token')
  const teacherToken = sessionStorage.getItem('tc_token')
  // 根据是否有学生token判断是学生端还是教师端
  const token = studentToken || teacherToken
  const isStudent = !!studentToken
  const path = isStudent ? '/student/resources/download' : '/resources/download'
  const url = `${api.defaults.baseURL}${path}/${resourceId}?token=${token}`
  window.open(url, '_blank')
}

// ============ 学生端 API ============

/** 获取学生个人信息 */
export async function getStudentProfile() {
  return await api.get('/student/profile')
}

/** 更新学生信息 */
export async function updateStudentProfile(data) {
  return await api.post('/student/profile', data)
}

/** 修改密码 */
export async function changeStudentPassword(oldPassword, newPassword) {
  return await api.post('/student/change_password', { old_password: oldPassword, new_password: newPassword })
}

/** 获取学生的课程列表
 * @param {string} term - 学期筛选（可选）
 */
export async function getStudentCourses(term = '') {
  const url = term ? `/student/courses?term=${encodeURIComponent(term)}` : '/student/courses'
  return await api.get(url)
}

/** 获取学生的作业列表 */
export async function getStudentHomework(courseId) {
  const url = courseId ? `/student/homework?course_id=${courseId}` : '/student/homework'
  return await api.get(url)
}

/** 提交作业 */
export async function submitHomework(homeworkId, formData) {
  return await api.post(`/student/homework/${homeworkId}/submit`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取学生端天梯榜
 * @param {string} courseId - 课程ID
 * @param {string} term - 学期（可选）
 */
export async function getStudentRanking(courseId, term = '') {
  const params = { course_id: courseId }
  if (term) params.term = term
  return await api.get('/student/homework/ranking', { params })
}

/**
 * 获取教师端班级天梯榜
 * @param {string} courseId - 课程ID
 * @param {string} classId - 班级ID
 */
export async function getClassRanking(courseId, classId) {
  return await api.get('/homework/ranking', {
    params: { course_id: courseId, class_id: classId }
  })
}

/**
 * 获取学生端课程资源
 * @param {object} params - { courseId, term }
 */
export async function getStudentCourseResources(params = {}) {
  const p = new URLSearchParams()
  if (params.courseId) p.append('course_id', params.courseId)
  if (params.term) p.append('term', params.term)
  return await api.get(`/student/resources?${p.toString()}`)
}

// ============ 学生通知 API ============

/** 获取学生通知列表 */
export async function getStudentNotifications() {
  return await api.get('/student/notifications')
}

/** 删除单条通知 */
export async function deleteNotification(id) {
  return await api.delete(`/student/notifications/${id}`)
}

/** 清空所有已读通知 */
export async function clearReadNotifications() {
  return await api.delete('/student/notifications')
}

/** 标记通知为已读 */
export async function markNotificationsRead(id = null) {
  return await api.put('/student/notifications/read', { id })
}

// ============ 工具函数 ============

/**
 * 下载文件
 * @param {string} path - 文件路径
 * @param {string} filename - 下载文件名
 */
export function downloadFile(path, filename) {
  const token = localStorage.getItem('tc_token')
  const url = `${API_BASE}/download?path=${encodeURIComponent(path)}&token=${token}`
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}

export default api
