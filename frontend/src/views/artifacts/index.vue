<template>
  <div class="artifacts-page">
    <div class="page-header">
      <div class="page-title">
        <h2>专家经验看护</h2>
        <p>管理 Skill、MCP、优秀实践等产出物</p>
      </div>
      <div class="page-action">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
        <el-button type="success" @click="showImportDialog">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="filters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="类别">
            <el-select v-model="queryForm.category" placeholder="请选择" clearable style="width: 140px">
              <el-option label="Skill" value="skill" />
              <el-option label="MCP" value="mcp" />
              <el-option label="优秀实践" value="bestpractice" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="queryForm.department" placeholder="请选择" clearable style="width: 160px">
              <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.name" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetQuery">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="filteredArtifacts" style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="category" label="类别" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" effect="light">{{ getCategoryName(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publisherName" label="发布人" width="100" />
        <el-table-column prop="publisherDept" label="发布人部门" width="120" />
        <el-table-column prop="link" label="链接" width="80">
          <template #default="{ row }">
            <el-button type="primary" link :href="row.link" target="_blank">查看</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="发布时间" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="editRow(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="addDialogVisible" :title="isEdit ? '编辑产出' : '新增产出'" width="600px" class="form-dialog">
      <el-form :model="form" label-position="top">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="名称" required>
              <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类别" required>
              <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
                <el-option label="Skill" value="skill" />
                <el-option label="MCP" value="mcp" />
                <el-option label="优秀实践" value="bestpractice" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="form.link" placeholder="请输入链接" />
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="发布人" required>
              <el-input v-model="form.publisher" placeholder="请输入发布人工号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布人部门">
              <el-select v-model="form.publisherDept" placeholder="请选择" style="width: 100%">
                <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.name" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="importDialogVisible" title="批量导入" width="550px" class="import-dialog">
      <div class="import-tip">
        <el-icon color="#6366f1"><InfoFilled /></el-icon>
        <div>
          <p style="font-weight: 500; color: #1f2937; margin: 0 0 8px 0">请上传Excel文件，支持以下字段：</p>
          <ul style="margin: 0; padding-left: 20px; color: #6b7280;">
            <li>名称(Name)</li>
            <li>描述(Description)</li>
            <li>链接(Link)</li>
            <li>类别(Category)</li>
            <li>发布人工号(Publisher)</li>
            <li>发布人部门(Department)</li>
          </ul>
        </div>
      </div>
      <el-upload
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          拖拽文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="upload-tip">支持 .xlsx 格式文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">确定导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'
import type { Artifact, ArtifactCategory } from '@/types'

const mockDataStore = useMockDataStore()

const queryForm = reactive({
  category: 'skill' as ArtifactCategory | '',
  department: ''
})

const addDialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEdit = ref(false)
const currentEditId = ref<number | null>(null)

const form = reactive({
  name: '',
  description: '',
  link: '',
  category: 'skill' as ArtifactCategory,
  publisher: '',
  publisherDept: ''
})

const departments = computed(() => mockDataStore.departments)

const filteredArtifacts = computed(() => {
  let list = mockDataStore.artifacts
  if (queryForm.category) {
    list = list.filter(a => a.category === queryForm.category)
  }
  if (queryForm.department) {
    list = list.filter(a => a.publisherDept === queryForm.department)
  }
  return list
})

const getCategoryType = (category: ArtifactCategory) => {
  const map: Record<ArtifactCategory, 'success' | 'warning' | 'danger'> = {
    skill: 'warning',
    mcp: 'warning',
    bestpractice: 'success'
  }
  return map[category]
}

const getCategoryName = (category: ArtifactCategory) => {
  const map: Record<ArtifactCategory, string> = {
    skill: 'Skill',
    mcp: 'MCP',
    bestpractice: '优秀实践'
  }
  return map[category]
}

const loadData = () => {}
const resetQuery = () => {
  queryForm.category = ''
  queryForm.department = ''
}

const showAddDialog = () => {
  isEdit.value = false
  currentEditId.value = null
  Object.keys(form).forEach(key => {
    (form as any)[key] = ''
  })
  form.category = 'skill'
  addDialogVisible.value = true
}

const editRow = (row: Artifact) => {
  isEdit.value = true
  currentEditId.value = row.id
  form.name = row.name
  form.description = row.description
  form.link = row.link
  form.category = row.category
  form.publisher = row.publisher
  form.publisherDept = row.publisherDept
  addDialogVisible.value = true
}

const deleteRow = async (row: Artifact) => {
  await ElMessageBox.confirm('确定要删除该产出吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  
  const idx = mockDataStore.artifacts.findIndex(a => a.id === row.id)
  if (idx > -1) {
    mockDataStore.artifacts.splice(idx, 1)
    ElMessage.success('删除成功')
  }
}

const submitForm = () => {
  if (!form.name || !form.category || !form.publisher) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  if (isEdit.value && currentEditId.value) {
    const idx = mockDataStore.artifacts.findIndex(a => a.id === currentEditId.value)
    if (idx > -1) {
      mockDataStore.artifacts[idx] = {
        ...mockDataStore.artifacts[idx],
        ...form
      }
    }
    ElMessage.success('编辑成功')
  } else {
    mockDataStore.artifacts.unshift({
      id: Date.now(),
      ...form,
      publisherName: form.publisher,
      createdAt: new Date().toISOString().slice(0, 10)
    })
    ElMessage.success('新增成功')
  }
  
  addDialogVisible.value = false
}

const showImportDialog = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  console.log('file:', file)
}

const confirmImport = () => {
  ElMessage.success('导入成功')
  importDialogVisible.value = false
}
</script>

<style scoped>
.artifacts-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.page-action {
  display: flex;
  gap: 12px;
}

.table-card {
  border: none;
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-table) {
  --el-table-border-color: #f3f4f6;
  --el-table-header-bg-color: #fafbfc;
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
  color: #374151;
}

:deep(.el-table td.el-table__cell) {
  font-size: 13px;
}

.form-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f3f4f6;
  padding: 16px 20px;
}

.form-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.import-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f3f4f6;
  padding: 16px 20px;
}

.import-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.import-tip {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 10px;
  margin-bottom: 20px;
}

.import-tip ul li {
  margin: 4px 0;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 40px 20px;
  border-radius: 12px;
  border: 2px dashed #d1d5db;
  background: #fafbfc;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #6366f1;
}

.upload-icon {
  font-size: 48px;
  color: #6366f1;
  margin-bottom: 12px;
}

.upload-text {
  color: #6b7280;
}

.upload-text em {
  color: #6366f1;
  font-style: normal;
}

.upload-tip {
  color: #9ca3af;
  font-size: 13px;
  margin-top: 8px;
}
</style>
