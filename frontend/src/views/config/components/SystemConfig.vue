<template>
  <div class="system-config">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索配置项名称、Key 或分类"
        clearable
        style="max-width: 360px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button :loading="configStore.loading" @click="configStore.fetchItems()">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table v-loading="configStore.loading" :data="filteredItems" stripe>
        <el-table-column prop="label" label="配置名称" min-width="160" />
        <el-table-column prop="key" label="配置 Key" min-width="200">
          <template #default="{ row }">
            <code class="config-key">{{ row.key }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="当前值" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="编辑配置" width="520px" destroy-on-close>
      <el-form v-if="editingItem" label-width="90px">
        <el-form-item label="配置名称">
          <el-input :model-value="editingItem.label" disabled />
        </el-form-item>
        <el-form-item label="配置 Key">
          <el-input :model-value="editingItem.key" disabled />
        </el-form-item>
        <el-form-item label="配置值">
          <el-input v-model="editForm.value" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="configStore.loading" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useConfigStore } from '@/stores/config'
import type { ConfigItem } from '@/types'

const configStore = useConfigStore()
const keyword = ref('')
const dialogVisible = ref(false)
const editingItem = ref<ConfigItem | null>(null)
const editForm = reactive({ value: '', description: '' })

const filteredItems = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return configStore.items
  return configStore.items.filter(
    (item) =>
      item.label.toLowerCase().includes(kw) ||
      item.key.toLowerCase().includes(kw) ||
      item.category.toLowerCase().includes(kw)
  )
})

onMounted(() => {
  configStore.fetchItems()
})

const openEdit = (item: ConfigItem) => {
  editingItem.value = item
  editForm.value = item.value
  editForm.description = item.description
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!editingItem.value) return
  const ok = await configStore.updateItem(editingItem.value.id, {
    value: editForm.value,
    description: editForm.description
  })
  if (ok) {
    ElMessage.success('配置已保存（Mock 数据，待接入 API）')
    dialogVisible.value = false
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.config-key {
  font-size: 12px;
  color: #6366f1;
  background: #eef2ff;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
