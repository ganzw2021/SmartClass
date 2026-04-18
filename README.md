# SmartClass 智慧课堂系统

> 江西樟树中医药职业学院 - 智慧课堂教学管理系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-green.svg)](https://vuejs.org/)

---

## 📖 项目简介

SmartClass 智慧课堂系统是一套面向职业院校的在线教学管理平台，支持作业管理、扫码签到、考勤报表、天梯榜排名等功能。系统分为三个独立端：教师端、管理端和学生端。

### 核心特性

- **作业管理**：教师创建作业、设置截止时间、上传附件；学生在线提交、支持历史版本回退
- **二维码签到**：动态二维码防作弊、实时同步签到状态、手动补签功能
- **考勤报表**：完整考勤记录、多种状态标记（已签到/迟到/请假/缺勤）
- **天梯榜**：基于作业得分的14级颜色段位排行，激发学习动力
- **自动批改**：支持Python评分脚本自动评分
- **微信小程序**：学生端移动版，支持微信聊天文件直接提交作业

---

## 🏗 技术架构

### 前端

| 技术栈 | 版本 | 说明 |
|--------|------|------|
| Vue.js | 3.4+ | 渐进式JavaScript框架 |
| Vite | 6.0+ | 下一代前端构建工具 |
| TailwindCSS | 3.4+ | 原子化CSS框架 |
| Axios | 1.6+ | HTTP请求库 |

### 后端

| 技术栈 | 版本 | 说明 |
|--------|------|------|
| Python | 3.8+ | 服务器端语言 |
| Flask | 3.0+ | 轻量级Web框架 |
| MySQL | 8.0+ | 关系型数据库 |
| JWT | - | 身份认证 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   教师端         │   管理端         │   学生端                     │
│  (teacher.html)  │  (admin.html)   │  (student.html)              │
│   端口: 5174     │   端口: 5173     │   端口: 5175                  │
└────────┬────────┴────────┬────────┴────────┬─────────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │ HTTP REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 服务层                                │
│                    Flask (端口: 5000)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  认证    │ │  作业    │ │  考勤    │ │  班级    │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                    │
│                    MySQL (smartclass)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
smartclass/
├── backend/                    # 后端服务
│   ├── app.py                  # Flask 主应用
│   ├── uploads/                # 文件上传目录
│   │   ├── homework/           # 作业附件
│   │   ├── submissions/        # 提交文件
│   │   ├── grades/             # 评分附件
│   │   └── forum/              # 论坛附件
│   ├── init_db.sql            # 数据库初始化脚本
│   └── requirements.txt        # Python 依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api.js              # API 请求封装
│   │   ├── App.vue             # 根组件
│   │   ├── teacher-main.js     # 教师端入口
│   │   ├── admin-main.js       # 管理端入口
│   │   ├── student-main.js     # 学生端入口
│   │   └── components/         # Vue 组件
│   │       ├── TeacherLogin.vue
│   │       ├── AdminLogin.vue
│   │       ├── StudentLogin.vue
│   │       ├── CoursesModule.vue
│   │       ├── AttendanceModule.vue
│   │       ├── AttendanceReportModule.vue
│   │       ├── TeacherHomeworkModule.vue
│   │       ├── TeacherRankingModule.vue
│   │       ├── AdminDashboardModule.vue
│   │       ├── AdminClassesModule.vue
│   │       ├── AdminTeachersModule.vue
│   │       ├── AdminStudentsModule.vue
│   │       ├── StudentHomeworkModule.vue
│   │       └── StudentRankingModule.vue
│   ├── teacher.html            # 教师端入口页面
│   ├── admin.html              # 管理端入口页面
│   ├── student.html            # 学生端入口页面
│   └── package.json
│
├── wx-student/                 # 微信小程序（学生端）
└── README.md                   # 项目说明文档
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Node.js**: 16+
- **MySQL**: 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/ganzw2021/SmartClass.git
cd SmartClass
```

### 2. 配置数据库

```bash
# 登录 MySQL
mysql -uroot -p

# 执行初始化脚本
source backend/init_db.sql
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 配置后端

编辑 `backend/app.py` 中的数据库配置：

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '你的数据库密码',
    'database': 'smartclass',
    'charset': 'utf8mb4'
}
```

### 5. 启动后端服务

```bash
cd backend
python app.py
```

后端服务运行在 `http://localhost:5000`

### 6. 安装前端依赖

```bash
cd frontend
npm install
```

### 7. 启动前端服务

```bash
# 同时启动三个端口
npm run dev:all

# 或单独启动
npm run dev:teacher   # 教师端: http://localhost:5174
npm run dev:admin      # 管理端: http://localhost:5173
npm run dev:student    # 学生端: http://localhost:5175
```

---

## 👤 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | Admin@123456 | 系统管理员 |
| 教师 | teacher1 | 123456 | 张老师（id=6）|
| 教师 | 18979576263 | 123456 | 甘祖文老师 |
| 教师 | 17262116237 | 123456 | 邹燕琴老师 |

---

## 📱 功能模块

### 教师端

| 模块 | 功能描述 |
|------|----------|
| 课程管理 | 创建课程、关联班级、管理授课内容 |
| 二维码签到 | 生成动态二维码、学生扫码签到、实时统计 |
| 考勤报表 | 查看历史考勤记录、修改考勤状态 |
| 作业管理 | 创建/编辑/删除作业、查看提交、在线评分 |
| 天梯榜 | 查看班级作业排名、14级颜色段位系统 |
| 随机点名 | 随机抽取学生回答问题 |

### 管理端

| 模块 | 功能描述 |
|------|----------|
| 班级管理 | 添加/编辑/删除班级、搜索班级 |
| 学生管理 | 批量导入学生、创建账号、批量清除账号数据 |
| 教师管理 | 添加/编辑/删除教师账号 |
| 仪表盘 | 系统数据概览 |

### 学生端

| 模块 | 功能描述 |
|------|----------|
| 作业列表 | 查看作业、提交作业、上传附件 |
| 我的提交 | 查看提交历史、历史版本回退 |
| 扫码签到 | 扫描教师二维码完成签到 |
| 天梯榜 | 查看个人课程排名 |

---

## 🔧 API 接口

### 认证接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/auth/change_password` | POST | 修改密码 |

### 作业接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/homework` | GET | 获取作业列表 |
| `/api/homework` | POST | 创建作业 |
| `/api/homework/<id>` | PUT | 更新作业 |
| `/api/homework/<id>` | DELETE | 删除作业 |
| `/api/homework/<id>/submissions` | GET | 获取提交列表 |
| `/api/homework/<id>/grade` | POST | 评分 |

### 考勤接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/attendance/start` | POST | 开始签到 |
| `/api/attendance/stop` | POST | 结束签到 |
| `/api/attendance/reports` | GET | 获取考勤报表 |
| `/api/attendance/student_status` | PUT | 更新学生考勤状态 |

---

## 🎮 天梯榜规则

系统采用14级颜色段位排行机制：

| 段位 | 颜色 | 排名范围 |
|------|------|----------|
| 青铜 | 🟤 棕色 | 第13-14名 |
| 白银 | ⬜ 银色 | 第11-12名 |
| 黄金 | 🟡 金色 | 第9-10名 |
| 铂金 | 🔘 灰色 | 第7-8名 |
| 钻石 | 🔵 蓝色 | 第5-6名 |
| 星耀 | 🟣 紫色 | 第3-4名 |
| 王者 | 🟠 橙色 | 第1-2名 |

排名规则：按单次作业最高分计算，非累计分数。

---

## 📦 部署说明

### 生产环境部署

#### 1. 后端部署

```bash
# 使用 Gunicorn
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. 前端构建

```bash
cd frontend
npm run build
```

#### 3. Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/smartclass/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 安全说明

1. **密码存储**：使用 bcrypt 进行密码哈希加密
2. **身份认证**：JWT Token 认证，默认30天有效期
3. **文件上传**：限制上传大小（100MB），存储路径与代码分离
4. **跨域访问**：CORS 配置允许跨域访问

---

## 🛠 维护指南

### 数据库备份

```bash
mysqldump -uroot -p smartclass > backup_$(date +%Y%m%d).sql
```

### 查看日志

```bash
# Linux/Mac
tail -f backend/app.log

# Windows PowerShell
Get-Content backend/app.log -Wait
```

### 重启服务

```powershell
# Windows
.\restart-all.ps1
```

---

## 📄 许可证

本项目基于 [MIT 许可证](https://opensource.org/licenses/MIT) 开源。

---

## 👥 开发团队

- **开发单位**：江西樟树中医药职业学院
- **技术栈**：Vue.js + Flask + MySQL

---

## 📝 更新日志

### v8.5 (2026-04-18)

- 新增学生端作业历史版本回退功能
- 新增考勤报表模块（AttendanceReportModule）
- 优化二维码签到机制（10秒有效期、3秒刷新）
- 新增14级颜色天梯榜排行系统
- 支持Python评分脚本自动批改作业
- 微信小程序学生端发布
- 管理端新增批量清除学生账号功能
- 教师端考勤模块优化（点击开始签到后显示名单）
