<template>
  <div class="system-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>字典配置</span>
          <el-button type="primary" @click="showAddDialog">新增</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="工具类型" name="tool">
          <el-table :data="toolDicts" style="width: 100%">
            <el-table-column prop="label" label="名称" />
            <el-table-column prop="value" label="值" />
            <el-table-column prop="sort" label="排序" width="80" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="模型" name="model">
          <el-table :data="modelDicts" style="width: 100%">
            <el-table-column prop="label" label="名称" />
            <el-table-column prop="value" label="值" />
            <el-table-column prop="sort" label="排序" width="80" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="产出类别" name="category">
          <el-table :data="categoryDicts" style="width: 100%">
            <el-table-column prop="label" label="名称" />
            <el-table-column prop="value" label="值" />
            <el-table-column prop="sort" label="排序" width="80" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <el-dialog v-model="dialogVisible" title="字典配置" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="请选择">
            <el-option label="工具类型" value="tool" />
            <el-option label="模型" value="model" />
            <el-option label="产出类别" value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.label" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="值">
          <el-input v-model="form.value" placeholder="请输入值" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('tool')
const dialogVisible = ref(false)

const form = reactive({
  type: 'tool',
  label: '',
  value: '',
  sort: 0
})

const toolDicts = ref([
  { id: 1, type: 'tool', label: 'Cursor', value: 'Cursor', sort: 1 },
  { id: 2, type: 'tool', label: 'Windsurf', value: 'Windsurf', sort: 2 },
  { id: 3, type: 'tool', label: 'Copilot', value: 'Copilot', sort: 3 },
  { id: 4, type: 'tool', label: 'Claude Code', value: 'Claude Code', sort: 4 }
])

const modelDicts = ref([
  { id: 1, type: 'model', label: 'GPT-4', value: 'GPT-4', sort: 1 },
  { id: 2, type: 'model', label: 'GPT-4o', value: 'GPT-4o', sort: 2 },
  { id: 3, type: 'model', label: 'Claude-3', value: 'Claude-3', sort: 3 },
  { id: 4, type: 'model', label: 'Claude-3.5', value: 'Claude-3.5', sort: 4 }
])

const categoryDicts = ref([
  { id: 1, type: 'category', label: 'Skill', value: 'skill', sort: 1 },
  { id: 2, type: 'category', label: 'MCP', value: 'mcp', sort: 2 },
  { id: 3, type: 'category', label: '优秀实践', value: 'bestpractice', sort: 3 }
])

const showAddDialog = () => {
  form.type = activeTab.value
  form.label = ''
  form.value = ''
  form.sort = 0
  dialogVisible.value = true
}

const deleteRow = (row: any) => {
  ElMessage.success('删除成功')
}

const submitForm = () => {
  if (!form.label || !form.value) {
    ElMessage.warning('请填写完整信息')
    return
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
}
</script>

<style scoped>
.system-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}
</style>
