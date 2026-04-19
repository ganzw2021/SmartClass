# SmartClass 蓝绿部署说明
# SmartClass Blue-Green Deployment Guide

========================================
  SmartClass 蓝绿部署指南
========================================

📁 目录结构
----------------------------------------
C:\smartclass\
├── backend\           # 原后端目录（保留备份）
├── backend_blue\      # 蓝环境后端 (port 5000)
├── backend_green\      # 绿环境后端 (port 5001)
└── scripts\           # 部署脚本
    ├── start_blue.ps1     # 启动蓝环境
    ├── start_green.ps1    # 启动绿环境
    ├── switch_blue.ps1    # 切换到蓝环境（回滚）
    ├── switch_green.ps1   # 切换到绿环境
    └── stop_all.ps1       # 停止所有后端

🚀 使用流程
----------------------------------------
1. 开发/修改代码在 backend 目录
2. 测试时用绿环境 (port 5001)
3. 确认无误后运行 switch_to_green.ps1 切换到绿环境
4. 发现问题？运行 switch_to_blue.ps1 回滚

⚠️ 注意事项
----------------------------------------
- 两个环境共用同一个数据库
- 切换时约 3-5 秒服务中断
- 上传文件目录共用 C:\smartclass\backend\uploads\
- 建议修改前先备份当前 backend 目录

🔧 常用命令
----------------------------------------
# 启动蓝环境
.\start_blue.ps1

# 启动绿环境（测试用）
.\start_green.ps1

# 切换到绿环境（发布）
.\switch_to_green.ps1

# 切换回蓝环境（回滚）
.\switch_to_blue.ps1

# 停止所有后端
.\stop_all.ps1

========================================
