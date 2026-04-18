<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-slate-800">作业管理</h2>
      <button @click="showCreateModal = true" class="bg-[#2d6a4f] hover:bg-[#245a42] text-white px-5 py-2.5 rounded-xl font-medium flex items-center gap-2 transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        发布作业
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
      <div class="flex flex-wrap gap-4">
        <select v-model="filterCourseId" @change="onFilterCourseChange" class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-[#2d6a4f] focus:ring-2 focus:ring-[#2d6a4f]/20 outline-none min-w-[200px]">
          <option value="">全部课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.name }}</option>
        </select>
        <select v-model="filterClassId" @change="loadHomework" class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-[#2d6a4f] focus:ring-2 focus:ring-[#2d6a4f]/20 outline-none min-w-[200px]">
          <option value="">全部班级</option>
          <option v-for="cls in filteredFilterClasses" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
        </select>
      </div>
    </div>

    <!-- 作业列表 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-[#2d6a4f] border-t-transparent rounded-full"></div>
    </div>
    
    <div v-else-if="homeworkList.length === 0" class="bg-white rounded-2xl p-12 shadow-sm border border-slate-100 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-slate-500">暂无作业，点击上方按钮发布第一份作业</p>
    </div>

    <div v-else class="grid gap-4">
      <div 
        v-for="hw in filteredHomeworkList" 
        :key="hw.id"
        class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-md transition-all cursor-pointer"
        @click="viewHomework(hw)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-bold text-slate-800">{{ hw.title }}</h3>
              <span class="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                {{ hw.course_name }}
              </span>
            </div>
            <p class="text-slate-500 text-sm mb-3 line-clamp-2">{{ hw.content || '无描述' }}</p>
            <div class="flex items-center gap-4 text-xs text-slate-400">
              <span>截止：{{ formatDate(hw.deadline) }}</span>
              <span>总分：{{ hw.total_score }}分</span>
              <span>提交：{{ hw.total_submissions || 0 }}人</span>
              <span v-if="hw.total_submissions > 0" class="text-[#2d6a4f] font-medium">
                已评分：{{ hw.graded_count || 0 }}人
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click.stop="editHomework(hw)" class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click.stop="confirmDelete(hw)" class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑作业弹窗 -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="closeCreateModal">
        <div class="bg-white rounded-[24px] w-full max-w-lg p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-slate-800">{{ editingHomework ? '编辑作业' : '发布作业' }}</h3>
            <button @click="closeCreateModal" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="submitHomework" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">作业标题 *</label>
              <input v-model="formData.title" type="text" required placeholder="请输入作业标题" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">关联课程 *</label>
              <select v-model="formData.course_id" required class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
                <option value="">请选择课程</option>
                <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">班级</label>
              <select v-model="formData.class_id" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
                <option value="">全部班级</option>
                <option v-for="cls in selectedCourseClasses" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">作业描述</label>
              <textarea v-model="formData.content" rows="4" placeholder="请输入作业描述内容" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors resize-none"></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">截止时间</label>
                <input v-model="formData.deadline" type="datetime-local" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">总分</label>
                <input v-model.number="formData.total_score" type="number" min="1" max="1000" value="100" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
              </div>
            </div>

            <!-- 附件上传 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">附件（作业材料）</label>
              <div class="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:border-[#2d6a4f] transition-colors">
                <input type="file" id="hw-files" multiple @change="handleFileSelect" class="hidden" accept="*/*">
                <label for="hw-files" class="cursor-pointer">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto text-slate-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span class="text-sm text-slate-500">点击选择文件或拖拽文件到此处</span>
                </label>
                <div v-if="selectedFiles.length > 0" class="mt-3 space-y-2">
                  <div v-for="(file, idx) in selectedFiles" :key="idx" class="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2">
                    <span class="text-sm text-slate-600 truncate max-w-[200px]">{{ file.name }}</span>
                    <button @click="removeFile(idx)" class="text-red-500 hover:text-red-600 ml-2">✕</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 评分脚本上传（仅创建时可用，编辑时在详情页操作） -->
            <div v-if="!editingHomework">
              <label class="block text-sm font-medium text-slate-700 mb-1.5">自动评分脚本（可选）</label>
              <div class="border-2 border-dashed border-orange-200 bg-orange-50/50 rounded-xl p-4 text-center hover:border-orange-400 transition-colors">
                <input type="file" id="create-script" @change="handleCreateScriptUpload" accept=".py" class="hidden">
                <label for="create-script" class="cursor-pointer">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto text-orange-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <span class="text-sm text-orange-600">点击上传 Python 评分脚本</span>
                  <p class="text-xs text-orange-400 mt-1">用于自动批改学生提交的Python文件作业</p>
                </label>
                <div v-if="createScriptFile" class="mt-3 flex items-center justify-between bg-white rounded-lg px-3 py-2">
                  <div class="flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                    <span class="text-sm text-slate-600">{{ createScriptFile.name }}</span>
                  </div>
                  <button @click="createScriptFile = null" class="text-red-500 hover:text-red-600">✕</button>
                </div>
                <div v-if="createScriptFile" class="mt-2">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="createEnableAutoGrade" class="w-4 h-4 rounded accent-orange-500">
                    <span class="text-sm text-orange-600">同时启用自动评分</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="flex gap-3 pt-4">
              <button type="button" @click="closeCreateModal" class="flex-1 border-2 border-slate-200 text-slate-600 py-3 rounded-xl font-medium hover:bg-slate-50 transition-colors">
                取消
              </button>
              <button type="submit" :disabled="submitting" class="flex-1 bg-[#2d6a4f] hover:bg-[#245a42] disabled:bg-slate-300 text-white py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
                <span v-if="submitting" class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
                {{ editingHomework ? '保存修改' : '发布作业' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 作业详情/提交列表弹窗 -->
    <Teleport to="body">
      <div v-if="showDetailModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showDetailModal = false">
        <div class="bg-white rounded-[24px] w-full max-w-3xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-slate-800">{{ currentHomework?.title }}</h3>
            <button @click="showDetailModal = false" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 作业信息 -->
          <div class="bg-slate-50 rounded-xl p-4 mb-6">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div><span class="text-slate-500">课程：</span><span class="font-medium">{{ currentHomework?.course_name }}</span></div>
              <div><span class="text-slate-500">班级：</span><span class="font-medium">{{ currentHomework?.class_name || '全部' }}</span></div>
              <div><span class="text-slate-500">截止时间：</span><span class="font-medium">{{ formatDate(currentHomework?.deadline) }}</span></div>
              <div><span class="text-slate-500">总分：</span><span class="font-medium">{{ currentHomework?.total_score }}分</span></div>
            </div>
            <p v-if="currentHomework?.content" class="mt-3 text-sm text-slate-600">{{ currentHomework.content }}</p>
          </div>

          <!-- 作业附件 -->
          <div v-if="currentHomework?.attachments?.length > 0" class="mb-6">
            <h4 class="font-bold text-slate-800 mb-3">作业附件</h4>
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="att in currentHomework.attachments" 
                :key="att.id"
                @click="downloadHwAttachment(att)"
                class="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg text-sm flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
                {{ att.file_name }}
              </button>
            </div>
          </div>

          <!-- 评分脚本管理 -->
          <div class="mb-6 border-t border-slate-200 pt-5">
            <div class="flex items-center justify-between mb-3">
              <h4 class="font-bold text-slate-800">自动评分脚本</h4>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="gradingAutoEnabled" @change="toggleAutoGrade" :disabled="!gradingScript || scriptUploading" class="w-4 h-4 rounded accent-[#2d6a4f]">
                <span class="text-sm" :class="gradingAutoEnabled ? 'text-[#2d6a4f] font-medium' : 'text-slate-500'">启用自动评分</span>
              </label>
            </div>
            
            <div v-if="gradingScript" class="bg-slate-50 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-slate-800">{{ gradingScript.script_name || '评分脚本' }}</p>
                    <p class="text-xs text-slate-400">已上传 · {{ gradingAutoEnabled ? '已启用' : '未启用' }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button @click="viewScriptContent" class="px-3 py-1.5 text-slate-600 hover:bg-slate-200 rounded-lg text-sm transition-colors">查看</button>
                  <button @click="handleDownloadScript" class="px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg text-sm transition-colors flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    下载
                  </button>
                  <button @click="regradeAll" :disabled="scriptUploading" class="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm transition-colors disabled:opacity-50">重新评分</button>
                  <button @click="confirmDeleteScript" class="px-3 py-1.5 text-red-500 hover:bg-red-50 rounded-lg text-sm transition-colors">删除</button>
                </div>
              </div>
            </div>
            
            <div v-else class="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center">
              <input type="file" id="grading-script" @change="handleScriptUpload" accept=".py" class="hidden">
              <label for="grading-script" class="cursor-pointer block">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto text-slate-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span class="text-sm text-slate-500">点击上传 Python 评分脚本</span>
                <p class="text-xs text-slate-400 mt-1">支持 .py 文件，用于自动评分</p>
              </label>
            </div>
          </div>

          <!-- 提交统计 -->

          <!-- 提交统计 -->
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-bold text-slate-800">学生提交情况</h4>
            <span class="text-sm text-slate-500">已提交 {{ submissions?.length || 0 }} / {{ totalStudents }} 人</span>
          </div>

          <!-- 提交列表 -->
          <div v-if="loadingSubmissions" class="flex justify-center py-8">
            <div class="animate-spin w-8 h-8 border-4 border-[#2d6a4f] border-t-transparent rounded-full"></div>
          </div>
          
          <div v-else-if="submissions?.length === 0" class="text-center py-8 text-slate-400">
            暂无学生提交
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="sub in submissions" 
              :key="sub.id"
              class="border border-slate-200 rounded-xl p-4 hover:bg-slate-50 transition-colors"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-[#2d6a4f] text-white rounded-full flex items-center justify-center font-bold">
                    {{ sub.student_name?.charAt(0) || '?' }}
                  </div>
                  <div>
                    <p class="font-medium text-slate-800">{{ sub.student_name }}</p>
                    <p class="text-xs text-slate-400">提交时间：{{ formatDate(sub.submitted_at) }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span v-if="sub.score !== null" class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-bold">
                    {{ sub.score }}分
                  </span>
                  <span v-else-if="sub.auto_score !== null" class="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-bold">
                    {{ sub.auto_score }}分 <span class="text-xs">自动</span>
                  </span>
                  <span v-else class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-sm">
                    未评分
                  </span>
                  <button @click="openGradeModal(sub)" class="text-[#2d6a4f] hover:text-[#245a42] font-medium text-sm">
                    {{ (sub.score !== null || sub.auto_score !== null) ? '修改评分' : '评分' }}
                  </button>
                </div>
              </div>
              
              <!-- 附件 -->
              <div v-if="sub.attachments?.length > 0" class="flex flex-wrap gap-2">
                <button 
                  v-for="att in sub.attachments" 
                  :key="att.id"
                  @click="downloadSubmissionAttachment(att)"
                  class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  {{ att.file_name }}
                </button>
              </div>
              
              <!-- 评语 -->
              <div v-if="sub.feedback" class="mt-3 text-sm text-slate-600 bg-yellow-50 rounded-lg p-3">
                <span class="font-medium text-yellow-700">评语：</span>{{ sub.feedback }}
              </div>
              
              <!-- 自动评分细节 -->
              <div v-if="sub.auto_grade_details && Object.keys(sub.auto_grade_details).length > 0" class="mt-3">
                <button 
                  @click="toggleSubDetails(sub.id)"
                  class="flex items-center gap-2 text-sm text-orange-600 hover:text-orange-700 font-medium"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 transition-transform" :class="{'rotate-90': expandedSubDetails[sub.id]}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  评分详情
                </button>
                <div v-if="expandedSubDetails[sub.id]" class="mt-2 bg-slate-800 text-slate-100 rounded-xl p-4 text-xs font-mono overflow-x-auto">
                  <div class="space-y-1.5">
                    <div v-for="(value, key) in sub.auto_grade_details" :key="key" class="whitespace-pre-wrap break-words leading-relaxed">
                      <span class="text-orange-400">{{ key }}：</span>
                      <span :class="value.includes('✅') ? 'text-green-400' : value.includes('❌') ? 'text-red-400' : 'text-slate-300'">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="sub.auto_grade_message && !sub.auto_grade_details" class="mt-3">
                <button 
                  @click="toggleSubDetails(sub.id)"
                  class="flex items-center gap-2 text-sm text-orange-600 hover:text-orange-700 font-medium"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 transition-transform" :class="{'rotate-90': expandedSubDetails[sub.id]}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  评分详情
                </button>
                <div v-if="expandedSubDetails[sub.id]" class="mt-2 bg-slate-800 text-slate-100 rounded-xl p-4 text-sm">
                  {{ sub.auto_grade_message }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 评分弹窗 -->
    <Teleport to="body">
      <div v-if="showGradeModal" class="fixed inset-0 bg-black/40 z-[110] flex items-center justify-center p-6" @click.self="showGradeModal = false">
        <div class="bg-white rounded-[24px] w-full max-w-md p-6 shadow-2xl">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-slate-800">评分 - {{ gradingSubmission?.student_name }}</h3>
            <button @click="showGradeModal = false" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="submitGrade" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">得分（满分{{ currentHomework?.total_score }}分）</label>
              <input v-model.number="gradeData.score" type="number" min="0" :max="currentHomework?.total_score" required class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors">
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">评语</label>
              <textarea v-model="gradeData.feedback" rows="3" placeholder="请输入评语（可选）" class="w-full border-2 border-slate-100 rounded-xl px-4 py-2.5 outline-none focus:border-[#2d6a4f] transition-colors resize-none"></textarea>
            </div>

            <div class="flex gap-3 pt-4">
              <button type="button" @click="showGradeModal = false" class="flex-1 border-2 border-slate-200 text-slate-600 py-3 rounded-xl font-medium hover:bg-slate-50 transition-colors">
                取消
              </button>
              <button type="submit" :disabled="gradingSubmitting" class="flex-1 bg-[#2d6a4f] hover:bg-[#245a42] disabled:bg-slate-300 text-white py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2">
                <span v-if="gradingSubmitting" class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
                提交评分
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showDeleteModal = false">
        <div class="bg-white rounded-[24px] w-full max-w-sm p-6 shadow-2xl">
          <div class="text-center">
            <div class="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2">确认删除</h3>
            <p class="text-slate-500 mb-6">确定要删除作业「{{ deletingHomework?.title }}」吗？此操作不可恢复。</p>
            <div class="flex gap-3">
              <button @click="showDeleteModal = false" class="flex-1 border-2 border-slate-200 text-slate-600 py-3 rounded-xl font-medium hover:bg-slate-50 transition-colors">
                取消
              </button>
              <button @click="deleteHomework" :disabled="deleting" class="flex-1 bg-red-500 hover:bg-red-600 disabled:bg-slate-300 text-white py-3 rounded-xl font-medium transition-colors">
                {{ deleting ? '删除中...' : '确认删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 评分脚本内容弹窗 -->
    <Teleport to="body">
      <div v-if="showScriptModal" class="fixed inset-0 bg-black/40 z-[110] flex items-center justify-center p-6" @click.self="showScriptModal = false">
        <div class="bg-white rounded-[24px] w-full max-w-2xl p-6 shadow-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-slate-800">评分脚本内容</h3>
            <button @click="showScriptModal = false" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <pre class="flex-1 overflow-auto bg-slate-800 text-slate-100 rounded-xl p-4 text-sm font-mono leading-relaxed">{{ scriptContent }}</pre>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getHomeworkList, getHomeworkDetail, getHomeworkSubmissions, createHomework, updateHomework, deleteHomework as apiDeleteHomework, gradeHomework, uploadGradingScript, getGradingScript, getGradingScriptContent, toggleGradingAuto, deleteGradingScript, downloadGradingScript } from '../api.js'

const props = defineProps({
  courses: { type: Array, default: () => [] }
})

// 状态
const loading = ref(false)
const homeworkList = ref([])
const filterCourseId = ref('')
const filterClassId = ref('')

// 根据选中的课程过滤班级（用于筛选栏）
const filteredFilterClasses = computed(() => {
  if (!filterCourseId.value) return []
  const course = props.courses.find(c => c.id === filterCourseId.value)
  if (!course || !course.classes) return []
  const classIds = course.classes.map(cls => cls.id)
  // 需要获取所有班级列表，这里用 courses 里的 classes
  return course.classes
})

// 课程变更时清空班级选择
function onFilterCourseChange() {
  filterClassId.value = ''
  loadHomework()
}

// 创建/编辑弹窗
const showCreateModal = ref(false)
const editingHomework = ref(null)
const submitting = ref(false)
const formData = ref({
  title: '',
  course_id: '',
  class_id: '',
  content: '',
  deadline: '',
  total_score: 100
})

// 详情弹窗
const showDetailModal = ref(false)
const currentHomework = ref(null)
const submissions = ref([])
const totalStudents = ref(0)
const loadingSubmissions = ref(false)

// 评分弹窗
const showGradeModal = ref(false)
const gradingSubmission = ref(null)
const gradingSubmitting = ref(false)
const gradeData = ref({ score: '', feedback: '' })

// 删除弹窗
const showDeleteModal = ref(false)
const deletingHomework = ref(null)
const deleting = ref(false)

// 评分脚本相关
const gradingScript = ref(null)
const gradingAutoEnabled = ref(false)
const scriptUploading = ref(false)
const showScriptModal = ref(false)
const scriptContent = ref('')
const selectedFiles = ref([])

// 创建作业时的脚本上传
const createScriptFile = ref(null)
const createEnableAutoGrade = ref(false)

// 评分细节展开状态
const expandedSubDetails = ref({})

function toggleSubDetails(subId) {
  expandedSubDetails.value[subId] = !expandedSubDetails.value[subId]
}

// 下载作业附件
function downloadHwAttachment(att) {
  const token = sessionStorage.getItem('tc_token')
  const url = `/api/homework/attachments/${att.id}/download?token=${token}`
  const a = document.createElement('a')
  a.href = url
  a.download = att.file_name
  a.click()
}

// 下载学生提交附件
function downloadSubmissionAttachment(att) {
  const token = sessionStorage.getItem('tc_token')
  const url = `/api/submissions/attachments/${att.id}/download?token=${token}`
  const a = document.createElement('a')
  a.href = url
  a.download = att.file_name
  a.click()
}

// 文件处理
function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  selectedFiles.value = [...selectedFiles.value, ...files]
}

function removeFile(idx) {
  selectedFiles.value.splice(idx, 1)
}

// 创建作业时的脚本上传
function handleCreateScriptUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!file.name.endsWith('.py')) {
    alert('仅支持 .py 文件')
    return
  }
  createScriptFile.value = file
}

// 计算属性
const filteredHomeworkList = computed(() => {
  if (!filterCourseId.value) return homeworkList.value
  return homeworkList.value.filter(hw => hw.course_id === filterCourseId.value)
})

const selectedCourseClasses = computed(() => {
  if (!formData.value.course_id) return []
  const course = props.courses.find(c => c.id === formData.value.course_id)
  return course?.classes || []
})

// 方法
async function loadHomework() {
  loading.value = true
  try {
    const res = await getHomeworkList({
      courseId: filterCourseId.value || null,
      classId: filterClassId.value || null
    })
    if (res.success) {
      homeworkList.value = res.data || []
    }
  } catch (e) {
    console.error('加载作业失败', e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '未设置'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function closeCreateModal() {
  showCreateModal.value = false
  editingHomework.value = null
  formData.value = { title: '', course_id: '', class_id: '', content: '', deadline: '', total_score: 100 }
  selectedFiles.value = []
  createScriptFile.value = null
  createEnableAutoGrade.value = false
}

function editHomework(hw) {
  editingHomework.value = hw
  formData.value = {
    title: hw.title,
    course_id: hw.course_id,
    class_id: hw.class_id || '',
    content: hw.content || '',
    deadline: hw.deadline ? new Date(hw.deadline).toISOString().slice(0, 16) : '',
    total_score: hw.total_score || 100
  }
  showCreateModal.value = true
}

async function submitHomework() {
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('title', formData.value.title)
    fd.append('course_id', formData.value.course_id)
    if (formData.value.class_id) fd.append('class_id', formData.value.class_id)
    if (formData.value.content) fd.append('content', formData.value.content)
    if (formData.value.deadline) fd.append('deadline', formData.value.deadline)
    fd.append('total_score', formData.value.total_score)
    
    // 添加附件
    for (const file of selectedFiles.value) {
      fd.append('files', file)
    }

    let res
    if (editingHomework.value) {
      res = await updateHomework(editingHomework.value.id, fd)
    } else {
      res = await createHomework(fd)
    }
    
    if (res.success) {
      const hwId = editingHomework.value ? editingHomework.value.id : res.data?.id
      
      // 如果创建时上传了评分脚本，上传脚本
      if (!editingHomework.value && createScriptFile.value && hwId) {
        const scriptFd = new FormData()
        scriptFd.append('script', createScriptFile.value)
        scriptFd.append('enable_auto', createEnableAutoGrade.value ? 'true' : 'false')
        scriptFd.append('regrade_all', 'false')
        await uploadGradingScript(hwId, scriptFd)
      }
      
      closeCreateModal()
      selectedFiles.value = []
      createScriptFile.value = null
      createEnableAutoGrade.value = false
      loadHomework()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e) {
    console.error('提交作业失败', e)
    alert('提交失败')
  } finally {
    submitting.value = false
  }
}

async function viewHomework(hw) {
  currentHomework.value = hw
  showDetailModal.value = true
  loadingSubmissions.value = true
  submissions.value = []
  totalStudents.value = 0
  gradingScript.value = null
  gradingAutoEnabled.value = false
  
  try {
    // 加载提交列表
    const res = await getHomeworkSubmissions(hw.id)
    if (res.success) {
      submissions.value = res.data?.submissions || []
      totalStudents.value = res.data?.total_students || 0
      // 附加作业详情中的附件
      if (res.data && res.data.attachments) {
        currentHomework.value.attachments = res.data.attachments
      }
    }
    
    // 加载评分脚本信息
    try {
      const scriptRes = await getGradingScript(hw.id)
      if (scriptRes.success && scriptRes.data) {
        gradingScript.value = scriptRes.data
        gradingAutoEnabled.value = !!scriptRes.data.auto_grade_enabled
      }
    } catch (e) {
      console.log('该作业暂无评分脚本')
    }
  } catch (e) {
    console.error('加载提交列表失败', e)
  } finally {
    loadingSubmissions.value = false
  }
}

function openGradeModal(sub) {
  gradingSubmission.value = sub
  // 优先使用手动评分分数，没有则使用自动评分分数
  gradeData.value = {
    score: sub.score !== null ? sub.score : (sub.auto_score !== null ? sub.auto_score : ''),
    feedback: sub.feedback || ''
  }
  showGradeModal.value = true
}

async function submitGrade() {
  gradingSubmitting.value = true
  try {
    const res = await gradeHomework(currentHomework.value.id, gradingSubmission.value.student_id, {
      score: gradeData.value.score,
      feedback: gradeData.value.feedback
    })
    
    if (res.success) {
      showGradeModal.value = false
      // 更新本地数据
      const idx = submissions.value.findIndex(s => s.id === gradingSubmission.value.id)
      if (idx !== -1) {
        submissions.value[idx] = {
          ...submissions.value[idx],
          score: gradeData.value.score,
          feedback: gradeData.value.feedback
        }
      }
    } else {
      alert(res.message || '评分失败')
    }
  } catch (e) {
    console.error('评分失败', e)
    alert('评分失败')
  } finally {
    gradingSubmitting.value = false
  }
}

function confirmDelete(hw) {
  deletingHomework.value = hw
  showDeleteModal.value = true
}

async function deleteHomework() {
  deleting.value = true
  try {
    const res = await apiDeleteHomework(deletingHomework.value.id)
    if (res.success) {
      showDeleteModal.value = false
      loadHomework()
    } else {
      alert(res.message || '删除失败')
    }
  } catch (e) {
    console.error('删除失败', e)
    alert('删除失败')
  } finally {
    deleting.value = false
  }
}

// 评分脚本相关方法
async function handleScriptUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  
  if (!file.name.endsWith('.py')) {
    alert('仅支持 .py 文件')
    return
  }
  
  scriptUploading.value = true
  try {
    const fd = new FormData()
    fd.append('script', file)
    fd.append('enable_auto', 'false')
    fd.append('regrade_all', 'false')
    
    const res = await uploadGradingScript(currentHomework.value.id, fd)
    if (res.success) {
      // 刷新评分脚本信息
      const scriptRes = await getGradingScript(currentHomework.value.id)
      if (scriptRes.success && scriptRes.data) {
        gradingScript.value = scriptRes.data
        gradingAutoEnabled.value = !!scriptRes.data.auto_grade_enabled
      }
      alert('评分脚本上传成功')
    } else {
      alert(res.message || '上传失败')
    }
  } catch (e) {
    console.error('上传评分脚本失败', e)
    alert('上传失败')
  } finally {
    scriptUploading.value = false
    e.target.value = ''
  }
}

async function viewScriptContent() {
  try {
    const res = await getGradingScriptContent(currentHomework.value.id)
    if (res.success && res.data) {
      scriptContent.value = res.data.content || ''
      showScriptModal.value = true
    } else {
      alert(res.message || '获取脚本内容失败')
    }
  } catch (e) {
    console.error('获取脚本内容失败', e)
    alert('获取脚本内容失败')
  }
}

async function toggleAutoGrade() {
  try {
    const res = await toggleGradingAuto(currentHomework.value.id, gradingAutoEnabled.value)
    if (res.success) {
      gradingAutoEnabled.value = res.data?.enabled ?? gradingAutoEnabled.value
    } else {
      alert(res.message || '切换失败')
      gradingAutoEnabled.value = !gradingAutoEnabled.value  // 回滚
    }
  } catch (e) {
    console.error('切换自动评分失败', e)
    gradingAutoEnabled.value = !gradingAutoEnabled.value  // 回滚
  }
}

async function regradeAll() {
  if (!confirm('确定要对所有未评分提交重新评分吗？这将使用现有脚本重新评分所有提交。')) return
  
  scriptUploading.value = true
  try {
    // 获取现有脚本内容并重新上传，触发重新评分
    const contentRes = await getGradingScriptContent(currentHomework.value.id)
    if (!contentRes.success || !contentRes.data) {
      alert('无法获取现有脚本')
      return
    }
    
    const fd = new FormData()
    fd.append('script', new Blob([contentRes.data.content], { type: 'text/plain' }), contentRes.data.script_name || 'grading.py')
    fd.append('enable_auto', 'true')
    fd.append('regrade_all', 'true')
    
    const res = await uploadGradingScript(currentHomework.value.id, fd)
    if (res.success) {
      alert('已触发重新评分，请稍后刷新查看结果')
    } else {
      alert(res.message || '重新评分失败')
    }
  } catch (e) {
    console.error('重新评分失败', e)
    alert('重新评分失败')
  } finally {
    scriptUploading.value = false
  }
}

function handleDownloadScript() {
  if (currentHomework.value?.id) {
    downloadGradingScript(currentHomework.value.id)
  }
}

async function confirmDeleteScript() {
  if (!confirm('确定要删除评分脚本吗？')) return
  
  try {
    const res = await deleteGradingScript(currentHomework.value.id)
    if (res.success) {
      gradingScript.value = null
      gradingAutoEnabled.value = false
      alert('评分脚本已删除')
    } else {
      alert(res.message || '删除失败')
    }
  } catch (e) {
    console.error('删除评分脚本失败', e)
    alert('删除失败')
  }
}

onMounted(() => {
  loadHomework()
})
</script>
