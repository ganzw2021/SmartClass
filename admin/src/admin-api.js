/**
 * API 服务层 - 智慧课堂管理端
 * 基于 Axios 封装所有后端接口
 */
import axios from 'axios'
import { ref } from 'vue'

// API 基础配置
const API_BASE = 'http://localhost:5000/api'

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
  const token = sessionStorage.getItem('tc_admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('tc_admin_token')
      sessionStorage.removeItem('tc_admin_user')
      window.location.href = '/admin.html'
    }
    return Promise.reject(error)
  }
)

// ===== 认证 =====
export function adminLogin(username, password) {
  return api.post('/auth/login', { type: 'admin', username, password })
}

export function getAdminProfile() {
  return api.get('/admin/profile')
}

// ===== 统计数据 =====
export function getStats() {
  return api.get('/admin/stats')
}

// ===== 教师管理 =====
export function getTeachers() {
  return api.get('/admin/teachers')
}

export function createTeacher(data) {
  return api.post('/admin/teachers', data)
}

export function updateTeacher(id, data) {
  return api.put(`/admin/teachers/${id}`, data)
}

export function deleteTeacher(id) {
  return api.delete(`/admin/teachers/${id}`)
}

export function resetTeacherToken(id) {
  return api.post(`/admin/teachers/${id}/reset_token`)
}

export function resetTeacherPassword(id, newPassword) {
  return api.post(`/admin/teachers/${id}/reset_password`, { new_password: newPassword })
}

// ===== 班级管理 =====
export function getAdminClasses() {
  return api.get('/admin/classes')
}

export function createClass(data) {
  return api.post('/admin/classes', data)
}

export function updateClass(id, data) {
  return api.put(`/admin/classes/${id}`, data)
}

export function deleteClass(id) {
  return api.delete(`/admin/classes/${id}`)
}

// ===== 学生管理 =====
export function getClassStudents(classId) {
  return api.get(`/admin/classes/${classId}/students`)
}

export function addStudent(classId, data) {
  return api.post(`/admin/classes/${classId}/students`, data)
}

export function deleteStudent(id) {
  return api.delete(`/admin/students/${id}`)
}

export function createStudentAccounts(studentIds) {
  return api.post('/admin/students/create_accounts', { student_ids: studentIds })
}

export function resetStudentPassword(id, newPassword) {
  return api.post('/admin/students/reset_password', { student_id: id, new_password: newPassword })
}

// ===== 课程管理 =====
export function getAdminCourses() {
  return api.get('/admin/courses')
}

// ===== 考勤记录 =====
export function getAttendanceLogs(params) {
  return api.get('/admin/attendance_logs', { params })
}

export function getAttendanceReports(params) {
  return api.get('/admin/attendance_reports', { params })
}

// 获取下载URL（带token）
export function getDownloadUrl(path) {
  const token = sessionStorage.getItem('tc_admin_token') || ''
  return `${API_BASE}${path}?token=${token}`
}
